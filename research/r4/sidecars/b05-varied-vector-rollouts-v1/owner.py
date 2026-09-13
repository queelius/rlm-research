"""Proven native owner with only48→64 physical metadata and new module bindings."""
import argparse
import json
import types
import collect
import metrics
import study


def implementation():
    path=study.ROOT.parent/'b05-public-normalization-fresh12-v1/owner.py';text=path.read_text()
    before='text.replace(before,f\'"{field}": 48\')';after='text.replace(before,f\'"{field}": 64\')'
    assert text.count(before)==1;text=text.replace(before,after)
    module=types.ModuleType('varied_vector_owner_binding');module.__file__=__file__
    with study.aliases({'study':study,'collect':collect,'metrics':metrics},study.ROOT):exec(compile(text,str(path),'exec'),module.__dict__)
    return module.implementation()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=('verify','run'));parser.add_argument('--outer-seconds',type=int,default=700);args=parser.parse_args()
    module=implementation()
    if args.command=='verify':print(study.verify()['identity'])
    else:
        result=module.execute(args.outer_seconds);print(json.dumps(result));raise SystemExit(0 if result['complete'] else 1)
