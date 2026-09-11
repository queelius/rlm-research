"""Publish training-only READY after narrow actual source/input/entry CPU qualification."""
import importlib.metadata
import inspect
import os
from pathlib import Path
import subprocess
import time
import dose_study as s

def main():
    started=time.time();old=s.original().verify();episodes=s.corpus()
    if len(episodes)!=72 or (s.ROOT/'READY.json').exists():raise ValueError('exact corpus or already sealed')
    plan=s.read(s.ROOT/'inputs/EVALUATION_PLAN.json')
    if len(plan['full'])!=96 or len(plan['first_action'])!=24:raise ValueError('preplanned inventory')
    if {a['policy'] for a in plan['full']}!={'sft6','sft24'} or any(x['available'] for x in plan['full']+plan['first_action']):raise ValueError('outcome-blind inventory')
    for policy in ('sft6','sft24'):
        rows=[x['coordinate'] for x in plan['full'] if x['policy']==policy]
        if len({r['id'] for r in rows})!=48:raise ValueError('unique paired endpoints')
    full_seeds={r['coordinate']['seed'] for r in plan['full']};probe_seeds={r['coordinate']['seed'] for r in plan['first_action']}
    if len(full_seeds)!=48 or len(probe_seeds)!=12 or full_seeds&probe_seeds:raise ValueError('paired seed inventory')
    seed_pins={};collisions=[]
    def walk(value,path):
        if isinstance(value,dict):
            for k,v in value.items():
                if 'seed' in k.lower() and type(v)==int and v in full_seeds|probe_seeds|{s.MASTER}:collisions.append(dict(path=str(path),key=k,seed=v))
                if isinstance(v,(dict,list)):walk(v,path)
        elif isinstance(value,list):
            for v in value:walk(v,path)
    for d in s.SIDE.iterdir():
        if not d.is_dir() or d==s.ROOT:continue
        for sub in (d,d/'inputs',d/'prepared-v1'):
            for path in sub.glob('*.json'):
                if path.stat().st_size<=2000000 and any(k in path.name for k in ('PLAN','SEED','SPEC')):
                    seed_pins[str(path)]=s.sha(path);walk(s.read(path),path)
    if collisions:raise ValueError('named prior seed collisions '+str(collisions))
    s.write(s.ROOT/'SEED_AUDIT.json',dict(scope='other sidecars top-level/inputs/prepared-v1 PLAN/SEED/SPEC JSON <=2MB; not global',source_sha256=seed_pins,collisions=collisions,full_seeds=sorted(full_seeds),probe_seeds=sorted(probe_seeds)))
    tests=[]
    for interpreter,files in [(s.original().TRAIN,['test_restore.py','test_inputs.py']),(s.original().NATIVE,['test_owner.py'])]:
        argv=[str(interpreter),'-m','pytest','-q','-p','no:cacheprovider',*files];before=time.time()
        result=subprocess.run(argv,cwd=s.ROOT,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'},capture_output=True,text=True,timeout=120)
        tests.append(dict(argv=argv,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,elapsed_seconds=time.time()-before))
        if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    s.write(s.ROOT/'CPU_REPORT.json',dict(tests=tests,red_evidence='3 missing restorer;1 missing input builder;2 missing owner failures before implementation. CPU meta mapping additionally caught inference-only config; owner fixture caught inherited credential preflight.',actual_owner_training_popen_intercepted=True,actual_training_cli_parsed=True,actual_504_moment_validation=True,meta_parameter_map=True,actual_gpu_load=False,model_services_started=0,elapsed_seconds=time.time()-started))
    source={**old['source_sha256'],**s.read(s.RECOVERY/'READY.json')['source_sha256']}
    source.update(seed_pins)
    source.update({str(p):s.sha(p) for p in s.ROOT.iterdir() if p.is_file() and p.name!='READY.json'})
    source.update({str(s.OLD/'READY_v2.json'):s.sha(s.OLD/'READY_v2.json'),str(s.RECOVERY/'READY.json'):s.sha(s.RECOVERY/'READY.json'),str(s.INVENTORY):s.INVENTORY_SHA})
    for name in ('2026-09-10-operator-sft-dose-decision.md','2026-09-10-operator-sft-dose-decision.yaml'):
        p=s.STORE/'ideas'/name;source[str(p)]=s.sha(p)
    inputs={**old['input_sha256'],**s.read(s.OLD/'outputs/attempt-001/capture/CORPUS_READY.json')['files_sha256']}
    inputs.update({str(p):s.sha(p) for p in (s.ROOT/'inputs').glob('*.json')})
    inputs.update(s.read(s.ROOT/'inputs/PROVENANCE.json')['source_sha256'])
    for p in s.START.iterdir():
        if p.is_file():inputs[str(p)]=s.sha(p)
    cp=s.OLD/'outputs/attempt-001/capture/CORPUS_READY.json';inputs[str(cp)]=s.CORPUS_SHA
    for p,h in {**source,**inputs}.items():s.check(p,h)
    ready=dict(schema='operator-dose-training-ready-v1',status='CPU_READY_NOT_LAUNCHED',source_sha256=source,input_sha256=inputs,training_first=True,starting_adapter_sha256=s.START_SHA,starting_optimizer_step=6,fixed_final_step=24,added_full72_passes=18,fresh_optimizer=False,child_loaded=False,corpus_sha256=s.CORPUS_SHA,owner_argv=[str(s.original().NATIVE),str(s.ROOT/'dose_owner.py'),'run','--output',str(s.ATTEMPT)],verify_argv=[str(s.original().NATIVE),str(s.ROOT/'dose_owner.py'),'verify'],work_seconds=4200,owned_seconds=4290,outer_seconds=4320,remaining_readout_outer_seconds=6480,combined_outer_seconds=10800,evaluation_plan_sha256=s.sha(s.ROOT/'inputs/EVALUATION_PLAN.json'),planned_full=96,planned_first_action=24,requires_existing_private_credential_for_qualified_dependency_preflight=True,credential_logged=False,cpu_only=True,main_launch_only=True)
    ready['identity']=s.digest(ready);s.write(s.ROOT/'READY.json',ready)
    s.verify();print(dict(ready_sha256=s.sha(s.ROOT/'READY.json'),identity=ready['identity'],sources=len(source),inputs=len(inputs),tests=tests,elapsed_seconds=time.time()-started))

if __name__=='__main__':main()
