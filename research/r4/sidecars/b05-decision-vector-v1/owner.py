"""Unmodified proven fresh48 owner, explicitly rebound to this sidecar."""
import argparse
import json
import collect
import metrics
import study
with study.aliases({'study':study,'collect':collect,'metrics':metrics},study.ROOT):
    previous=study.load('vector_qualified_fresh48_owner',study.PRIOR/'owner.py')
implementation=previous.implementation


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=('verify','run'));parser.add_argument('--outer-seconds',type=int,default=700);args=parser.parse_args()
    module=implementation()
    if args.command=='verify':print(study.verify()['identity'])
    else:
        result=module.execute(args.outer_seconds);print(json.dumps(result));raise SystemExit(0 if result['complete'] else 1)
