"""Qualified 48-row owner in the exact new output namespace."""
import argparse
from pathlib import Path
import study as s,protocol as p
import sys,types
path=s.SOURCE/'owner.py';pin='6161e7eaf855c936f38a6b8f8a4ab7b47380d22dd896d6861422781af8247277'
if s.sha(path)!=pin:raise ValueError('exact owner changed')
source=path.read_text();changes=(('mnli-exact-tag32-collect','mnli-fixed-output-visible-reference48-collect'),("terminal['planned']!=32 or terminal['recorded']!=32","terminal['planned']!=48 or terminal['recorded']!=48"),("planned=32,elapsed_seconds","planned=48,elapsed_seconds"))
for old,new in changes:
    if source.count(old)!=1:raise ValueError('owner seam changed: '+old)
    source=source.replace(old,new)
module=types.ModuleType('fixed_output_visible_reference_owner');module.__file__=str(path);sys.modules[module.__name__]=module
with s.aliases({'study':s,'protocol':p}):exec(compile(source,str(path)+'::new-context-plan48','exec'),module.__dict__)
validate_argv,collector_argv,credential,binding,preflight,suite,execute=(getattr(module,x) for x in ('validate_argv','collector_argv','credential','binding','preflight','suite','execute'))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=('verify','run'));ap.add_argument('--output',type=Path,default=s.ATTEMPT);a=ap.parse_args()
    if a.command=='verify':print(s.verify()['identity'])
    else:
        result=execute(a.output);print(result);raise SystemExit(0 if result['complete'] else 1)
