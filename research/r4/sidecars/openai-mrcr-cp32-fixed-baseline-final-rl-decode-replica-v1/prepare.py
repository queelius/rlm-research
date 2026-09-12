"""CPU-only payload freeze, real fixed-model qualification and immutable READY."""
import os
import subprocess
import time
import checkpoint
import study

def prepare():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='' and not study.READY.exists()
    prior=study.prior.verify();q=checkpoint.verify_checkpoint()
    # JSON serializes tuples as arrays; use the same type in the runtime qualifier.
    study.write_x(study.ROOT/'CHECKPOINT_QUALIFICATION.json',q)
    plan=study.schedule('cp32');source=study.prior.input_dir('held')
    old_tasks={r['name']:r for r in study.read(source/'tasks.json')};old_prefix=study.read(source/'PREFIXES.json')
    tasks=[];prefixes={}
    for c in plan:
        task=dict(old_tasks[c['source_coordinate_id']]);task['name']=c['id'];tasks.append(task)
        prefixes[c['id']]=old_prefix[c['source_coordinate_id']]
    target=study.input_dir('cp32')
    for name,value in [('tasks.json',tasks),('PREFIXES.json',prefixes),('HOST_GOLD.json',study.read(source/'HOST_GOLD.json')),
                       ('PUBLIC.json',dict(plan=plan,source_input_dir=str(source),new_seeds=True,context_units=16,episodes_per_arm=32,selection_by_outcome=False))]:
        study.write_x(target/name,value)
    (target/'HOST_GOLD.json').chmod(0o600)
    command=[str(study.NATIVE),'-m','pytest','-q','-p','no:cacheprovider','test_replica.py']
    env=dict(os.environ,CUDA_VISIBLE_DEVICES='',PYTHONDONTWRITEBYTECODE='1',TOKENIZERS_PARALLELISM='false')
    started=time.monotonic();result=subprocess.run(command,cwd=study.ROOT,env=env,capture_output=True,text=True,timeout=180)
    study.write_x(study.ROOT/'CPU_TESTS.json',dict(command=command,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,
        elapsed_seconds=time.monotonic()-started,original_red='Two missing-study implementation failures',GPU_calls=0))
    assert result.returncode==0,result.stdout+result.stderr
    pins=dict(prior['closure_sha256']);pins[str(study.PRIOR/'READY.json')]=study.sha(study.PRIOR/'READY.json')
    for p in study.ROOT.rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts:pins[str(p)]=study.sha(p)
    for p,h in pins.items():assert study.sha(p)==h,p
    r=dict(schema='fixed-model-short-decoding-replica-ready-v1',closure_sha256=pins,schedule_sha256=study.digest(plan),
        checkpoint_qualification=q,planned_total=64,episodes_per_arm=32,context_units=16,repeats_per_arm=2,
        seed_rule='202609270000+2*original_row_index+repeat',old_baseline_reused=False,new_training=False,
        temperature=.5,max_tokens=2048,total_actions=6,children=0,workers=4,caps=study.CAPS,
        fixed_argv={arm:[str(study.NATIVE),str(study.ROOT/'owner.py'),'run','--phase',arm] for arm in study.CAPS},
        GPU_admission=False,no_outcome_manipulation_gate=True)
    r['identity']=study.digest(r);study.write_x(study.READY,r);study.verify()
    print({'identity':r['identity'],'READY_sha256':study.sha(study.READY),'pins':len(pins)})
if __name__=='__main__':prepare()
