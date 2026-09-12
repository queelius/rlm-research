"""Exact qualified V3 lifecycle adaptation; current explicit module bindings."""
import argparse
import json
from types import ModuleType
import collect
import metrics
import study


def implementation():
    text=(study.PRIOR/'owner.py').read_text()
    assert text.count("'planned_calls': 72")==1
    module=ModuleType('flexible_four_qualified_owner'); module.__file__=str(study.PRIOR/'owner.py')+':60-call-cap'
    with study.aliases({'study':study,'collect':collect,'metrics':metrics},study.ROOT):
        exec(compile(text.replace("'planned_calls': 72","'planned_calls': 60"),module.__file__,'exec'),module.__dict__)
    return module.implementation()


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('command',choices=['verify','run'])
    parser.add_argument('--outer-seconds',type=int,default=study.OWNER_SECONDS); args=parser.parse_args()
    if args.command=='verify': print(study.verify()['identity'])
    else:
        value=implementation().execute(args.outer_seconds); print(json.dumps(value)); raise SystemExit(0 if value['complete'] else 1)
