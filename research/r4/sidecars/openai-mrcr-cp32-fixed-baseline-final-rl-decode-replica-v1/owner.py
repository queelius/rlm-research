"""Two explicit substitutions in the accepted finite owner; no shared file edits."""
import argparse
import importlib.util
import json
import sys
import checkpoint
import study

path=study.PRIOR/'owner.py';text=path.read_text()
for before,after in [("binding=checkpoint.binding('updated')","binding=checkpoint.binding(phase)"),
                     ("'--phase',phase,'--arm','updated'","'--phase',phase,'--arm',phase")]:
    assert text.count(before)==1,before
    text=text.replace(before,after)
old={n:sys.modules.get(n) for n in ('study','checkpoint')};sys.modules.update(study=study,checkpoint=checkpoint)
try:
    spec=importlib.util.spec_from_loader('decode_replica_accepted_owner',loader=None);source=importlib.util.module_from_spec(spec)
    source.__file__=str(path)+':decode_replica_projection';exec(compile(text,source.__file__,'exec'),source.__dict__)
finally:
    for n,v in old.items():
        if v is None:sys.modules.pop(n,None)
        else:sys.modules[n]=v
verify=source.verify;execute=source.execute
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['verify','run']);p.add_argument('--phase',choices=tuple(study.CAPS),required=True);a=p.parse_args()
    if a.command=='verify':print(verify(a.phase)['identity'])
    else:
        value=execute(a.phase);print(json.dumps(value,sort_keys=True));raise SystemExit(0 if value['complete'] else 1)
