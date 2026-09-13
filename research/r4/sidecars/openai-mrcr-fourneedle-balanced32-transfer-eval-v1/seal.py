"""Seal focused CPU evidence around the already immutable scientific READY."""
import json,subprocess,time
from pathlib import Path
import study
RUN_READY=study.ROOT/'RUN_READY.json';CPU=study.ROOT/'CPU_TESTS.json'
def build():
    if RUN_READY.exists() or CPU.exists():raise FileExistsError('already sealed')
    started=time.time();p=subprocess.run([str(study.NATIVE),'-m','pytest','-q',str(study.ROOT/'test_eval.py')],text=True,capture_output=True,timeout=240)
    receipt={'schema':'mrcr-balanced32-eval-cpu-tests-v1','started_epoch':started,'elapsed_seconds':time.time()-started,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
    study.write_x(CPU,receipt)
    if p.returncode:raise RuntimeError(p.stdout+'\n'+p.stderr)
    base=study.read(study.READY);value={'schema':'mrcr-balanced32-eval-run-ready-v1','created_epoch':time.time(),'source_ready':str(study.READY),'source_ready_sha256':study.sha(study.READY),'source_ready_identity':base['identity'],
      'cpu_tests':str(CPU),'cpu_tests_sha256':study.sha(CPU),'fixed_argv':{'cp32':[str(study.NATIVE),str(study.ROOT/'owner.py'),'run','--stage','cp32','--outer-seconds','1100'],'lr1e4':[str(study.NATIVE),str(study.ROOT/'owner.py'),'run','--stage','lr1e4','--outer-seconds','1100']},
      'external_cap_seconds_per_arm':1200,'both_arms_required':True,'no_gpu_launched_during_preparation':True}
    value['identity']=study.digest(value);study.write_x(RUN_READY,value);return value
if __name__=='__main__':
    v=build();print(json.dumps({'identity':v['identity'],'sha256':study.sha(RUN_READY)},sort_keys=True))
