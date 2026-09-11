"""Freeze inputs/source and publish READY last after the actual native hook proof."""
import ast
import json
import os
import subprocess
import time
from pathlib import Path
import experiment as e

def seeds_in(value):
    if isinstance(value,dict):
        return {v for k,v in value.items() if k in ('seed','seed_master','seed_audit_master') and type(v) is int}|set().union(*(seeds_in(v) for v in value.values()))
    if isinstance(value,list): return set().union(*(seeds_in(v) for v in value))
    return set()

def prepare():
    c=e.c;tasks=e.make_tasks();plan=e.build_plan(tasks);prior=c.read(e.UPTAKE/'SPEC.json')
    proof=c.read(e.ROOT/'qualification-attempt-002/RESULT.json')
    if proof['provider_calls']!=8 or proof['actual_model_calls']!=0 or not all(r['wire_equal_except_schema'] for r in proof['comparisons']): raise ValueError('actual-hook proof missing')
    seed_files=sorted(set(e.ROOT.parent.glob('*/SPEC*.json'))|set(e.ROOT.parent.glob('*/inputs/PLANS.json')))
    seed_files=[p for p in seed_files if e.ROOT not in p.parents];existing=set()
    for p in seed_files: existing.update(seeds_in(c.read(p)))
    seeds={r['seed'] for r in plan}
    if seeds&existing: raise ValueError('seed collision')
    c.write_once(e.ROOT/'inputs/SEED_AUDIT.json',{'seeds':sorted(seeds),'master':e.SEED_MASTER,'order_seed':e.ORDER_SEED,'collisions':[],
        'scope':'Top-level sidecar SPEC*.json and inputs/PLANS.json, not outcomes or a universal registry','sources':{str(p):c.file_hash(p) for p in seed_files}})
    catalogs={str(t.data.context_window_id):e.catalog_for(t) for t in tasks.values()}
    identities=[];requests=[];policy=prior['policies']['step8'];binding=e.binding_for(policy)
    for name,task in tasks.items():
        arms={}
        for arm in e.ARMS:
            t=e.with_prompt(task,arm);snippet=e.example_code(t.data.prompt);compile(snippet,name+'/'+arm,'exec',flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
            arms[arm]={'prompt':t.data.prompt,'prompt_sha256':e.hashlib.sha256(t.data.prompt.encode()).hexdigest(),'task_hash':t.hash,'offered_example':snippet}
        if arms['restored_raw']!=arms['typed']: raise ValueError('R/T prompt/package drift')
        identities.append({'name':name,'context_sha256':e.hashlib.sha256(task.data.context.encode()).hexdigest(),'context_window_id':task.data.context_window_id,
            'gold_sha256':c.digest(task.data.answer),'catalog_sha256':c.digest(catalogs[str(task.data.context_window_id)]),'arms':arms})
    for row in plan:
        ctx=e.make_context(e.old.planned_endpoint(binding),row)
        requests.append({'coordinate':row,'model':ctx.model,'client':ctx.client.model_dump(mode='json'),
            'sampling':ctx.sampling.model_dump(mode='json'),'public_root_prompt':e.with_prompt(tasks[row['task_name']],row['arm']).data.prompt,
            'context_sha256':row['context_sha256'],'runtime_gold_present':False,'adaptive_children_not_predeclared':True})
    for name,value in [('PLAN',plan),('TASKS',identities),('REQUESTS',requests),('PUBLIC_CATALOGS',catalogs),('BINDING',binding)]: c.write_once(e.ROOT/'inputs'/f'{name}.json',value)
    command=[str(c.NATIVE_PYTHON),'-m','unittest','test_contract','test_study','-v'];started=time.time()
    result=subprocess.run(command,cwd=e.ROOT,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True,timeout=120)
    c.write_once(e.ROOT/'FOCUSED_TESTS.json',{'argv':command,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'seconds':time.time()-started})
    if result.returncode: raise ValueError('focused test failure, no READY')
    sources=dict(prior['source_file_sha256'])
    image=c.read(e.IMAGE_READY);sources.update(image['source_and_artifact_sha256'])
    paths=list(e.ROOT.glob('*.py'))+list(e.ROOT.glob('*.md'))+list((e.ROOT/'inputs').glob('*.json'))
    paths += [e.UPTAKE/'SPEC.json',e.UPTAKE/'READY.json',e.UPTAKE/'experiment.py',e.DECISION,e.DESIGN,e.IMAGE_READY,e.ROOT/'FOCUSED_TESTS.json']
    paths += list((e.ROOT/'qualification-attempt-001').rglob('*.json'))+list((e.ROOT/'qualification-attempt-002').rglob('*.json'))
    paths += [e.ROOT/'qualification-attempt-001/QUALIFY_SOURCE.py']
    # Exact installed native grammar transport, beyond inherited component chat grammar pins.
    v=Path('/project/alex_phd/envs/prime-rl-5990b1b/lib/python3.12/site-packages/vllm')
    paths += [v/p for p in ('sampling_params.py','entrypoints/scale_out/token_in_token_out/protocol.py','entrypoints/scale_out/token_in_token_out/serving.py','entrypoints/scale_out/token_in_token_out/api_router.py','v1/structured_output/backend_xgrammar.py','v1/structured_output/__init__.py','config/structured_outputs.py')]
    sources.update({str(p):c.file_hash(p) for p in paths})
    spec={'schema':e.ROOT.name,'source_file_sha256':sources,'plan':plan,'plan_sha256':c.digest(plan),'tasks':identities,'policies':{'step8':policy},
        'bindings':{'step8':binding},'environment':e.environment(),'image_id':'sha256:'+e.IMAGE,'image_cpu_ready_sha256':c.file_hash(e.IMAGE_READY),
        'sampling':prior['sampling'],'renderer':prior['renderer'],'base_model':prior['base_model'],'base_manifest_sha256':prior['base_manifest_sha256'],
        'max_concurrent_pairs':4,'wall_time_cap_seconds':1800,'collection_cap_seconds':1800,'work_cap_seconds':2280,'owned_cap_seconds':2400,'outer_cap_seconds':2430,
        'exposure':prior['exposure'],'source_provenance':prior['source_provenance'],'inherited_retry_caveat':prior['inherited_retry_caveat'],
        'partial_trace_limitation':prior['partial_trace_limitation'],'scored_episodes':36,'coordinate_triples':12,
        'collector_adapter':{'source_sha256':e.u.COLLECTOR_SHA,'adapted_sha256':e.hashlib.sha256(e.u.receipt.collector_source().encode()).hexdigest(),
            'delta':'exact pair chunk2->3, image constants rebound to approved symmetric private image'},
        'primary':'typed minus restored_raw strict whole-RLM success; ordinary unchanged calibration','qualification':'qualification-attempt-002',
        'no_semantic_validation':True,'no_training':True,'ordered_keys_and_child_tool_suppression':True}
    c.write_once(e.ROOT/'SPEC.json',spec);e.verify()
    argv=[str(c.NATIVE_PYTHON),str(e.ROOT/'driver.py'),'run','--output',str(e.ROOT/'outputs/attempt-001')]
    ready={'schema':e.ROOT.name,'planned':36,'prepared_epoch':time.time(),'spec_sha256':c.file_hash(e.ROOT/'SPEC.json'),'driver_sha256':c.file_hash(e.ROOT/'driver.py'),
        'launch_argv':argv,'launch_command':'PYTHONDONTWRITEBYTECODE=1 '+' '.join(argv),'outer_cap_seconds':2430,'owned_job_cap_seconds':2400,'work_cap_seconds':2280,'collection_cap_seconds':1800,
        'artifact_sha256':{str(p):c.file_hash(p) for p in (e.ROOT/'SPEC.json',e.ROOT/'FOCUSED_TESTS.json',e.ROOT/'qualification-attempt-002/RESULT.json')},
        'model_calls_during_preparation':0,'gpu_calls_during_preparation':0,'successful_fixture_provider_calls':8,'failed_fixture_provider_calls':4,
        'retained_failed_fixture':'qualification-attempt-001: actual R chain passed; local Episode.reward projection attribute absent before T',
        'acceptance':'CPU READY only. Main separately approves and launches.'}
    c.write_once(e.ROOT/'READY.json',ready)
    print(json.dumps({'ready':str(e.ROOT/'READY.json'),'ready_sha256':c.file_hash(e.ROOT/'READY.json'),'planned':36,'gpu_calls':0}),flush=True)

if __name__=='__main__': prepare()
