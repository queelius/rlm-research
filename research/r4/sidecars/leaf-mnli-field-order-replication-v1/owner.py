"""Qualified exact owner with additive 96-row/1800-second allocation."""
import argparse,sys,types
from pathlib import Path
import protocol as p,study as s
path=s.SOURCE/'owner.py';pin='6161e7eaf855c936f38a6b8f8a4ab7b47380d22dd896d6861422781af8247277'
if s.sha(path)!=pin:raise ValueError('exact owner changed')
source=path.read_text()
changes=(("started+1080","started+1680"),("started+1170","started+1770"),("outer_seconds=1200","outer_seconds=1800"),("owned1170 deadline","owned1770 deadline"),("mnli-exact-tag32-collect","mnli-field-order-replication96-collect"),("terminal['planned']!=32 or terminal['recorded']!=32","terminal['planned']!=96 or terminal['recorded']!=96"),("collector must retain32 slots","collector must retain96 slots"),("planned=32,elapsed_seconds","planned=96,elapsed_seconds"))
for old,new in changes:
    if source.count(old)!=1:raise ValueError('owner seam changed: '+old)
    source=source.replace(old,new)
needle="outer_seconds=1800,gpu=gpu"
if source.count(needle)!=1:raise ValueError('owner clock seam changed')
source=source.replace(needle,"outer_seconds=1800,work_deadline_epoch=work,owned_deadline_epoch=owned,gpu=gpu")
module=types.ModuleType('field_order_replication_owner');module.__file__=str(path);sys.modules[module.__name__]=module
with s.aliases({'study':s,'protocol':p}):exec(compile(source,str(path)+'::field-order-replication','exec'),module.__dict__)
validate_argv,collector_argv,credential,binding,preflight,suite,execute=(getattr(module,x) for x in ('validate_argv','collector_argv','credential','binding','preflight','suite','execute'))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=('verify','run'));ap.add_argument('--output',type=Path,default=s.ATTEMPT);args=ap.parse_args()
    if args.command=='verify':print(s.verify()['identity'])
    else:
        result=execute(args.output);print(result);raise SystemExit(0 if result['complete'] else 1)

