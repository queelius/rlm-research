"""Evaluate only authenticated four-step checkpoint-0004 on frozen unseen256."""

import argparse
import importlib.util
import json
import sys

import fourstep_panel_study as study


SOURCE=study.C32/"owner.py";SOURCE_SHA="c38d9bced6caa910f159e560ffcb0b354ee140f8af087bbbdb69467238f91fda"
if study.sha(SOURCE)!=SOURCE_SHA: raise ValueError("sealed c32 unseen collector changed")
spec=importlib.util.spec_from_file_location("fourstep_unseen_collector_owner",SOURCE)
collector=importlib.util.module_from_spec(spec);previous=sys.modules.get("unseen_panel_study");sys.modules["unseen_panel_study"]=study
try: spec.loader.exec_module(collector)
finally:
    if previous is None: sys.modules.pop("unseen_panel_study",None)
    else: sys.modules["unseen_panel_study"]=previous

original_summary=collector.summarize
def summarize(calls,gold,expected=True):
    result=original_summary(calls,gold,expected);eligibility=study.read(study.ATTEMPT/"ELIGIBILITY.json")
    result.update(schema="helper-hf-fourstep-unseen-result-v1",policy="authenticated four-step primary checkpoint-0004",
        primary_step=4,training_ready_identity=eligibility["training_ready_identity"],
        checkpoint_state_sha256=eligibility["checkpoint_state_sha256"],eligibility_sha256=study.sha(study.ATTEMPT/"ELIGIBILITY.json"),
        source_c32_ready_identity=study.read(study.C32/"READY.json")["identity"],schedule_sha256=study.digest(study.schedule()))
    return result
collector.summarize=summarize;execute=collector.execute


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("command",choices=("verify","qualify","run"));parser.add_argument("--outer-seconds",type=int,default=study.CAP);args=parser.parse_args()
    if args.command=="verify": print(study.verify()["identity"])
    elif args.command=="qualify": print(json.dumps(study.qualify_fourstep(),sort_keys=True))
    else:
        terminal=execute(args.outer_seconds);print(json.dumps(terminal,sort_keys=True));raise SystemExit(0 if terminal["complete"] else 1)
