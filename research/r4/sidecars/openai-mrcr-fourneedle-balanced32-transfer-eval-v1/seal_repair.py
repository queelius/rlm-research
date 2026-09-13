"""Seal the observed startup repair without changing scientific inputs."""
import json,subprocess,time
from pathlib import Path
import study_repair as study
ROOT=study.ROOT;PRIOR=ROOT/'RUN_READY_V3.json';CPU=ROOT/'CPU_TESTS_SERVICE_REPAIR.json';READY=ROOT/'RUN_READY_SERVICE_REPAIR.json'
if CPU.exists() or READY.exists():raise FileExistsError('repair already sealed')
start=time.time();cmd=[str(study.NATIVE),'-m','pytest','-q','-p','no:cacheprovider',str(ROOT/'test_service_repair.py')]
p=subprocess.run(cmd,capture_output=True,text=True,timeout=180);study.write_x(CPU,{'command':cmd,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'elapsed_seconds':time.time()-start,'GPU_calls':0})
if p.returncode:raise RuntimeError(p.stdout+p.stderr)
prior=study.read(PRIOR)
for raw,h in prior['authoritative_closure_sha256'].items():
    if study.sha(Path(raw))!=h:raise ValueError('prior closure changed: '+raw)
closure=dict(prior['authoritative_closure_sha256'])
for path in (ROOT/'study_repair.py',ROOT/'checkpoint_repair.py',ROOT/'owner_repair.py',ROOT/'test_service_repair.py',ROOT/'seal_repair.py',CPU):closure[str(path)]=study.sha(path)
value={'schema':'mrcr-balanced32-service-repair-run-ready-v1','created_epoch':time.time(),'scientific_ready_sha256':study.sha(study.READY),'scientific_ready_identity':study.read(study.READY)['identity'],
 'observed_attempt001_failure':'wrong frozen-base-only service wrapper rejected valid dual-LoRA binding before science','attempt001_preserved':True,'attempt002_outputs':{'cp32':str(ROOT/'outputs/cp32-002'),'lr1e4':str(ROOT/'outputs/lr1e4-002')},
 'authoritative_closure_sha256':closure,'cpu_tests_sha256':study.sha(CPU),
 'fixed_argv':{'cp32':[str(study.NATIVE),str(ROOT/'owner_repair.py'),'run','--stage','cp32','--outer-seconds','1100'],'lr1e4':[str(study.NATIVE),str(ROOT/'owner_repair.py'),'run','--stage','lr1e4','--outer-seconds','1100']},
 'external_cap_seconds_per_arm':1200,'both_arms_required_regardless_score':True,'no_gpu_launched_during_repair':True}
value['identity']=study.digest(value);study.write_x(READY,value);print(json.dumps({'sha256':study.sha(READY),'identity':value['identity']},sort_keys=True))
