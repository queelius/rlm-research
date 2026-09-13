"""Authoritative additive entrypoint repair; scientific READY is unchanged."""
import json,time
from pathlib import Path
import study
PRIOR=study.ROOT/'READY_V2.json';READY=study.ROOT/'RUN_READY_V3.json'
if READY.exists():raise FileExistsError(READY)
p=study.read(PRIOR)
for raw,h in p['authoritative_closure_sha256'].items():
    if study.sha(Path(raw))!=h:raise ValueError('prior closure changed: '+raw)
closure=dict(p['authoritative_closure_sha256'])
for path in (study.ROOT/'owner_v2.py',study.ROOT/'seal_v3.py'):closure[str(path)]=study.sha(path)
value={'schema':'mrcr-balanced32-eval-run-ready-v3','created_epoch':time.time(),'scientific_ready':str(study.READY),'scientific_ready_sha256':study.sha(study.READY),'scientific_ready_identity':study.read(study.READY)['identity'],
 'supersedes_unlaunched_entrypoint_only':str(PRIOR),'authoritative_closure_sha256':closure,
 'fixed_argv':{'cp32':[str(study.NATIVE),str(study.ROOT/'owner_v2.py'),'run','--stage','cp32','--outer-seconds','1100'],'lr1e4':[str(study.NATIVE),str(study.ROOT/'owner_v2.py'),'run','--stage','lr1e4','--outer-seconds','1100']},
 'external_cap_seconds_per_arm':1200,'both_arms_required':True,'no_gpu_launched_during_preparation':True}
value['identity']=study.digest(value);study.write_x(READY,value)
print(json.dumps({'identity':value['identity'],'sha256':study.sha(READY)},sort_keys=True))
