"""Exact accepted finite owner; each phase independently eligible regardless scores."""
import argparse
import json
import checkpoint
import study
source=study.bound('fresh8_dose_eval_owner',study.PRIOR/'owner.py',study=study,checkpoint=checkpoint)
verify=source.verify;execute=source.execute
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['verify','run'])
    p.add_argument('--phase',choices=tuple(study.CAPS),required=True);a=p.parse_args()
    if a.command=='verify':print(verify(a.phase)['identity'])
    else:
        r=execute(a.phase);print(json.dumps(r,sort_keys=True));raise SystemExit(0 if r['complete'] else 1)
