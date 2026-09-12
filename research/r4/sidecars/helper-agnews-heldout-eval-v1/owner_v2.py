"""Correct AG-only scorer facade; preserves V1 collector and raw call artifacts."""

import argparse
from collections import Counter
import importlib.util
import json
from pathlib import Path


ROOT=Path(__file__).resolve().parent
STUDY_SPEC=importlib.util.spec_from_file_location("ag_eval_study_v2",ROOT/"study.py")
study=importlib.util.module_from_spec(STUDY_SPEC);STUDY_SPEC.loader.exec_module(study)
OWNER_SPEC=importlib.util.spec_from_file_location("ag_eval_owner_v1_preserved",ROOT/"owner.py")
v1=importlib.util.module_from_spec(OWNER_SPEC);OWNER_SPEC.loader.exec_module(v1)


def summarize(calls,gold,expected=True):
    expected_ids=set(gold["labels"])
    metric={"physical_calls":len(calls),"valid_calls":0,"invalid_calls":0,"request_errors":0,"predictions":0,"correct":0,"prompt_tokens":0,"completion_tokens":0,"cached_prompt_tokens":0,"wall_seconds_sum":0.0,"label_gold":Counter(),"label_correct":Counter()}
    seen=[]
    for call in calls:
        metric["wall_seconds_sum"]+=float(call.get("wall_seconds") or 0)
        for field in ("prompt_tokens","completion_tokens","cached_prompt_tokens"): metric[field]+=int(call.get(field) or 0)
        if call.get("status")=="returned_valid":
            metric["valid_calls"]+=1
            for identifier in call["ids"]:
                seen.append(identifier);label=gold["labels"][identifier];metric["label_gold"][label]+=1;metric["predictions"]+=1
                if call["prediction"][identifier]==label: metric["correct"]+=1;metric["label_correct"][label]+=1
        elif call.get("status")=="invalid_response": metric["invalid_calls"]+=1
        else: metric["request_errors"]+=1
    metric["label_gold"]=dict(metric["label_gold"]);metric["label_correct"]=dict(metric["label_correct"])
    metric["accuracy_available"]=metric["correct"]/metric["predictions"] if metric["predictions"] else None
    metric["unavailable_predictions"]=len(expected_ids)-metric["predictions"]
    duplicates=sorted(identifier for identifier,count in Counter(seen).items() if count>1);missing=sorted(expected_ids-set(seen))
    complete=len(calls)==64 and not duplicates and not missing and all(call.get("status")=="returned_valid" for call in calls)
    return {"schema":"helper-agnews-heldout-eval-result-v2","complete":complete,"inventory":{"expected_calls":64,"expected_ids":256,"attempted_calls":len(calls),"returned_ids":len(seen),"missing_ids":missing,"duplicate_ids":duplicates,"invalid_calls":metric["invalid_calls"],"request_errors":metric["request_errors"]},"datasets":{"ag_news":metric},"calls":calls,"claim_boundary":"Prospectively selected balanced AG News train-split heldout256; not guaranteed absent from base pretraining.","heldout_build_audit_sha256":study.sha(study.INPUTS/"BUILD_AUDIT.json"),"schedule_sha256":study.digest(study.schedule())}


def collector(arm):
    module=v1.collector(arm);module.summarize=summarize;return module


def ready_path(arm): return ROOT/("READY_"+arm.upper()+"_V2.json")
def verify_v2(arm):
    ready=study.read(ready_path(arm))
    for raw,expected in ready["closure_sha256"].items():
        if study.sha(raw)!=expected: raise ValueError("V2 closure changed: "+raw)
    if ready.get("schedule_sha256")!=study.digest(study.schedule()) or ready.get("arm")!=arm: raise ValueError("V2 plan changed")
    if arm!="ag_step4": study.binding(arm)
    return ready


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("command",choices=("verify","run"));parser.add_argument("--arm",required=True,choices=study.ARMS);parser.add_argument("--outer-seconds",type=int,default=study.CAP);args=parser.parse_args()
    ready=verify_v2(args.arm)
    if args.command=="verify": print(ready["identity"])
    else:
        terminal=collector(args.arm).execute(args.outer_seconds);print(json.dumps(terminal,sort_keys=True));raise SystemExit(0 if terminal["complete"] else 1)
