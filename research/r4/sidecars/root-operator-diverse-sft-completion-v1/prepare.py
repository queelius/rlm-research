"""CPU-only freeze/qualification; no service/GPU/lock or old artifact mutation."""
import json
import os
from pathlib import Path
import subprocess
import time
import recovery as r

def prepare():
    s=r.s;old=s.verify();episodes=s.corpus();original=s.ATTEMPT
    if len(episodes)!=72 or list((original/'training').glob('checkpoint-*')):raise ValueError('exact72 and original zero checkpoint required')
    terminal=s.read(original/'OWNER_TERMINAL.json')
    baseline=[x for x in terminal['readout_inventory'] if x['arm']=='unchanged'];missing=[x for x in terminal['readout_inventory'] if x['arm']=='sft6']
    if len(baseline)!=24 or len(missing)!=24 or any(x['recorded'] for x in missing) or terminal['active_unreleased_service'] is not None:raise ValueError('original24 planned baseline/24 absent fixed6 and released owner required')
    if any(Path(x['path']).exists()!=x['recorded'] for x in baseline+missing):raise ValueError('original recorded inventory/path disagreement')
    command=s.read(original/'train-stage/gate-and-six-updates-COMMAND.json')
    failure=s.read(original/'training/FAILURE.json')
    if command['gpu_visible_to_command'] is not False or failure['message']!='MAIN must assign exactly one GPU' or (original/'training/GATE.json').exists() or (original/'training/LOAD_AUDIT.json').exists():raise ValueError('exact pre-load environment failure')
    frozen={str(path):s.sha(path) for path in sorted(original.rglob('*')) if path.is_file()}
    receipt=dict(original_attempt=str(original),original_ready_sha256=s.sha(r.OLD/'READY_v2.json'),original_scientific_identity=old['identity'],corpus_path=str(original/'capture/CORPUS_READY.json'),corpus_sha256=s.sha(original/'capture/CORPUS_READY.json'),examples=72,original_baseline_planned=24,original_baseline_records=sum(x['recorded'] for x in baseline),original_baseline_missing_ids=[x['coordinate']['id'] for x in baseline if not x['recorded']],original_sft_records=0,original_optimizer_checkpoints=0,original_failed_before_gate_and_load=True,original_artifact_sha256=frozen,readout_plan_sha256=s.sha(r.OLD/'inputs/FREE_PLAN.json'),training_interpreter=str(s.TRAIN),training_script_sha256=s.sha(r.OLD/'od_train.py'),binding_edit=dict(before="directory=s.ATTEMPT/'training';",after='directory=RECOVERY_TRAINING;',count=1),original_identity_intentionally_preserved_in_checkpoints=True,completion_identity_separate=True)
    s.write(r.ROOT/'SOURCE_RECEIPT.json',receipt)
    started=time.time();argv=[str(s.NATIVE),'-m','pytest','-q',str(r.ROOT/'test_recovery.py')]
    result=subprocess.run(argv,text=True,capture_output=True,env={**os.environ,'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1'},timeout=120)
    cpu=dict(argv=argv,returncode=result.returncode,stdout=result.stdout,stderr=result.stderr,elapsed_seconds=time.time()-started,gpu_calls=0,actual_training_popen_intercepted=True,full_4b_load_tested=False,source_sha256={str(p):s.sha(p) for p in r.ROOT.glob('*.py')})
    s.write(r.ROOT/'CPU_REPORT.json',cpu)
    if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    sources={**old['source_sha256'],str(r.OLD/'READY_v2.json'):s.sha(r.OLD/'READY_v2.json')}
    sources.update({str(p):s.sha(p) for p in r.ROOT.iterdir() if p.is_file() and p.name!='READY.json'})
    inputs={**old['input_sha256'],**frozen}
    ready=dict(source_sha256=sources,input_sha256=inputs,original_ready_sha256=r.ORIGINAL_READY_SHA,original_corpus_sha256=receipt['corpus_sha256'],starting=s.starting_policy(),training_argv_template=r.training_argv(r.ATTEMPT,'9999999999'),owner_argv=[str(s.NATIVE),str(r.ROOT/'recovery.py'),'run','--output',str(r.ATTEMPT)],outer_seconds=5400,work_seconds=5220,owned_seconds=5370,planned_new_endpoints=24,capture_repeated=False,baseline_repeated=False,fixed_updates=6,main_launch_only=True,cpu_only=True)
    ready['identity']=s.digest(ready);s.write(r.ROOT/'READY.json',ready);r.verify()
    print(json.dumps(dict(ready_sha256=s.sha(r.ROOT/'READY.json'),identity=ready['identity'],source_pins=len(sources),input_pins=len(inputs),cpu_sha256=s.sha(r.ROOT/'CPU_REPORT.json'),tests=result.stdout),sort_keys=True))

if __name__=='__main__':prepare()
