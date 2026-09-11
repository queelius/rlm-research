"""Outcome-independent CPU preparation; READY is the final publication operation."""
import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
from pathlib import Path
import experiment as e
import runtime as r
import owned


def seed_audit():
    paths=[]
    for pattern in ('**/PLAN.json','**/PLAN-*.json','**/SEEDS.json','**/SPEC.json'):
        paths.extend(r.SIDE.glob(pattern))
    paths=sorted({p for p in paths if not p.is_relative_to(r.ROOT) and p.stat().st_size<2000000
        and not any(x in p.parts for x in ('outputs','training','service'))})
    hits=[]
    def walk(value,path):
        if isinstance(value,dict):
            for key,item in value.items():
                if 'seed' in key.lower() and type(item) is int and item in (*e.SEEDS,981273001): hits.append([str(path),key,item])
                walk(item,path)
        elif isinstance(value,list):
            for item in value: walk(item,path)
    for path in paths: walk(r.read(path),path)
    if hits: raise ValueError('seed collision in named-plan audit: '+str(hits))
    return {'scope':'Named PLAN/PLAN-*/SEEDS/SPEC JSON below2MB, excluding outputs/training/service and this study; not global',
        'seed_master':981273001,'sampling_seeds':list(e.SEEDS),'collisions':hits,
        'source_sha256':{str(p):r.file_hash(p) for p in paths}}


def prepare():
    if r.file_hash(e.DESIGN)!='d1665da58c22172c921944b463af1847983d7f28a7afb5302749b5412d3ac708':
        raise ValueError('approved design changed')
    expected={e.BROAD/'inputs/PUBLIC.json':'2c466164e9aaffe2571c1f83c18b394345213c82610b7fc3068282600b1eee6b',
        e.BROAD/'inputs/HOST_GOLD.json':'384f15ed3ff64d3a9444bfa47a1534132e8f7de8bfcb96a8b4ded621a35b1ff6'}
    for path,sha in expected.items():
        if r.file_hash(path)!=sha: raise ValueError('frozen candidate data changed')
    proof=r.read(r.ROOT/'qualification-attempt-001/RESULT.json')
    if not proof['complete'] or proof['provider_fixture_calls']!=8 or proof['actual_model_calls'] or proof['gpu_calls']:
        raise ValueError('actual native CPU qualification missing')
    for path,sha in proof['source_sha256'].items():
        if r.file_hash(path)!=sha: raise ValueError('qualified runtime source changed')
    tasks,descriptor,binding=e.make_tasks(),r.read(e.capture.ENDPOINT),e.binding()
    plan=e.build_plan(tasks)
    endpoint={'url':f"http://{descriptor['host']}:{descriptor['port']}/v1",'model':descriptor['model_alias'],
        'api_key_env':descriptor['api_key_env'],'renderer_model':descriptor['base_model']['path']}
    spec=e.capture.role.make_spec(endpoint,binding,tasks,plan,r.ROOT.name)
    for task in spec['tasks']:
        task['arms']={arm:{'prompt':e.with_prompt(tasks[task['name']],arm).data.prompt,
            'task_hash':e.with_prompt(tasks[task['name']],arm).hash} for arm in r.ARMS}
    audit=seed_audit()
    r.write_once(r.ROOT/'inputs/SEED_AUDIT.json',audit)
    r.write_once(r.ROOT/'inputs/PLAN.json',plan)
    r.write_once(r.ROOT/'inputs/TASKS.json',[{'name':name,'context':task.data.context,
        'root_prompt':e.with_prompt(task,'control').data.prompt,'context_sha256':hashlib.sha256(task.data.context.encode()).hexdigest(),
        'root_prompt_sha256':hashlib.sha256(e.with_prompt(task,'control').data.prompt.encode()).hexdigest(),
        'source_id':task.data.source_id,'context_window_id':task.data.context_window_id,
        'root_tokens_from_fixture_note':'Physical root inputs are captured per call; qualified root system/user/tools, no host gold included.'}
        for name,task in tasks.items()])
    r.write_once(r.ROOT/'inputs/BINDING.json',binding)
    spec.update(role_binding=binding,source_endpoint_descriptor=descriptor,
        request_template=e.capture.native.request_metadata(endpoint,plan[0]),
        role_policy={'depth0':binding['role_map']['root'],'depth1':binding['fixed_child'],'suffix_depth':1,
            'tools':'unchanged available','child_user':'unchanged','root_prompt':'unchanged'},
        treatment={'suffix':r.SUFFIX,'seam':'nano _start before initial system/user message construction',
            'arm_delivery':'host-only ContextVar around run_slot to owned runtime setup'},
        interpretation='Exposed failure-enriched inference-only role suffix; no training, no general-efficiency claim.',
        wall_time_cap_seconds=1500,inclusive_job_cap_seconds=1800,dispatch_ceiling=2048,
        dispatch_counter_semantics='Allowed final native request-hook entries immediately before transport; not verified server receipt or sampling. Prevented entries separate.',
        inherited_stop_rule='Above50% execution errors after8 attempted episodes; completed malformed outputs not execution errors.',
        cpu_qualification=proof,selection='Three failure-enriched exposed groups plus exposed moderate comparator; no test selection of weights.',
        root_initial_source_sha256=r.digest(spec['tasks']),
        versions={name:importlib.metadata.version(name) for name in ('verifiers','renderers','prime-rl','vllm','torch')},
        python=platform.python_version())
    sources=spec['source_file_sha256']
    sources.update(r.read(r.SIDE/'root-only-credit-v1/SPEC.json')['source_file_sha256'])
    sources.update(r.read(r.SIDE/'leaf-post-sft-suite-v1/MANIFEST.json')['source_sha256'])
    sources.update(r.read(r.SIDE/'root-rlvr-campaign-v1/LIFECYCLE_V2.json')['source_sha256'])
    paths=[e.DESIGN,e.DECISION,owned.SUITE,owned.OBSERVER,e.BROAD/'campaign_native.py',
        e.BROAD/'inputs/PUBLIC.json',e.BROAD/'inputs/HOST_GOLD.json',e.BROAD/'inputs/PROVENANCE.json',
        r.SIDE/'root-curriculum-data-v1/PROVENANCE.json',r.SIDE/'root-curriculum-data-v1/MANIFEST.json',
        r.SIDE/'leaf-post-sft-suite-v1/MANIFEST.json',r.SIDE/'root-rlvr-campaign-v1/LIFECYCLE_V2.json',
        r.ROOT.parents[1]/'ideas/2026-09-09-child-call-amplification.json']
    paths+=list(r.ROOT.glob('*.py'))+list(r.ROOT.glob('*.md'))+list((r.ROOT/'inputs').glob('*.json'))
    sources.update({str(p):r.file_hash(p) for p in paths})
    sources.update(audit['source_sha256'])
    for path,sha in sources.items():
        if r.file_hash(path)!=sha: raise ValueError('source closure differs: '+path)
    r.write_once(r.ROOT/'SPEC.json',spec)
    return spec


def seal():
    spec=e.verify()
    command=[sys.executable,'-m','pytest','-q','-p','no:cacheprovider','test_runtime.py','test_plan.py','test_owned.py','test_results.py']
    test=subprocess.run(command,cwd=r.ROOT,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True)
    evidence={'argv':command,'exit_code':test.returncode,'stdout':test.stdout,'stderr':test.stderr,
        'red_evidence':'Preparation transcript:4 missing-runtime assertions, then missing-plan and missing-owned assertions. Material message-construction test also caught indentation before GREEN.',
        'runtime_qualification_source_unchanged':r.read(r.ROOT/'qualification-attempt-001/RESULT.json')['source_sha256'],
        'gpu_calls':0}
    r.write_once(r.ROOT/'FOCUSED_TESTS.json',evidence)
    if test.returncode: raise ValueError('focused checks failed')
    files=[r.ROOT/'SPEC.json',r.ROOT/'FOCUSED_TESTS.json']+list((r.ROOT/'qualification-attempt-001').rglob('*.json'))
    artifact={str(p):r.file_hash(p) for p in files}
    ready={'schema':'child-role-suffix-ready-v1','status':'CPU_READY_NOT_LAUNCHED','planned':16,
        'spec_sha256':r.file_hash(r.ROOT/'SPEC.json'),'source_sha256':spec['source_file_sha256'],
        'artifact_sha256':artifact,'argv':[sys.executable,str(r.ROOT/'owned.py'),'--output',str(r.ROOT/'outputs/attempt-001')],
        'cwd':str(r.ROOT),'verify_argv':[sys.executable,str(r.ROOT/'owned.py'),'--verify'],
        'analysis_argv':[sys.executable,str(r.ROOT/'driver.py'),'analyze','--output',str(r.ROOT/'outputs/attempt-001')],
        'environment':'Inherit parent actual exclusive CUDA_VISIBLE_DEVICES/MIG UUID, LD_LIBRARY_PATH and credential; no hardcoded CUDA0.',
        'caps':{'inclusive_seconds':1800,'startup_deadline_from_entry_seconds':180,'collection_seconds':1500,
            'cleanup_reserve_seconds':120,'native_dispatch_ceiling':2048,'parent_outer_seconds':1830,'parent_cleanup_grace_seconds':120},
        'provider_dispatch_boundary':spec['dispatch_counter_semantics'],
        'weights':binding_digest(spec),'preparation_gpu_calls':0,'qualified_fixture_calls':8,
        'native_graph_and_physical_prefix_qualification':True,'focused_tests_exit0':True,
        'approval':'Parent acceptance/launch only; no scheduler or automatic successor implemented'}
    # Publication is deliberately the last write; no more source/data edits after this.
    r.write_once(r.ROOT/'READY.json',ready)
    return ready


def binding_digest(spec):
    b=spec['role_binding']
    return {'root':b['models'][b['role_map']['root']]['adapter_sha256'],
        'child':b['models'][b['fixed_child']]['adapter_sha256']}


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=('prepare','seal'))
    args=parser.parse_args()
    value=prepare() if args.command=='prepare' else seal()
    print(json.dumps({'command':args.command,'planned':len(value.get('plan',[])) or value.get('planned'),'gpu_calls':0}))
