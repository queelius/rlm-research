"""Identical current-service finite72 owner; MAIN alone may launch."""
import argparse
import json
import study as s
import collect
import metrics
with s.aliases({'study':s,'collect':collect,'metrics':metrics},s.PARENT):
    implementation=s.load('BA18_dose_same_owner',s.PARENT/'owner.py')
execute=implementation.execute

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=('verify','run'));p.add_argument('--outer-seconds',type=int,default=s.OWNER_SECONDS);a=p.parse_args()
    if a.command=='verify':print(s.verify()['identity'])
    else:
        terminal=execute(a.outer_seconds);print(json.dumps(terminal));raise SystemExit(0 if terminal['complete'] else 1)
