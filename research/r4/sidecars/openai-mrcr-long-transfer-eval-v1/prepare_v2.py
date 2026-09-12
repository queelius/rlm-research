"""Seal additive long-transfer dual-service dependency repair."""
import json,time
from pathlib import Path
import checkpoint_v2 as checkpoint
import study_v2 as study
V1=study.ROOT/'READY.json'
def build():
    prior=study.read(V1);assert prior['identity']==study.digest({k:v for k,v in prior.items() if k!='identity'})
    for p,h in prior['closure_sha256'].items():assert study.sha(Path(p))==h,p
    checkpoint.verify_checkpoint();study.terminal_hooks();suite=study.dependencies()
    expected=study.SIDE/'runtime-an22-5801-v1/service_wrapper_v2.py'
    if suite.SERVE!=expected or suite.life.__dict__.get('ALLOCATION_SERVICE')!=expected:raise ValueError('dual-service repair absent')
    added=[study.ROOT/n for n in ('study_v2.py','checkpoint_v2.py','collect_v2.py','owner_v2.py','prepare_v2.py','test_repair_v2.py')]
    v={**{k:x for k,x in prior.items() if k not in ('identity','created_epoch','closure_sha256','outputs')},'schema':'openai-mrcr-long-transfer-evaluation-ready-v2','created_epoch':time.time(),'repair':{'only_change':'route service startup through procedural eval dual-LoRA dependency override','v1_ready':str(V1),'v1_ready_sha256':study.sha(V1),'v1_identity':prior['identity'],'failed_v1_outputs':['outputs/base-001','outputs/checkpoint32-001'],'science_schedule_changed':False,'sampling_changed':False,'bindings_changed':False,'hooks_changed':False},'outputs':{'base':str(study.ROOT/'outputs/base-002'),'checkpoint32':str(study.ROOT/'outputs/checkpoint32-002')},'closure_sha256':{**prior['closure_sha256'],str(V1):study.sha(V1),**{str(p):study.sha(p) for p in added}}};v['identity']=study.digest(v);study.write_x(study.READY,v);return v
def verify():
    v=study.read(study.READY);assert v['identity']==study.digest({k:x for k,x in v.items() if k!='identity'})
    for p,h in v['closure_sha256'].items():assert study.sha(Path(p))==h,p
    return v
if __name__=='__main__':
    v=verify() if study.READY.exists() else build();print(json.dumps({'identity':v['identity'],'sha256':study.sha(study.READY)},sort_keys=True))
