"""Explicit new collector binding, qualified V3 lifecycle, exact cached base model."""
import argparse
import json
from types import ModuleType
import collect
import metrics
import study


def implementation():
    text=(study.PRIOR/'owner.py').read_text()
    for before,after in (("'planned_calls': 72","'planned_calls': 12"),("'planned_final_slots': 24","'planned_final_slots': 12")):
        assert text.count(before)==1;text=text.replace(before,after)
    module=ModuleType('answer_contract_v3_owner');module.__file__=str(study.PRIOR/'owner.py')+':12-call-12-new-final'
    with study.aliases({'study':study,'collect':collect,'metrics':metrics},study.ROOT):exec(compile(text,module.__file__,'exec'),module.__dict__)
    return module.implementation()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['verify','run']);parser.add_argument('--outer-seconds',type=int,default=study.OWNER_SECONDS);args=parser.parse_args()
    if args.command=='verify':print(study.verify()['identity'])
    else:
        study.check_binding(study.base_owner().study.binding())
        value=implementation().execute(args.outer_seconds);print(json.dumps(value));raise SystemExit(0 if value['complete'] else 1)
