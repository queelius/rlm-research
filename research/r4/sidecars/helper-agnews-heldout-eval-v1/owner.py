"""Thin three-arm facade over the authenticated native helper evaluator."""

import argparse
import importlib.util
import json
from pathlib import Path
import sys
import types

LOCAL_ROOT=Path(__file__).resolve().parent
LOCAL_SPEC=importlib.util.spec_from_file_location("ag_heldout_local_study",LOCAL_ROOT/"study.py")
study=importlib.util.module_from_spec(LOCAL_SPEC);LOCAL_SPEC.loader.exec_module(study)
SOURCE=study.BASELINE/"owner.py"


def collector(arm):
    if arm not in study.ARMS: raise ValueError("unknown arm")
    facade=types.ModuleType("unseen_panel_study")
    for name in ("CAP","CHILD_ALIAS","MODEL","NATIVE","dependencies","schedule","read","write_x","digest","sha"):
        setattr(facade,name,getattr(study,name))
    facade.ATTEMPT=study.attempt(arm)
    facade.binding=lambda: study.binding(arm)
    facade.verify=lambda: study.verify(arm)
    facade.panel=lambda: (None,None,study.read(study.INPUTS/"PUBLIC.json"),study.read(study.INPUTS/"HOST_GOLD.json"),study.read(study.INPUTS/"REQUESTS.json"))
    spec=importlib.util.spec_from_file_location("ag_heldout_native_collector_"+arm,SOURCE)
    module=importlib.util.module_from_spec(spec);previous=sys.modules.get("unseen_panel_study");sys.modules["unseen_panel_study"]=facade
    try: spec.loader.exec_module(module)
    finally:
        if previous is None: sys.modules.pop("unseen_panel_study",None)
        else: sys.modules["unseen_panel_study"]=previous
    original=module.summarize
    def summarize(calls,gold,expected=True):
        result=original(calls,gold,expected);result.update(schema="helper-agnews-heldout-eval-result-v1",arm=arm,policy={"c32":"original c32","reference_t1":"reference T1 fourstep checkpoint-0004","ag_step4":"AG-trained checkpoint-0004"}[arm],frozen_heldout_manifest_sha256=study.sha(study.INPUTS/"BUILD_AUDIT.json"),schedule_sha256=study.digest(study.schedule()))
        return result
    module.summarize=summarize
    return module


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("command",choices=("verify","run"));parser.add_argument("--arm",required=True,choices=study.ARMS);parser.add_argument("--outer-seconds",type=int,default=study.CAP);args=parser.parse_args()
    if args.command=="verify": print(study.verify(args.arm)["identity"])
    else:
        terminal=collector(args.arm).execute(args.outer_seconds);print(json.dumps(terminal,sort_keys=True));raise SystemExit(0 if terminal["complete"] else 1)
