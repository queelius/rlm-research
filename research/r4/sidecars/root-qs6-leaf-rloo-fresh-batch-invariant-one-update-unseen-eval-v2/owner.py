"""Evaluate only the authenticated repaired-seed V2 child checkpoint."""

import argparse
import importlib.util
import json
import sys

import one_update_panel_study as study


SOURCE=study.C32/"owner.py"
SOURCE_SHA="c38d9bced6caa910f159e560ffcb0b354ee140f8af087bbbdb69467238f91fda"


def build_collector():
    if study.sha(SOURCE)!=SOURCE_SHA: raise ValueError("sealed c32 collector changed")
    spec=importlib.util.spec_from_file_location("fresh48_one_update_v2_collector",SOURCE)
    if spec is None or spec.loader is None: raise RuntimeError("cannot load source collector")
    collector=importlib.util.module_from_spec(spec);previous=sys.modules.get("unseen_panel_study");sys.modules["unseen_panel_study"]=study
    try: spec.loader.exec_module(collector)
    finally:
        if previous is None: sys.modules.pop("unseen_panel_study",None)
        else: sys.modules["unseen_panel_study"]=previous
    if collector.study is not study: raise ValueError("collector did not bind V2 study facade")
    return collector


collector=build_collector();original_summary=collector.summarize


def summarize(calls,gold,expected=True):
    result=original_summary(calls,gold,expected);eligibility=study.read(study.ATTEMPT/"ELIGIBILITY.json")
    result.update(schema="qualified-fresh48-one-update-unseen-result-v2",policy="authenticated repaired-seed fresh48 checkpoint-0001",primary_step=1,
        training_ready_identity=eligibility["training_ready_identity"],checkpoint_state_sha256=eligibility["checkpoint_state_sha256"],
        step_commit_sha256=eligibility["step_commit_sha256"],qualification_sha256=eligibility["qualification_sha256"],
        rng_seeds_sha256=eligibility["rng_seeds_sha256"],eligibility_sha256=study.sha(study.ATTEMPT/"ELIGIBILITY.json"),schedule_sha256=study.digest(study.schedule()))
    return result


collector.summarize=summarize
def execute(outer_seconds): return collector.execute(outer_seconds)


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("command",choices=("verify","qualify","run"));parser.add_argument("--outer-seconds",type=int,default=study.CAP);args=parser.parse_args()
    if args.command=="verify": print(study.verify()["identity"])
    elif args.command=="qualify": print(json.dumps(study.qualify_one_update(),sort_keys=True))
    else:
        terminal=execute(args.outer_seconds);print(json.dumps(terminal,sort_keys=True));raise SystemExit(0 if terminal["complete"] else 1)
