"""Exact finite service owner with a single train-readout phase and no score gate."""
import argparse
import json
import checkpoint
import study
source=study.bound('fresh8_trainread_owner',study.PRIOR/'owner.py',study=study,checkpoint=checkpoint)
verify=source.verify;execute=source.execute
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['verify','run'])
    p.add_argument('--phase',choices=['train'],required=True);a=p.parse_args()
    if a.command=='verify':print(verify(a.phase)['identity'])
    else:
        result=execute(a.phase);print(json.dumps(result,sort_keys=True));raise SystemExit(0 if result['complete'] else 1)
