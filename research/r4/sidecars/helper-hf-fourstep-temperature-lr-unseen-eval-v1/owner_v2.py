"""Run one corrected arm-specific authenticated checkpoint-0004 evaluator."""

import argparse
import importlib.util
import json
import sys

import arm_eval_study_v2 as study


def build(arm):
 study.select(arm);source=study.C32/"owner.py";spec=importlib.util.spec_from_file_location("corrected_arm_unseen_collector_owner",source);collector=importlib.util.module_from_spec(spec);previous=sys.modules.get("unseen_panel_study");sys.modules["unseen_panel_study"]=study
 try:spec.loader.exec_module(collector)
 finally:
  if previous is None:sys.modules.pop("unseen_panel_study",None)
  else:sys.modules["unseen_panel_study"]=previous
 original=collector.summarize
 def summarize(calls,gold,expected=True):
  result=original(calls,gold,expected);eligibility=study.read(study.ATTEMPT/"ELIGIBILITY.json");result.update(schema="helper-hf-fourstep-arm-unseen-result-v2",policy="authenticated arm-specific primary checkpoint-0004",experimental_arm=eligibility["arm"],primary_step=4,training_ready_identity=eligibility["training_ready_identity"],checkpoint_state_sha256=eligibility["checkpoint_state_sha256"],eligibility_sha256=study.sha(study.ATTEMPT/"ELIGIBILITY.json"),schedule_sha256=study.digest(study.schedule()));return result
 collector.summarize=summarize;return collector


if __name__=="__main__":
 parser=argparse.ArgumentParser();parser.add_argument("command",choices=("verify","qualify","run"));parser.add_argument("--arm",choices=tuple(study.ARMS),required=True);parser.add_argument("--outer-seconds",type=int,default=study.CAP);args=parser.parse_args()
 if args.command=="verify":print(study.verify(args.arm)["identity"])
 elif args.command=="qualify":print(json.dumps(study.qualify_arm(args.arm),sort_keys=True))
 else:
  study.verify(args.arm);terminal=build(args.arm).execute(args.outer_seconds);print(json.dumps(terminal,sort_keys=True));raise SystemExit(0 if terminal["complete"] else 1)
