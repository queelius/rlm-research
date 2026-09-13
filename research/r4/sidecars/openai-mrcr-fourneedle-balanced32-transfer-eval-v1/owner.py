"""One bounded owned service for each fixed balanced32 endpoint."""
import argparse,importlib.util,json,sys
from pathlib import Path
import checkpoint,study
text=(study.parent.PARENT/'owner.py').read_text();old={n:sys.modules.get(n) for n in ('study','checkpoint')};sys.modules.update(study=study,checkpoint=checkpoint)
try:
    spec=importlib.util.spec_from_loader('balanced32_owner_source',loader=None);source=importlib.util.module_from_spec(spec);source.__file__=str(study.parent.PARENT/'owner.py')+':balanced32';exec(compile(text,source.__file__,'exec'),source.__dict__)
finally:
    for n,v in old.items():
        if v is None:sys.modules.pop(n,None)
        else:sys.modules[n]=v
source.STAGES={'cp32':{'arm':'cp32','output':study.ROOT/'outputs/cp32-001'},'lr1e4':{'arm':'lr1e4','output':study.ROOT/'outputs/lr1e4-001'}}
STAGES=source.STAGES;verify=source.verify;execute=source.execute
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['verify','run']);p.add_argument('--stage',choices=tuple(STAGES),required=True);p.add_argument('--output',type=Path);p.add_argument('--outer-seconds',type=int,default=study.OWNER_SECONDS);a=p.parse_args()
    if a.command=='verify':print(verify(a.stage)['identity'])
    else:
        value=execute(a.stage,a.output or STAGES[a.stage]['output'],a.outer_seconds);print(json.dumps(value,sort_keys=True));raise SystemExit(0 if value['complete'] else 1)
