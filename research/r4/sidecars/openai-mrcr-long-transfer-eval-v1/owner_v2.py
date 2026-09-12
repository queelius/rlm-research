"""Additive long-transfer attempt-002 owners with corrected service dependency."""
import argparse,importlib.util,json,sys
from pathlib import Path
import checkpoint_v2 as checkpoint
import study_v2 as study
ROOT=Path(__file__).resolve().parent;text=(ROOT/'owner.py').read_text()
for old,new in [('outputs/base-001','outputs/base-002'),('outputs/checkpoint32-001','outputs/checkpoint32-002')]:
    if text.count(old)!=1:raise ValueError('V1 owner output boundary changed: '+old)
    text=text.replace(old,new)
if text.count('str(study.ROOT / "collect.py")')!=1:raise ValueError('V1 collector boundary changed')
text=text.replace('str(study.ROOT / "collect.py")','str(COLLECTOR)')
text=text.replace('STAGES = {','COLLECTOR = study.ROOT / "collect_v2.py"\n\nSTAGES = {',1)
_old={n:sys.modules.get(n) for n in ('study','checkpoint')};sys.modules.update(study=study,checkpoint=checkpoint)
try:
    _spec=importlib.util.spec_from_loader('mrcr_long_v1_owner_for_v2',loader=None);_module=importlib.util.module_from_spec(_spec);_module.__file__=str(ROOT/'owner.py')+':v2';exec(compile(text,_module.__file__,'exec'),_module.__dict__)
finally:
    for _n,_v in _old.items():
        if _v is None:sys.modules.pop(_n,None)
        else:sys.modules[_n]=_v
COLLECTOR=_module.COLLECTOR;STAGES=_module.STAGES;verify=_module.verify;execute=_module.execute
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['verify','run']);p.add_argument('--stage',choices=tuple(STAGES),required=True);p.add_argument('--output',type=Path);p.add_argument('--outer-seconds',type=int,default=study.OWNER_SECONDS);a=p.parse_args()
    if a.command=='verify':print(verify(a.stage)['identity'])
    else:
        v=execute(a.stage,a.output or STAGES[a.stage]['output'],a.outer_seconds);print(json.dumps(v,sort_keys=True));raise SystemExit(0 if v['complete'] else 1)
