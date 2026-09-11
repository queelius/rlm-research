"""Freeze source/requests/costs after CPU qualification; publish READY last."""
import ast
import copy
import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path
import experiment as e
import driver
from batch_contract import request_for


def frozen_input(path,value):
    # Explicit CPU preparation restart after serialization failure, never an episode retry.
    if path.exists():
        if e.c.read(path)!=value:raise ValueError('already-frozen preparation input changed: '+str(path))
        return
    e.c.write_once(path,value)


def freeze():
    c=e.c;root=e.ROOT
    proof=c.read(root/'qualification-attempt-005/RESULT.json')
    cancel=c.read(root/'qualification-cancel-attempt-001/RESULT.json')
    if proof['status']!='SEAM_PROOF_PASS' or not proof['free_has_no_operator_program_or_config'] or not proof['query_aware_filter_fixture'] or cancel['status']!='OWNED_CANCELLATION_PASS':
        raise ValueError('required corrected-surface/native/cancellation CPU proofs absent')
    if hashlib.sha256(e.DEFINITIONS.encode()).hexdigest()!='b4c783af63b6c94b79750471c9b129c686de6cd1661c3fac95b695012cc34860':
        raise ValueError('historical definitions changed')
    plan=c.read(root/'inputs/PLAN.json');logical=c.read(root/'inputs/LOGICAL_CELLS.json');tasks=e.make_tasks()
    requests=[]
    common=['context.txt','records.json','query.txt','batch_contract.py']
    for row in plan:
        task=e.with_prompt(tasks[row['task_name']],row['arm'])
        public_bytes={'context.txt':task.data.context.encode(),'records.json':json.dumps(task.public_records,ensure_ascii=False).encode(),
            'query.txt':task.plain_query.encode(),'batch_contract.py':(root/'batch_contract.py').read_bytes()}
        if task.controller!='free':
            public_bytes.update({'operator_program.py':(root/'operator_program.py').read_bytes(),
                'operator_config.json':json.dumps({'controller':task.controller}).encode()})
        requests.append({'id':row['id'],'task_hash':task.hash,'prompt':task.data.prompt,
            'prompt_sha256':hashlib.sha256(task.data.prompt.encode()).hexdigest(),
            'files':{key:hashlib.sha256(value).hexdigest() for key,value in public_bytes.items()},
            'controller':task.controller,'root_training_eligibility':'not_applicable_operator' if task.controller!='free' else 'no_training_authorized'})
    frozen_input(root/'inputs/REQUESTS.json',requests)
    canonical=[]
    for context in c.read(root/'inputs/PUBLIC.json'):
        batches=[context['records'][i:i+16] for i in range(0,128,16)]
        batches.append([r for r in context['records'] if r['user']==context['query_user']])
        for batch in batches:
            text=request_for(batch)
            canonical.append({'context':context['index'],'ordered_ids':[r['id'] for r in batch],
                'request':text,'request_sha256':hashlib.sha256(text.encode()).hexdigest()})
    frozen_input(root/'inputs/CANONICAL_REQUESTS.json',canonical)
    seed_sources={}
    for pattern in ('*/SPEC.json','*/inputs/PLAN.json','*/inputs/PLANS.json','*/inputs/REQUESTS.json'):
        for path in root.parent.glob(pattern):
            if path.is_relative_to(root):continue
            payload=path.read_bytes()
            if re.search(rb'(?<![0-9])(981281401|981281402)(?![0-9])',payload):
                raise ValueError('declared seed collision in '+str(path))
            seed_sources[str(path)]=hashlib.sha256(payload).hexdigest()
    frozen_input(root/'inputs/SEED_AUDIT.json',{'declared_seeds':[981281401,981281402],
        'exact_collisions':[],'source_sha256':seed_sources,'scope':'Top-level sidecar SPEC and named input PLAN/PLANS/REQUESTS only; no outcome directories opened.'})
    prior=c.read(root.parent/'root-receipt-uptake-v1/SPEC.json')
    sources=dict(prior['source_file_sha256'])
    decision=root.parents[1]/'operations/2026-09-09-continuous-allocation/ADAPTIVE_FILTER_CPU_DECISION.md'
    design=root.parents[1]/'ideas/2026-09-09-adaptive-filter-pilot-design.md'
    for path in [*root.glob('*.py'),*root.glob('*.md'),*root.glob('inputs/*.json'),decision,design,
                 root.parent/'root-receipt-uptake-v1/experiment.py',root.parent/'root-receipt-uptake-v1/driver.py']:
        sources[str(path)]=c.file_hash(path)
    sources.update(c.read(root/'inputs/PROVENANCE.json')['source_sha256'])
    sources.update({p:r['sha256'] for p,r in c.read(root/'inputs/PROVENANCE.json')['later_catalogues'].items()})
    extra=c.read(root/'inputs/CHILD_ROLE_CATALOG_CHECK.json');sources[extra['catalogue_path']]=extra['catalogue_sha256']
    policy=c.read(e.old.ROOT/'SPEC.json')['policies']['step8'];binding=e.binding_for(policy)
    for model in binding['models'].values():
        for name,key in [('adapter_model.safetensors','adapter_sha256'),('adapter_config.json','config_sha256')]:
            sources[str(Path(model['path'])/name)]=model[key]
    c.authenticate(sources)
    from verifiers.v1.envs.single_agent import SingleAgentEnvConfig
    environment=e.environment_config();SingleAgentEnvConfig.model_validate(copy.deepcopy(environment))
    spec={'schema':root.name,'plan':plan,'plan_sha256':c.digest(plan),'logical_cells':logical,
        'source_file_sha256':sources,'policy':policy,'binding':binding,'environment':environment,
        'image_id':prior['image_id'],'max_concurrent_pairs':4,
        'tasks':[{'name':name,'task_hash':task.hash,'prompt':task.data.prompt,'context_sha256':hashlib.sha256(task.data.context.encode()).hexdigest()} for name,task in sorted(tasks.items())],
        'caps':{'work':2580,'inclusive_owned':2700,'outer':2730,'collection':2280,'cleanup_reserve':120,'startup':180},
        'request_commonality':'Same ordered records/request builder/seed implies same intended child string; corrected CPU proof compares actual full initial native tokens. Divergent free requests are not paired child calls.',
        'primary':'Strict exact terminal integer, null for unanswered/incomplete; every planned cell retained. No coverage reward, answer repair or new model selection.',
        'operator':'Operator-authored actions have no sampled root call or root likelihood. Child-native traces are not root-training exports.',
        'shared_global':'Eight fixed global outcomes each referenced twice; physical40, logical48, context clusters4.',
        'answer_skew':'User2/1/2/2: constant2 hits6/8 repeated-seed user cells; global16/18/22/20. No reallocation.'}
    c.write_once(root/'SPEC.json',spec)
    command=[str(c.NATIVE_PYTHON),'-m','unittest','discover','-s',str(root),'-p','test_*.py','-v']
    started=time.time()
    result=subprocess.run(command,cwd=root,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True,timeout=120)
    c.write_once(root/'FOCUSED_TESTS.json',{'argv':command,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'seconds':time.time()-started,'gpu_calls':0})
    if result.returncode:raise ValueError('focused tests failed; no READY')
    for path in root.glob('*.py'):
        compile(path.read_text(),str(path),'exec',flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT if path.name=='operator_program.py' else 0)
    driver.verify()
    artifacts=[root/'SPEC.json',root/'FOCUSED_TESTS.json']
    for directory in ('qualification-attempt-005','qualification-cancel-attempt-001'):
        artifacts.extend((root/directory).rglob('*.json'))
    ready={'schema':root.name,'prepared_epoch':time.time(),'planned':40,'logical_cells':48,
        'spec_sha256':c.file_hash(root/'SPEC.json'),'driver':str(root/'driver.py'),'driver_sha256':c.file_hash(root/'driver.py'),
        'python':str(c.NATIVE_PYTHON),'output':str(root/'outputs/attempt-001'),'global_cap_seconds':2700,'outer_cap_seconds':2730,
        'artifact_sha256':{str(p):c.file_hash(p) for p in artifacts},'actual_model_calls':0,'gpu_calls':0,
        'launch_argv':[str(c.NATIVE_PYTHON),str(root/'driver.py'),'run','--output',str(root/'outputs/attempt-001')],
        'authority':'CPU-ready only; main alone accepts/launches with one assigned GPU and existing credential. No training authorized.'}
    c.write_once(root/'READY.json',ready)
    print(json.dumps({'planned':40,'logical':48,'ready_sha256':c.file_hash(root/'READY.json'),'spec_sha256':ready['spec_sha256']}),flush=True)


if __name__=='__main__':freeze()
