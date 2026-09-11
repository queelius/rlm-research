"""Qualified 48-row collector in the exact new output namespace."""
import argparse,asyncio
from pathlib import Path
import study as s,protocol as p,scoring
path=s.SOURCE/'collect.py';pin='53c9f05634aa0dc60731e96325c3f969fae8257ba63beafe57bd9c738c224b7d'
if s.sha(path)!=pin:raise ValueError('exact collector changed')
source=path.read_text();old='status=dict(planned=32,recorded=len(rows)';inventory='inventory_complete=len(rows)==32'
if source.count(old)!=1 or source.count(inventory)!=1:raise ValueError('collector status seam changed')
import sys,types
module=types.ModuleType('new_context_alien_collector');module.__file__=str(path);sys.modules[module.__name__]=module
source=source.replace(old,'status=dict(planned=48,recorded=len(rows)').replace(inventory,'inventory_complete=len(rows)==48')
with s.aliases({'study':s,'protocol':p,'scoring':scoring}):exec(compile(source,str(path)+'::new-context-plan48','exec'),module.__dict__)
run,summarize=module.run,module.summarize
if __name__=='__main__':
    import owner
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=('run',));ap.add_argument('--endpoint',required=True);ap.add_argument('--output',required=True);ap.add_argument('--deadline',required=True,type=float);a=ap.parse_args()
    owner.validate_argv([str(s.NATIVE),str(s.ROOT/'collect.py'),'run','--endpoint',a.endpoint,'--output',a.output,'--deadline',str(a.deadline)])
    print(asyncio.run(run(Path(a.endpoint),Path(a.output),a.deadline)))
