"""Same qualified1100-second cp32 owner; new collector/task source closure only."""
import argparse
import json
from pathlib import Path
import checkpoint
import study

source=study.load('literal_inspection_proven_owner',study.PARENT/'owner.py')
OUTPUT=source.OUTPUT;verify=source.verify;execute=source.execute

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['verify','run']);p.add_argument('--output',type=Path,default=OUTPUT)
    p.add_argument('--outer-seconds',type=int,default=study.OWNER_SECONDS);a=p.parse_args()
    if a.command=='verify':print(verify()['identity'])
    else:
        value=execute(a.output,a.outer_seconds);print(json.dumps(value));raise SystemExit(0 if value['complete'] else 1)
