"""Freeze prospective96 tasks/requests and publish CPU READY only after qualification."""
import ast
import json
import os
import subprocess
import time
from pathlib import Path
import experiment as e

c=e.c
QUALIFICATION='qualification-attempt-002'


def seeds_in(value):
    result=set()
    if isinstance(value,dict):
        for key,child in value.items():
            if key in ('seed','seed_master','seed_audit_master') and type(child) is int: result.add(child)
            result.update(seeds_in(child))
    elif isinstance(value,list):
        for child in value: result.update(seeds_in(child))
    return result


def prepare():
    tasks=e.make_tasks()
    plan=e.build_plan(tasks)
    prior=c.read(e.PRIOR/'SPEC.json')
    factorial=c.read(e.old.ROOT/'SPEC.json')
    policies=factorial['policies']
    bindings={w:e.binding_for(p) for w,p in policies.items()}
    for binding in bindings.values(): e.native.authenticate_binding(binding)
    seed_files=sorted(set(e.ROOT.parent.glob('*/SPEC*.json'))|set(e.ROOT.parent.glob('*/inputs/PLANS.json')))
    seed_files=[p for p in seed_files if e.ROOT not in p.parents]
    old_seeds=set()
    for path in seed_files: old_seeds.update(seeds_in(c.read(path)))
    seeds={row['seed'] for row in plan}
    if old_seeds & seeds: raise ValueError('candidate seed collision: '+str(sorted(old_seeds&seeds)))
    seed_audit={'seed_master':e.SEED_MASTER,'distinct_rollout_seeds':sorted(seeds),'previous_seed_count':len(old_seeds),'collisions':[],
        'source_sha256':{str(p):c.file_hash(p) for p in seed_files},
        'scope':'Bounded top-level sidecar SPEC*.json and inputs/PLANS.json; no outcomes read and no global registry claim.'}
    from tokenizers import Tokenizer
    tokenizer=Tokenizer.from_file(str(Path(prior['base_model'])/'tokenizer.json'))
    identities,requests=[],[]
    for name,task in tasks.items():
        arms={}
        for arm in e.ARMS:
            variant=e.with_prompt(task,arm)
            prompt=variant.data.prompt
            snippet=e.example_code(prompt)
            compile(snippet,name+'/'+arm,'exec',flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
            arms[arm]={'prompt':prompt,'prompt_sha256':e.hashlib.sha256(prompt.encode()).hexdigest(),
                'task_hash':variant.hash,'prompt_tokens':len(tokenizer.encode(prompt,add_special_tokens=False).ids),
                'offered_example':snippet,'example_sha256':e.hashlib.sha256(snippet.encode()).hexdigest()}
        if arms['restored_raw']['prompt'].replace(e.procedure(task)+'\n\n','',1)!=arms['taught_raw']['prompt']:
            raise ValueError('D to R changed more than paragraph')
        identities.append({'name':name,'context_sha256':e.hashlib.sha256(task.data.context.encode()).hexdigest(),
            'context_window_id':task.data.context_window_id,'gold_sha256':c.digest(task.data.answer),
            'catalog_sha256':c.digest(e.catalog_for(task)),'arms':arms})
    identity_by_name={t['name']:t for t in identities}
    for row in plan:
        endpoint=e.old.planned_endpoint(bindings[row['weight']])
        typed=e.capture.make_context(endpoint,row)
        context={'model':typed.model,'client':typed.client.model_dump(mode='json'),
            'sampling':typed.sampling.model_dump(mode='json')}
        if typed.model!=bindings[row['weight']]['role_map']['root'] or typed.sampling.seed!=row['seed']:
            raise ValueError('typed actual root/seed mismatch')
        variant=e.with_prompt(tasks[row['task_name']],row['arm'])
        if variant.hash!=row['task_hash']: raise ValueError('typed task changed')
        requests.append({'coordinate':row,'model_context':context,'request_metadata':e.capture.native.request_metadata(endpoint,row),
            'public_root_prompt':variant.data.prompt,'prompt_sha256':identity_by_name[row['task_name']]['arms'][row['arm']]['prompt_sha256'],
            'context_sha256':row['context_sha256'],'helper_catalog_sha256':identity_by_name[row['task_name']]['catalog_sha256'],
            'runtime_gold_present':False,'adaptivity':'Later root/child messages chosen by free policy, not predeclared paired child calls.'})
    c.write_once(e.ROOT/'inputs/PLAN.json',plan)
    c.write_once(e.ROOT/'inputs/TASKS.json',identities)
    c.write_once(e.ROOT/'inputs/REQUESTS.json',requests)
    c.write_once(e.ROOT/'inputs/BINDINGS.json',bindings)
    c.write_once(e.ROOT/'inputs/SEED_AUDIT.json',seed_audit)
    c.write_once(e.ROOT/'inputs/PUBLIC_CATALOGS.json',{t.data.context_window_id:e.catalog_for(t) for t in tasks.values()})
    proof=c.read(e.ROOT/QUALIFICATION/'RESULT.json')
    if proof['provider_calls']!=21 or proof['actual_model_calls']!=0 or proof['gpu_calls']!=0 or len(proof['cases'])!=7:
        raise ValueError('exact seven-case fake-runtime proof missing')
    command=[str(c.NATIVE_PYTHON),'-m','unittest','test_uptake','-v']
    started=time.time()
    tests=subprocess.run(command,cwd=e.ROOT,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True,timeout=120)
    c.write_once(e.ROOT/'FOCUSED_TESTS.json',{'argv':command,'returncode':tests.returncode,'stdout':tests.stdout,'stderr':tests.stderr,'seconds':time.time()-started,'gpu_calls':0})
    if tests.returncode: raise ValueError('focused tests failed; READY absent')
    sources=dict(prior['source_file_sha256'])
    paths=list(e.ROOT.glob('*.py'))+list(e.ROOT.glob('*.md'))+list((e.ROOT/'inputs').glob('*.json'))+[e.ROOT/'FOCUSED_TESTS.json',e.ROOT/'SAVED_CAPTURE_CHECK.json']
    paths += [e.PRIOR/'SPEC.json',e.PRIOR/'READY.json',e.PRIOR/'experiment.py',e.PRIOR/'receipt_api.py',e.PRIOR/'results.py',e.PRIOR/'driver.py',e.old.ROOT/'SPEC.json',e.DECISION,e.DESIGN]
    op=e.ROOT.parents[1]/'operations/2026-09-09-after-identity-receipt'
    paths += [op/'receipt_driver.py',op/'test_receipt_driver.py',op/'LIFECYCLE_AMENDMENT.md',e.ROOT.parent/'root-seed-lifecycle-continuation-v1/driver.py']
    for attempt in ('qualification-attempt-001',QUALIFICATION): paths+=list((e.ROOT/attempt).rglob('*.json'))
    sources.update({str(p):c.file_hash(p) for p in paths})
    c.authenticate(sources)
    spec={'schema':e.ROOT.name,'source_file_sha256':sources,'plan':plan,'plan_sha256':c.digest(plan),
        'tasks':identities,'policies':policies,'bindings':bindings,'phase_order':list(e.PHASES),
        'phase_weights':e.PHASE_WEIGHTS,'phase_collection_cap_seconds':e.PHASE_CAPS,
        'seed_master':e.SEED_MASTER,'seed_audit':seed_audit,'environment':prior['environment'],'image_id':prior['image_id'],
        'sampling':prior['sampling'],'renderer':prior['renderer'],'base_model':prior['base_model'],'base_manifest_sha256':prior['base_manifest_sha256'],
        'max_concurrent_pairs':8,'max_concurrent_quadruplets':8,'wall_time_cap_seconds':3600,'collection_cap_seconds':2400,
        'work_cap_seconds':3480,'cleanup_reserve_seconds':120,'outer_cap_seconds':3630,
        'exposure':prior['exposure'],'source_provenance':prior['source_provenance'],'inherited_retry_caveat':prior['inherited_retry_caveat'],
        'partial_trace_limitation':prior['partial_trace_limitation'],'scored_episodes':96,'coordinate_quadruplets':24,'live_smoke':None,
        'objective':'Native-corroborated helper uptake restored_raw minus taught_raw, separately by root; strict final success secondary.',
        'receipt_format':prior['receipt_format'],'collector_adapter':{'original_sha256':e.COLLECTOR_SHA,
            'adapted_sha256':e.hashlib.sha256(e.collector_source().encode()).hexdigest(),'changes':'Exactly two queue-chunk literals2->4; no collector semantic change.'},
        'runtime_helper_source':str(e.PRIOR/'receipt_api.py'),'qualification':QUALIFICATION,
        'causal_limits':['D->R paragraph effect under common API teaching, not retrospective explanation of receipt72','R->V receipt plus minimal availability/access documentation','root contrast counterbalanced by cohort but still has residual period confounding','free adaptive child calls are not paired','root-writable audit is not semantic validation']}
    c.write_once(e.ROOT/'SPEC.json',spec)
    e.verify()
    argv=[str(c.NATIVE_PYTHON),str(e.ROOT/'driver.py'),'run','--output',str(e.ROOT/'outputs/attempt-001')]
    ready={'schema':e.ROOT.name,'planned':96,'prepared_epoch':time.time(),'spec_sha256':c.file_hash(e.ROOT/'SPEC.json'),
        'driver_sha256':c.file_hash(e.ROOT/'driver.py'),'launch_argv':argv,'launch_command':'PYTHONDONTWRITEBYTECODE=1 '+' '.join(argv),
        'outer_cap_seconds':3630,'owned_job_cap_seconds':3600,'work_cap_seconds':3480,'collection_cap_seconds':2400,
        'phase_collection_cap_seconds':e.PHASE_CAPS,'phase_order':list(e.PHASES),
        'artifact_sha256':{str(p):c.file_hash(p) for p in [e.ROOT/'SPEC.json',e.ROOT/'FOCUSED_TESTS.json',e.ROOT/QUALIFICATION/'RESULT.json']},
        'actual_model_calls_during_preparation':0,'gpu_calls_during_preparation':0,'fake_provider_calls_during_qualification':21,
        'retained_failed_cpu_qualification':{'path':str(e.ROOT/'qualification-attempt-001'),'fake_provider_calls':3,'model_calls':0},
        'acceptance':'CPU READY only; main separately accepts and launches. No automatic queue or GPU authority.',
        'environment':'Main supplies one exclusive CUDA_VISIBLE_DEVICES and existing STRICT_RLM_CALIBRATION_API_KEY; secret values are never serialized.'}
    c.write_once(e.ROOT/'READY.json',ready)
    print(json.dumps({'ready':str(e.ROOT/'READY.json'),'ready_sha256':c.file_hash(e.ROOT/'READY.json'),'planned':96,'gpu_calls':0}))


if __name__=='__main__': prepare()
