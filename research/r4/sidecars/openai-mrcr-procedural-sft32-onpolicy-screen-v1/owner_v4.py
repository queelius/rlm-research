"""Additive attempt-004 owner using V4 collector."""
import argparse,importlib.util,json,sys
from pathlib import Path
import checkpoint_v4 as checkpoint
import study_v4 as study
ROOT=Path(__file__).resolve().parent;text=(ROOT/'owner.py').read_text()
text=text.replace('OUTPUT = study.ROOT / "outputs/attempt-001"','OUTPUT = study.ROOT / "outputs/attempt-004"\nCOLLECTOR = study.ROOT / "collect_v4.py"')
if text.count('str(study.ROOT / "collect.py")')!=1:raise ValueError('owner collector boundary changed')
text=text.replace('str(study.ROOT / "collect.py")','str(COLLECTOR)');_old={n:sys.modules.get(n) for n in ('study','checkpoint')};sys.modules.update(study=study,checkpoint=checkpoint)
try:
    _spec=importlib.util.spec_from_loader('sft32_onpolicy_v1_owner_for_v4',loader=None);_module=importlib.util.module_from_spec(_spec);_module.__file__=str(ROOT/'owner.py')+':v4';exec(compile(text,_module.__file__,'exec'),_module.__dict__)
finally:
    for _n,_v in _old.items():
        if _v is None:sys.modules.pop(_n,None)
        else:sys.modules[_n]=_v
OUTPUT=_module.OUTPUT;COLLECTOR=_module.COLLECTOR;verify=_module.verify;execute=_module.execute
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['verify','run']);p.add_argument('--output',type=Path,default=OUTPUT);p.add_argument('--outer-seconds',type=int,default=study.OWNER_SECONDS);a=p.parse_args()
    if a.command=='verify':print(verify()['identity'])
    else:
        v=execute(a.output,a.outer_seconds);print(json.dumps(v,sort_keys=True));raise SystemExit(0 if v['complete'] else 1)
