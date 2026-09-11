"""Additive scoring-amendment owner; exact same fresh namespace/protocol/cap."""
import argparse
from pathlib import Path
from types import ModuleType
import study as s

def verify_ready():
    s.verify();ready=s.read(s.ROOT/'READY_V2.json')
    if s.digest({k:v for k,v in ready.items() if k!='identity'})!=ready['identity']:raise ValueError('amendment READY identity')
    for path,pin in ready['source_sha256'].items():
        if s.sha(path)!=pin:raise ValueError('amendment source changed: '+path)
    return ready

SOURCE=s.ROOT/'owner.py'
if s.sha(SOURCE)!='c6d4a72d01b335c0553e7cf96c66fe37d29ebf55a4b6aea17e833c6dd59168d1':raise ValueError('original sealed owner changed')
text=SOURCE.read_text()
for before,after,count in [("s.ROOT/'collect.py'","s.ROOT/'collect_v2.py'",2),('private=credential();ready=s.verify()','private=credential();ready=verify_ready()',1),('ready_sha256=s.sha(s.ROOT/\'READY.json\')','ready_sha256=s.sha(s.ROOT/\'READY_V2.json\')',1)]:
    if text.count(before)!=count:raise ValueError('owner amendment seam changed: '+before)
    text=text.replace(before,after)
module=ModuleType('partition_owner_scoring_v2');module.__file__=str(Path(__file__).resolve());module.__dict__['verify_ready']=verify_ready
exec(compile(text,str(SOURCE)+':scoring-amendment-v2','exec'),module.__dict__)
collector_argv=module.collector_argv;validate_argv=module.validate_argv;execute=module.execute

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=('verify','run'));ap.add_argument('--output',type=Path,default=s.ATTEMPT);args=ap.parse_args()
    if args.command=='verify':print(verify_ready()['identity'])
    else:
        result=execute(args.output);print(result);raise SystemExit(0 if result['complete'] else 1)
