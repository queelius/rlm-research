"""CPU input preparation and immutable acceptance; never launches a model."""
import argparse
import os
from pathlib import Path
import re
import subprocess
import time
import qsr_study as s
import qsr_data as d

def inputs():
    import qsr_native as n
    bundle=d.build();contexts={c['id']:c for c in bundle['PUBLIC.json']};tasks={}
    for name,q in bundle['QUERIES.json'].items():
        cid,family=name.split(':');query=d.question(q);gold=bundle['HOST_GOLD.json'][cid]['answers'][family]
        task=n.make_task(contexts[cid],query,gold,name);prefix=n.first_prefix(task)
        if len(prefix)+2048>8192:raise ValueError('native initial prefix cannot fit without cropping')
        tasks[name]=dict(question=query,prompt=task.data.prompt,task_hash=task.hash,first_prompt_token_ids=prefix)
    bundle['TASKS.json']=tasks
    seeds=[r['seed'] for rows in bundle['PLANS.json']['training'].values() for r in rows]+[r['seed'] for r in bundle['PLANS.json']['readout']]+[s.MASTER,s.SEED]
    expression=re.compile(r'\b981381\d{3}\b');sources=[]
    for side in sorted(s.SIDE.iterdir()):
        if not side.is_dir() or side==s.ROOT:continue
        for folder in (side,side/'inputs',side/'prepared-v1',side/'prepared-v2'):
            if not folder.is_dir():continue
            for p in sorted(folder.iterdir()):
                if p.is_file() and p.suffix in ('.py','.json') and p.stat().st_size<20_000_000:
                    found=set(map(int,expression.findall(p.read_text())))&set(seeds)
                    if found:raise ValueError('fresh seed collision '+str(p))
                    if 'PLAN' in p.name or 'SPEC' in p.name or 'RECIPE' in p.name:sources.append(dict(path=str(p),sha256=s.sha(p)))
    bundle['SEED_AUDIT.json']=dict(seeds=seeds,scope='top-level source and named prepared directories, no outputs/outcome reads; not global history',scanned_metadata=sources,no_collisions=True)
    for name,value in bundle.items():s.write(s.ROOT/'inputs'/name,value)
    recipe=s.read(s.BOUNDED/'RECIPE.json')
    recipe.update(schema=s.ROOT.name,training_seed=s.SEED,optimizer_steps=12,maximum_actual_updates=12,scheduled_windows=12,refill='none; fixed24/window',selection='last actual committed update, including zero; no GPU validation',limitations='scoped-root-catalog novel contexts; child-training-exposed; operator/scope holdouts; equal episodes not equal tokens/FLOPs',caps=dict(outer=14400,work=14100,owned=14280,cleanup=180,margin=120,training_side=9000,final_total=5100,final_policy_block=2550,service_ready=180,endpoint=180,training_collection=600,training_process=480,training_forward_backward=240,training_save_release=60),admission='Authenticated returned native final1/0 separate from conservative whole-graph training admission; unreturned/no-final/unverified endpoints NULL; operational planned-zero sensitivity separate')
    s.write(s.ROOT/'RECIPE.json',recipe);s.write(s.ROOT/'START.json',dict(kind='fixed_success_sft8',policy=s.fixed_start(),fresh_rl_adam=True,selection='fixed low66c independent of current joint-SFT outcomes',approval_design_sha256=s.sha(s.ROOT/'DESIGN.md')))
    return dict(contexts=24,groups=448,tasks=len(tasks),training=288,paired_readout=96,prompt_tokens=[min(len(t['first_prompt_token_ids']) for t in tasks.values()),max(len(t['first_prompt_token_ids']) for t in tasks.values())],gpu_calls=0)

def qualify():
    fixture=s.read(s.ROOT/'qualification-native-001/RESULT.json')
    if fixture['status']!='PASS' or fixture['actual_model_calls'] or fixture['gpu_calls']:raise ValueError('actual CPU native proof missing')
    records=[]
    for label,python,args in [('native',s.NATIVE,['-m','unittest','-v','test_data','test_native','test_training','test_entrypoints']),('tiny-Adam',s.TRAIN,['-m','pytest','-q','test_tensor.py'])]:
        command=[str(python),*args];start=time.time()
        result=subprocess.run(command,cwd=s.ROOT,text=True,capture_output=True,timeout=120,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
        records.append(dict(name=label,argv=command,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,elapsed_seconds=time.time()-start))
        if result.returncode:print(result.stdout,result.stderr);raise ValueError('focused CPU test failure')
    s.write(s.ROOT/'CPU_TESTS.json',dict(status='PASS',tests=records,unittest_count=16,tiny_tensor_tests=1,native_fixture=fixture,native_fixture_result_sha256=s.sha(s.ROOT/'qualification-native-001/RESULT.json'),red_green='New data/native/cursor/endpoint/owner/tensor tests failed before implementation; committed-window recovery and failed-release gating reproduced before fixes',actual_model_calls=0,gpu_calls=0,synthetic_likelihoods_excluded_from_science=True))
    return dict(status='PASS',focused_tests=17,actual_native_cpu_fixtures=1,gpu_calls=0)

def seal():
    if s.read(s.ROOT/'CPU_TESTS.json')['status']!='PASS':raise ValueError('CPU tests missing')
    d.excluded()
    inherited=s.read(s.BOUNDED/'READY.json');sources={**inherited['source_sha256'],**inherited['input_sha256']}
    for name in ('READY.json','CAMPAIGN.json','study.py'):sources[str(s.BOUNDED/name)]=s.sha(s.BOUNDED/name)
    for name,key in [('CPU_READY.json','source_and_artifact_sha256'),('LIFECYCLE_READY_V2.json','source_sha256')]:
        manifest=s.read(s.RUNTIME/name);sources.update(manifest[key]);sources[str(s.RUNTIME/name)]=s.sha(s.RUNTIME/name)
    for name in ('study_wrapper.py','lifecycle_adapter.py','credential_preflight.py','service_wrapper_v2.py'):sources[str(s.RUNTIME/name)]=s.sha(s.RUNTIME/name)
    receipt=s.read(d.RECEIPT);sources.update(receipt['source_sha256']);sources.update({v['path']:v['sha256'] for v in receipt['files']});sources[str(d.RECEIPT)]=d.RECEIPT_SHA
    sources.update({str(p):s.sha(p) for p in list(s.ROOT.glob('*.py'))+list(s.ROOT.glob('*.md'))+[s.ROOT/'RECIPE.json',s.ROOT/'START.json',s.ROOT/'CPU_TESTS.json',s.SIDE/'root-map-contract-clarity-v1/metrics.py',s.SIDE/'root-corrective-reduction-sft-v1/inputs/NATIVE_TEMPLATE.json']})
    proof={str(p):s.sha(p) for p in (s.ROOT/'qualification-native-001').rglob('*') if p.is_file() and p.suffix in ('.json','.jsonl','.log')}
    inputs={str(p):s.sha(p) for p in (s.ROOT/'inputs').glob('*.json')};inputs.update(proof)
    for path,pin in {**sources,**inputs}.items():s.check(path,pin)
    campaign=dict(schema=s.ROOT.name,namespace=s.ROOT.name,seed=s.SEED,seed_master=s.MASTER,optimizer_seed=s.SEED,source_sha256=sources,input_sha256=inputs,scheduled_windows=12,maximum_actual_optimizer_updates=12,training_attempts=288,readout_attempts=96,root_sha256=s.fixed_start()['adapter_sha256'],child_sha256=s.CHILD_SHA,outer_seconds=14400,gpu_calls_in_preparation=0)
    campaign['campaign_id']=s.digest(campaign);s.write(s.ROOT/'CAMPAIGN.json',campaign)
    ready=dict(status='CPU_READY_WAITING_MAIN_ACCEPTANCE',campaign_id=campaign['campaign_id'],campaign_sha256=s.sha(s.ROOT/'CAMPAIGN.json'),source_sha256=sources,input_sha256=inputs,cpu_tests_sha256=s.sha(s.ROOT/'CPU_TESTS.json'),driver=str(s.ROOT/'owner.py'),driver_sha256=s.sha(s.ROOT/'owner.py'),output=str(s.ATTEMPT),verify_argv=[str(s.NATIVE),str(s.ROOT/'owner.py'),'verify'],launch_argv=[str(s.NATIVE),str(s.ROOT/'owner.py'),'run','--output',str(s.ATTEMPT)],caps=dict(outer=14400,owned=14280,work=14100,training_side=9000,mandatory_final=5100,cleanup=180,margin=120),launch_authorized=False,actual_model_calls=0,gpu_calls=0,prepared_epoch=time.time())
    s.write(s.ROOT/'READY.json',ready);s.verify_prepared()
    return dict(status=ready['status'],ready_sha256=s.sha(s.ROOT/'READY.json'),campaign_id=campaign['campaign_id'],pins=len(sources)+len(inputs))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=('inputs','qualify','seal'));a=p.parse_args();print({'inputs':inputs,'qualify':qualify,'seal':seal}[a.command]())
