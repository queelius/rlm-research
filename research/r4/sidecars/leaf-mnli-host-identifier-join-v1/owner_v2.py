"""Qualified exact owner with additive 48-row/1440-second allocation."""
import argparse,sys,types
from pathlib import Path
import protocol_v2 as p,study as s

path=s.SOURCE/'owner.py';pin='6161e7eaf855c936f38a6b8f8a4ab7b47380d22dd896d6861422781af8247277'
if s.sha(path)!=pin:raise ValueError('exact owner changed')
source=path.read_text()
if source.count("import protocol;")!=1:raise ValueError("owner runtime protocol seam changed")
source=source.replace("import protocol;","import protocol_v2 as protocol;")
if source.count("str(s.ROOT/'collect.py')")!=2:raise ValueError('owner collector path seams changed')
source=source.replace("str(s.ROOT/'collect.py')","str(s.ROOT/'collect_v2.py')")
changes=(
    ("s.ROOT/'service_wrapper.py'","s.ROOT/'service_wrapper_v2.py'"),
    ("started+1080","started+1320"),("started+1170","started+1410"),
    ("outer_seconds=1200","outer_seconds=1440"),("owned1170 deadline","owned1410 deadline"),
    ("s.ROOT/'PLAN.json'","s.ROOT/'PLAN_v2.json'"),
    ("mnli-exact-tag32-collect","mnli-host-identifier-join48-collect"),
    ("terminal['planned']!=32 or terminal['recorded']!=32","terminal['planned']!=48 or terminal['recorded']!=48"),
    ("collector must retain32 slots","collector must retain48 slots"),("planned=32,elapsed_seconds","planned=48,elapsed_seconds"))
for old,new in changes:
    if source.count(old)!=1:raise ValueError('owner seam changed: '+old)
    source=source.replace(old,new)
needle="outer_seconds=1440,gpu=gpu"
if source.count(needle)!=1:raise ValueError('owner clock receipt seam changed')
source=source.replace(needle,"outer_seconds=1440,work_deadline_epoch=work,owned_deadline_epoch=owned,gpu=gpu")
module=types.ModuleType('visible_reference_owner_v2');module.__file__=str(path);sys.modules[module.__name__]=module
with s.aliases({'study':s,'protocol':p}):exec(compile(source,str(path)+'::visible-reference48-v2','exec'),module.__dict__)
validate_argv,collector_argv,credential,binding,preflight,suite,execute=(getattr(module,x) for x in ('validate_argv','collector_argv','credential','binding','preflight','suite','execute'))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=('verify','run'));ap.add_argument('--output',type=Path,default=s.ATTEMPT);a=ap.parse_args()
    if a.command=='verify':print(s.verify()['identity'])
    else:
        result=execute(a.output);print(result);raise SystemExit(0 if result['complete'] else 1)
