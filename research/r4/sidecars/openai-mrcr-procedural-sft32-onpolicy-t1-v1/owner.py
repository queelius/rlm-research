"""Fixed owner for the cp32 T1.0 G4 screen."""
import argparse,importlib.util,json,sys
from pathlib import Path
import checkpoint,study
ROOT=Path(__file__).resolve().parent;COLLECTOR=ROOT/'collect.py';_old={n:sys.modules.get(n) for n in ('study','checkpoint')};sys.modules.update(study=study,checkpoint=checkpoint)
try:
    s=importlib.util.spec_from_file_location('mrcr_t1_owner_source',study.SOURCE_SCREEN/'owner.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
finally:
    for n,v in _old.items():
        if v is None:sys.modules.pop(n,None)
        else:sys.modules[n]=v
OUTPUT=m.OUTPUT;verify=m.verify;execute=m.execute
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['verify','run']);p.add_argument('--output',type=Path,default=OUTPUT);p.add_argument('--outer-seconds',type=int,default=study.OWNER_SECONDS);a=p.parse_args()
    if a.command=='verify':print(verify()['identity'])
    else:
        v=execute(a.output,a.outer_seconds);print(json.dumps(v,sort_keys=True));raise SystemExit(0 if v['complete'] else 1)
