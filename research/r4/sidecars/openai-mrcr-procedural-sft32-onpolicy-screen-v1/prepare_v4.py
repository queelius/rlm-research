"""Seal additive V4 innermost-verifier repair."""
import json,time
from pathlib import Path
import checkpoint_v4 as checkpoint
import study_v4 as study
V3=study.ROOT/'CPU_READY_V3.json'
def build():
    prior=study.read(V3);assert prior['identity']==study.digest({k:v for k,v in prior.items() if k!='identity'})
    for p,h in prior['closure_sha256'].items():assert study.sha(Path(p))==h,p
    checkpoint.verify_checkpoint();study.terminal_hooks();added=[study.ROOT/n for n in ('study_v4.py','checkpoint_v4.py','collect_v4.py','owner_v4.py','test_repair_v4.py','prepare_v4.py')]
    v={**{k:x for k,x in prior.items() if k not in ('identity','created_epoch','closure_sha256','output','repair')},'schema':'openai-mrcr-procedural-sft32-onpolicy-screen-ready-v4','created_epoch':time.time(),'repair':{'only_change':'rebind flat READY verifier through actual innermost inherited collector run','v3_ready':str(V3),'v3_ready_sha256':study.sha(V3),'v3_identity':prior['identity'],'science_schedule_changed':False,'sampling_changed':False,'checkpoint_changed':False,'terminal_hooks_changed':False},'output':str(study.ROOT/'outputs/attempt-004'),'closure_sha256':{**prior['closure_sha256'],str(V3):study.sha(V3),**{str(p):study.sha(p) for p in added}}};v['identity']=study.digest(v);study.write_x(study.READY,v);return v
def verify():
    v=study.read(study.READY);assert v['identity']==study.digest({k:x for k,x in v.items() if k!='identity'})
    for p,h in v['closure_sha256'].items():assert study.sha(Path(p))==h,p
    return v
if __name__=='__main__':
    v=verify() if study.READY.exists() else build();print(json.dumps({'identity':v['identity'],'sha256':study.sha(study.READY)},sort_keys=True))
