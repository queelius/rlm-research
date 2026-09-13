"""Unmodified admitted FinQA owner implementation under explicit fresh bindings."""
import argparse
import json
import collect
import metrics
import study


def implementation():
    with study.aliases({"study":study,"collect":collect,"metrics":metrics},study.PARENT):
        parent=study.load("finqa_fresh_original_owner",study.PARENT/"owner.py")
    return parent.implementation()


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("command",choices=("verify","run"))
    parser.add_argument("--outer-seconds",type=int,default=study.OWNER_SECONDS);args=parser.parse_args()
    module=implementation()
    if args.command=="verify":print(study.verify()["identity"])
    else:
        terminal=module.execute(args.outer_seconds);print(json.dumps(terminal))
        raise SystemExit(0 if terminal["complete"] else 1)
