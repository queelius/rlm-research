"""Seal the conditional step4-only native unseen-panel evaluator."""

import json
import os
from pathlib import Path
import subprocess
import time

import fourstep_panel_study as study


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES")!="": raise ValueError("CPU-only sealing requires empty CUDA_VISIBLE_DEVICES")
    if (study.ROOT/"READY.json").exists(): raise FileExistsError("preserve existing eval READY")
    training=study.read(study.TRAINING/"READY.json");c32=study.read(study.C32/"READY.json")
    if study.sha(study.TRAINING/"READY.json")!=study.TRAIN_READY_SHA or training["identity"]!=study.TRAIN_READY_IDENTITY:
        raise ValueError("exact sealed fourstep READY required")
    closure=dict(training["closure_sha256"])
    for path,expected in c32["closure_sha256"].items():
        if path in closure and closure[path]!=expected: raise ValueError("source seals disagree: "+path)
        closure[path]=expected
    command=[str(study.NATIVE),"-m","pytest","-q","test_eval.py"]
    tests=subprocess.run(command,cwd=study.ROOT,capture_output=True,text=True,timeout=90,env={**os.environ,"CUDA_VISIBLE_DEVICES":""})
    study.write_x(study.ROOT/"CPU_TESTS.json",{"command":command,"returncode":tests.returncode,"stdout":tests.stdout,"stderr":tests.stderr})
    if tests.returncode: raise ValueError("focused CPU tests failed")
    paths=list(study.ROOT.glob("*.py"))+[study.ROOT/"CPU_TESTS.json",study.TRAINING/"READY.json",study.TRAINING/"EVALUATION_INTERFACE.md",study.C32/"READY.json"]
    closure.update({str(path):study.sha(path) for path in paths})
    ready={"schema":"helper-hf-fourstep-unseen-eval-ready-v1","status":"CPU_READY_CONDITIONAL_ON_COMPLETED_FOURSTEP_PRIMARY",
        "identity":study.digest(closure),"created_epoch":time.time(),"gpu_launched":False,"closure_sha256":closure,
        "training_ready_sha256":study.TRAIN_READY_SHA,"training_ready_identity":study.TRAIN_READY_IDENTITY,
        "source_c32_ready_identity":c32["identity"],"panel_manifest_identity":study.panel()[0]["manifest_identity"],
        "fixed_primary_checkpoint_step":4,"selection":"step4 predeclared primary only; no evaluation-driven checkpoint choice",
        "schedule_sha256":study.digest(study.schedule()),"command":[str(study.NATIVE),str(study.ROOT/"owner.py"),"run","--outer-seconds","600"],
        "inner_cap_seconds":600,"external_timeout_seconds":700,"launch_authority":"MAIN only under shared GPU flock",
        "inventory":{"physical_calls":64,"record_predictions":256,"trec_test":128,"ag_news_test":128,"batch_size":4,"root_calls":0,"training_updates":0},
        "policy":{"temperature":0,"request_bodies":"exact frozen c32 unseen schedule","ordered_schemas":True,"service":"fresh; only authenticated child binding changes"},
        "eligibility":"Requires COMPLETED_FOUR_UPDATES primary step4 plus four ordered state/STEP_COMMIT/collection/qualification/group-commit lineages, recomputed probability gates, serialized cumulative AdamW steps1..4, and exact child-only binding.",
        "claim_boundary":"Adaptive reuse of a panel absent from verified c32 optimizer inputs/new32 but not claimed absent from base pretraining; no root or faithfulness claim.",
        "cpu_tests":{"observed":tests.stdout.strip(),"actual_artifact_validation":"run owner.py qualify after fourstep completion before any service launch"},
        "environment":training.get("environment")}
    study.write_x(study.ROOT/"READY.json",ready)
    print(json.dumps({"ready_sha256":study.sha(study.ROOT/"READY.json"),"identity":ready["identity"],"tests":tests.stdout.strip()}))


if __name__=="__main__":main()
