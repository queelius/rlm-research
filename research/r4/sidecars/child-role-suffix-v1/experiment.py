"""Frozen exposed task/seed grid and narrow private collector adaptation."""
import argparse
import ast
import asyncio
import copy
import hashlib
import os
import sys
from pathlib import Path
from types import SimpleNamespace
import runtime as r

ROOT,SIDE=r.ROOT,r.SIDE
BROAD=SIDE/'root-broad-curriculum-v1'
DESIGN=ROOT.parents[1]/'ideas/2026-09-09-child-role-suffix-design.md'
DECISION=ROOT.parents[1]/'operations/2026-09-09-continuous-allocation/CHILD_ROLE_SUFFIX_IMPLEMENTATION_DECISION.md'
NAMES=('training-016-00:human_being','training-032-00:numeric_value',
       'training-064-00:entity','validation-064-02:entity')
SEEDS=(893350289,62794825)
sys.path.insert(0,str(SIDE/'root-only-credit-v1'))
capture=r.checked_import('suffix_frozen_capture',SIDE/'root-only-credit-v1/capture.py',r.PINS[SIDE/'root-only-credit-v1/capture.py'])
sys.path.insert(0,str(ROOT))
q=capture.q


def make_tasks():
    path=BROAD/'campaign_native.py'
    if r.file_hash(path)!='a04913d35a18404516338d2afbf26211ce81e683c08b7f3656b573b7fb20118b':
        raise ValueError('original task builder changed')
    node=next(n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='make_tasks')
    descriptor=r.read(capture.ENDPOINT)
    scope={'c':SimpleNamespace(ROOT=BROAD,Path=Path,read=r.read,
        pilot_recipe=lambda:{'base_model':descriptor['base_model']['path']})}
    exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),scope)
    tasks=scope['make_tasks']()
    return {name:tasks[name] for name in NAMES}


def with_prompt(task,arm):
    if arm not in r.ARMS: raise ValueError('unknown role suffix arm')
    return capture.role.with_prompt(task,'sft_child')


def build_plan(tasks):
    plan=[]
    for repeat,seed in enumerate(SEEDS):
        for index,name in enumerate(NAMES):
            task=tasks[name]
            identity={'study':ROOT.name,'task_name':name,'source_id':task.data.source_id,
                'context_window_id':task.data.context_window_id,
                'context_sha256':hashlib.sha256(task.data.context.encode()).hexdigest(),
                'analysis_split':'exposed_failure_enriched_diagnostic' if index!=1 else 'exposed_moderate_comparator',
                'split':'diagnostic_no_training','repeat':repeat,'seed':seed,'temperature':.5,'client_path':'train'}
            pair=r.digest(identity)
            arms=r.ARMS if (index+repeat)%2==0 else tuple(reversed(r.ARMS))
            for order,arm in enumerate(arms):
                row={**identity,'arm':arm,'pair_id':pair,'pair_order':order,'dispatch_order':len(plan),
                    'group_id':r.digest([ROOT.name,name]),'task_hash':with_prompt(task,arm).hash}
                plan.append({**row,'id':r.digest(row)})
    return plan


def binding():
    value=capture.binding()
    if value['models'][value['role_map']['root']]['adapter_sha256']!='857a7ce6907c759a8c1b478eb53029d3b700b81c3094d8edb3394e52def9fcb6':
        raise ValueError('original root changed')
    if value['models'][value['fixed_child']]['adapter_sha256']!='c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3':
        raise ValueError('fixed child changed')
    return value


def verify():
    value=r.read(ROOT/'SPEC.json')
    for path,sha in value['source_file_sha256'].items():
        if r.file_hash(path)!=sha: raise ValueError('sealed source/input changed: '+path)
    if value['plan']!=build_plan(make_tasks()) or value['plan_sha256']!=r.digest(value['plan']):
        raise ValueError('coordinates changed')
    if value['role_binding']!=binding(): raise ValueError('weight binding changed')
    return value


def bind(endpoint_path,binding_path,destination,cap):
    value=copy.deepcopy(verify())
    descriptor,bound=r.read(endpoint_path),r.read(binding_path)
    if bound!=value['role_binding']: raise ValueError('actual binding differs')
    root=bound['models'][bound['role_map']['root']]
    if descriptor['adapter']!={'path':root['path'],'model_sha256':root['adapter_sha256'],'config_sha256':root['config_sha256']}:
        raise ValueError('actual descriptor differs')
    if descriptor['base_model']!=value['source_endpoint_descriptor']['base_model'] or descriptor['model_alias']!=bound['role_map']['root']:
        raise ValueError('actual base/root differs')
    value['endpoint']={**value['endpoint'],'url':f"http://{descriptor['host']}:{descriptor['port']}/v1",'api_key_env':descriptor['api_key_env']}
    value.update(source_endpoint_descriptor=descriptor,parent_spec_sha256=r.file_hash(ROOT/'SPEC.json'),
        binding_path=str(binding_path),endpoint_descriptor_path=str(endpoint_path),wall_time_cap_seconds=min(1500,cap),
        serving_evidence=capture.recursive.serving_evidence(Path(endpoint_path).parent/'inference.log'))
    value['source_file_sha256'].update({str(p):r.file_hash(p) for p in (ROOT/'SPEC.json',ROOT/'READY.json',Path(endpoint_path),Path(binding_path))})
    r.write_once(destination,value)
    return value


def verify_bound(path):
    value,parent=r.read(path),verify()
    for source,sha in value['source_file_sha256'].items():
        if r.file_hash(source)!=sha: raise ValueError('bound source differs: '+source)
    for key in ('plan','plan_sha256','environment','tasks','role_binding','image_id','max_concurrent_pairs','request_template'):
        if value[key]!=parent[key]: raise ValueError('bound invariant differs: '+key)
    if value['parent_spec_sha256']!=r.file_hash(ROOT/'SPEC.json') or not 0<value['wall_time_cap_seconds']<=1500:
        raise ValueError('bound deadline/parent differs')
    descriptor=r.read(value['endpoint_descriptor_path'])
    if value['source_endpoint_descriptor']!=descriptor or value['role_binding']!=r.read(value['binding_path']):
        raise ValueError('bound endpoint/weights differs')
    expected={**parent['endpoint'],'url':f"http://{descriptor['host']}:{descriptor['port']}/v1",'api_key_env':descriptor['api_key_env']}
    if value['endpoint']!=expected: raise ValueError('bound endpoint address differs')
    capture.recursive.validate_serving_evidence(value['serving_evidence'])
    return value


async def collect(spec_path,output):
    spec=verify_bound(spec_path)
    output=Path(output)
    audit=output.with_name(output.name+'-routing')
    if output.exists() or audit.exists(): raise ValueError('new capture paths required')
    guard=r.DispatchBudget(audit/'dispatch-budget')
    hooks=r.native_hooks(guard)
    collector=r.collector(capture.base)
    collector.with_prompt=with_prompt
    collector.crossover_metrics=capture.native.episode_metrics
    collector.summarize=lambda records,plan:capture.native.summarize(records,len(plan))
    collector.STUDY=ROOT.name
    saved=(q.make_context,q.request_metadata)
    q.make_context,q.request_metadata=capture.make_context,capture.native.request_metadata
    os.environ['PATH']=str(q.ROOTLESS/'bin')+os.pathsep+os.environ.get('PATH','')
    os.environ.setdefault('VERIFIERS_CACHE_DIR','/project/alex_phd/cache/verifiers-prime')
    r.write_once(audit/'BINDING.json',spec['role_binding'])
    try:
        with hooks.installed_hooks(spec['role_binding'],audit):
            work=asyncio.create_task(collector.run(argparse.Namespace(endpoint_url=None,output_dir=output,resume=False),copy.deepcopy(spec),make_tasks()))
            stopped=asyncio.create_task(guard.exhausted.wait())
            done,_=await asyncio.wait((work,stopped),return_when=asyncio.FIRST_COMPLETED)
            if stopped in done and not work.done(): work.cancel()
            stopped.cancel()
            await asyncio.gather(stopped,return_exceptions=True)
            try: result=await work
            except asyncio.CancelledError: result=3
            if guard.exhausted.is_set(): result=3
    finally:
        q.make_context,q.request_metadata=saved
        r.write_once(audit/'DISPATCH_STATUS.json',{'sent':guard.sent,'prevented':guard.prevented,
            'cap':guard.limit,'cap_exhausted':guard.exhausted.is_set(),
            'native_executed_source_sha256':hooks.executed_source_sha256,
            'collector_executed_source_sha256':collector.executed_source_sha256})
    return result
