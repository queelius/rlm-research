"""Additive CPU/test closure after the V1 prelaunch fixture exposed a test-only TypeError."""
import json,subprocess,time
from pathlib import Path
import study
SOURCE=study.ROOT/'READY.json'; READY=study.ROOT/'READY_V2.json'; CPU=study.ROOT/'CPU_TESTS_V2.json'
def build():
    if READY.exists() or CPU.exists():raise FileExistsError('already sealed')
    started=time.time();p=subprocess.run([str(study.NATIVE),'-m','pytest','-q',str(study.ROOT/'test_eval_v2.py')],text=True,capture_output=True,timeout=240)
    study.write_x(CPU,{'schema':'mrcr-balanced32-eval-cpu-tests-v2','started_epoch':started,'elapsed_seconds':time.time()-started,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'v1_failure_was_test_only':True})
    if p.returncode:raise RuntimeError(p.stdout+'\n'+p.stderr)
    prior=study.read(SOURCE);closure=dict(prior['closure_sha256'])
    for path in (study.ROOT/'test_eval_v2.py',study.ROOT/'seal_v2.py',CPU):closure[str(path)]=study.sha(path)
    value={'schema':'mrcr-balanced32-eval-run-ready-v2','created_epoch':time.time(),'source_ready':str(SOURCE),'source_ready_sha256':study.sha(SOURCE),'source_ready_identity':prior['identity'],
      'authoritative_closure_sha256':closure,'cpu_tests':str(CPU),'cpu_tests_sha256':study.sha(CPU),
      'fixed_argv':{'cp32':[str(study.NATIVE),str(study.ROOT/'owner.py'),'run','--stage','cp32','--outer-seconds','1100'],'lr1e4':[str(study.NATIVE),str(study.ROOT/'owner.py'),'run','--stage','lr1e4','--outer-seconds','1100']},
      'external_cap_seconds_per_arm':1200,'both_arms_required':True,'no_gpu_launched_during_preparation':True,'supersedes_unlaunched_test_receipt_only':str(study.ROOT/'CPU_TESTS.json')}
    value['identity']=study.digest(value);study.write_x(READY,value);return value
if __name__=='__main__':
    v=build();print(json.dumps({'identity':v['identity'],'sha256':study.sha(READY)},sort_keys=True))
