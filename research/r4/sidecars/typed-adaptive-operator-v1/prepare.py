"""Reuse exact input bytes/content; freeze24/32 only after narrow native proof."""
import ast
import hashlib
import json
import os
import re
import subprocess
import time
from pathlib import Path
import experiment as e
import contract
import hooks
plan_for=e.plan_for

def freeze():
    c=e.c
    decision=e.ROOT.parents[1]/'operations/2026-09-09-continuous-allocation/TYPED_OPERATOR_PARTIAL_QUALIFICATION_DECISION.md'
    if not decision.is_file():raise ValueError('main composed evidence decision missing')
    q=e.ROOT/'qualification-attempt-002';failure=c.read(q/'FAILURE.json');providers=c.read(q/'PROVIDER_REQUESTS.json')
    episode=c.read(q/'all16/EPISODE.json');audits=list((q/'all16/typed-audit').glob('*-result.json'))
    if len(audits)!=1 or len(providers)!=1 or failure['type']!='TimeoutError' or failure['provider_calls']!=1:raise ValueError('unexpected partial fixture evidence')
    audit=c.read(audits[0]);d=audit['decision']
    if not episode['ok'] or episode['traces'][0]['root_reply']!='Answer: 1':raise ValueError('all16 reduction failed')
    if not audit['wire_schema_verified'] or audit['depth']!=1 or not d['apply'] or not d['matched'] or d['requested_ids']!=['q0001','q0002']:raise ValueError('all16 native grammar proof failed')
    if providers[0]['case']!='all16' or providers[0]['body']!=audit['native_wire_request']['body']:raise ValueError('actual native wire mismatch')
    oldproof_path=e.PRIOR/'qualification-attempt-005/RESULT.json';oldproof=c.read(oldproof_path)
    oldfilter=next(x for x in oldproof['proofs'] if x['case']=='operator-filter')
    if oldproof['status']!='SEAM_PROOF_PASS' or oldfilter['root_provider_calls']!=0 or oldfilter['child_provider_calls']!=1 or oldfilter['root_replies']!=['Answer: 1']:raise ValueError('inherited filter proof missing')
    composed_path=e.ROOT/'COMPOSED_QUALIFICATION.json'
    c.write_once(composed_path,{'status':'COMPOSED_EXPLORATORY_EVIDENCE','fresh_all16':'Actual native typed child and valid operator reduction passed.',
        'fresh_filter16':'NOT_COMPLETED: owned setup exceeded160-second fixture cap before provider request; not a fresh native filter PASS.',
        'inherited_filter16':oldfilter,'real_model_calls':0,'gpu_calls':0,'fresh_provider_calls':1,
        'fixture_seconds':failure['seconds'],'exact_batch_schema_checks':'Focused tests cover36 distinct real requests and136 planned sessions.',
        'artifact_sha256':{str(p):c.file_hash(p) for p in [decision,oldproof_path,q/'FAILURE.json',q/'PROVIDER_REQUESTS.json',q/'all16/EPISODE.json',audits[0],e.ROOT/'qualification-attempt-001/FAILURE.json']}})
    contexts=c.read(e.PRIOR/'inputs/PUBLIC.json');plan,logical=plan_for(contexts);tasks=e.make_tasks();prior=c.read(e.PRIOR/'SPEC.json')
    seed_sources={}
    for pattern in ('*/SPEC.json','*/inputs/PLAN.json','*/inputs/PLANS.json'):
        for p in e.ROOT.parent.glob(pattern):
            if e.ROOT in p.parents:continue
            raw=p.read_bytes()
            if re.search(rb'(?<![0-9])(981292801|981292802)(?![0-9])',raw):raise ValueError('seed collision: '+str(p))
            seed_sources[str(p)]=hashlib.sha256(raw).hexdigest()
    c.write_once(e.ROOT/'inputs/SEED_AUDIT.json',{'seeds':list(e.SEEDS),'order_seed':e.ORDER_SEED,'exact_collisions':[],
        'sources':seed_sources,'scope':'Top-level SPEC and named input PLAN/PLANS only; no outcome directories.'})
    for name,value in [('PUBLIC',contexts),('PLAN',plan),('LOGICAL_CELLS',logical)]:c.write_once(e.ROOT/'inputs'/f'{name}.json',value)
    requests=[]
    for row in plan:
        task=e.with_prompt(tasks[row['task_name']],row['arm'])
        files={'context.txt':task.data.context.encode(),'records.json':json.dumps(task.public_records,ensure_ascii=False).encode(),
            'query.txt':task.plain_query.encode(),'batch_contract.py':(e.PRIOR/'batch_contract.py').read_bytes(),
            'operator_program.py':(e.PRIOR/'operator_program.py').read_bytes(),'operator_config.json':json.dumps({'controller':task.controller}).encode()}
        requests.append({'coordinate':row,'task_hash':task.hash,'root_prompt':task.data.prompt,
            'runtime_file_sha256':{k:hashlib.sha256(v).hexdigest() for k,v in files.items()},'runtime_gold_present':False,'operator_root_likelihood':None})
    c.write_once(e.ROOT/'inputs/REQUESTS.json',requests)
    canonical=[]
    for ctx in contexts:
        batches=[ctx['records'][i:i+16] for i in range(0,128,16)]+[[r for r in ctx['records'] if r['user']==ctx['query_user']]]
        for batch in batches:
            prompt=contract.batch.request_for(batch);match=contract.match_request(prompt,e.catalogs([ctx])[str(1800+ctx['index'])])
            if not match['matched']:raise ValueError('canonical batch mismatch')
            canonical.append({'context_index':ctx['index'],**match})
    c.write_once(e.ROOT/'inputs/CANONICAL_REQUESTS.json',canonical)
    command=[str(c.NATIVE_PYTHON),'-m','unittest','test_contract','test_study','-v'];start=time.time()
    tests=subprocess.run(command,cwd=e.ROOT,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True,timeout=120)
    c.write_once(e.ROOT/'FOCUSED_TESTS.json',{'argv':command,'returncode':tests.returncode,'stdout':tests.stdout,'stderr':tests.stderr,'seconds':time.time()-start})
    if tests.returncode:raise ValueError('focused tests failed')
    sources=dict(prior['source_file_sha256']);typed=c.read(e.TYPED/'SPEC.json');sources.update(typed['source_file_sha256'])
    image=c.read(e.IMAGE_READY);sources.update(image['source_and_artifact_sha256'])
    paths=list(e.ROOT.glob('*.py'))+list(e.ROOT.glob('*.md'))+list((e.ROOT/'inputs').glob('*.json'))+list((e.ROOT/'qualification-attempt-001').rglob('*.json'))+list((e.ROOT/'qualification-attempt-002').rglob('*.json'))+[e.ROOT/'qualification-attempt-001/EXPERIMENT_SOURCE.py']
    paths += [e.PRIOR/'SPEC.json',e.PRIOR/'READY.json',e.PRIOR/'experiment.py',e.PRIOR/'driver.py',e.PRIOR/'results.py',e.TYPED/'SPEC.json',e.TYPED/'READY.json',e.TYPED/'hooks.py',e.TYPED/'contract.py',e.IMAGE_READY,e.DESIGN,e.ROOT/'FOCUSED_TESTS.json',composed_path,decision,oldproof_path]
    sources.update({str(p):c.file_hash(p) for p in paths})
    policy=prior['policy'];binding=e.binding_for(policy)
    spec={'schema':e.ROOT.name,'plan':plan,'plan_sha256':c.digest(plan),'logical_cells':logical,'source_file_sha256':sources,
        'policy':policy,'binding':binding,'environment':e.environment_config(),'image_id':'sha256:'+e.IMAGE,'max_concurrent_pairs':4,
        'tasks':[{'name':name,'task_hash':t.hash,'prompt':t.data.prompt,'context_sha256':hashlib.sha256(t.data.context.encode()).hexdigest()} for name,t in sorted(tasks.items())],
        'caps':{'startup':180,'collection':1440,'work':1680,'inclusive_owned':1800,'outer':1830,'cleanup_reserve':120},
        'primary':'User filter-all strict count accuracy with nulls; realized classification cost among completed successes and all planned work separately.',
        'planned_child_sessions_if_complete':136,'planned_root_model_calls':0,'physical_executions':24,'logical_references':32,
        'exposure':'All original adaptive contexts now exposed; no reselection; leaf-train-supported, unknown dataset license.',
        'operator_root_behavior_likelihood':None,'child_training_credit':False,'grammar':'Ordered exact public ID→six-label map; constrained child action space, not semantic validation.',
        'shared_global':'Eight actual global executions referenced twice, never independent and never double-costed.',
        'answer_skew':prior['answer_skew'],'inherited_retries':'nano transient retry capability unchanged; no new retry/reroll/fallback.',
        'adapter_sha256':{'collector':hashlib.sha256(e.collector_source().encode()).hexdigest(),'native_hook':hashlib.sha256(hooks.ADAPTED.encode()).hexdigest()}}
    c.write_once(e.ROOT/'SPEC.json',spec);e.verify()
    import driver
    driver.verify()
    argv=[str(c.NATIVE_PYTHON),str(e.ROOT/'driver.py'),'run','--output',str(e.ROOT/'outputs/attempt-001')]
    ready={'schema':e.ROOT.name,'planned':24,'logical_cells':32,'prepared_epoch':time.time(),'spec_sha256':c.file_hash(e.ROOT/'SPEC.json'),
        'driver_sha256':c.file_hash(e.ROOT/'driver.py'),'launch_argv':argv,'launch_command':'PYTHONDONTWRITEBYTECODE=1 '+' '.join(argv),
        'outer_cap_seconds':1830,'owned_job_cap_seconds':1800,'work_cap_seconds':1680,'collection_cap_seconds':1440,
        'artifact_sha256':{str(p):c.file_hash(p) for p in (e.ROOT/'SPEC.json',e.ROOT/'FOCUSED_TESTS.json',composed_path,decision)},
        'cpu_fixture_provider_calls':1,'real_model_calls':0,'gpu_calls':0,
        'retained_cpu_failure':'attempt001: setup45 expired before provider; attempt002: all16 native passed, filter16 setup exceeded160s fixture cap before provider. Composed evidence explicitly accepted by main, not a fresh filter PASS. Symmetric study setup120 under owned1800.',
        'acceptance':'CPU READY only; main separately accepts and launches.'}
    c.write_once(e.ROOT/'READY.json',ready)
    print(json.dumps({'ready':str(e.ROOT/'READY.json'),'ready_sha256':c.file_hash(e.ROOT/'READY.json'),'planned':24,'logical':32}),flush=True)

if __name__=='__main__':freeze()
