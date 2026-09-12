"""CPU-test and seal the conditional qualified one-update fixed256 evaluator."""

import json
import os
import subprocess
import time

import one_update_panel_study as study


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES")!="": raise ValueError("CPU-only sealing requires empty CUDA_VISIBLE_DEVICES")
    if (study.ROOT/"READY.json").exists() or study.ATTEMPT.exists(): raise FileExistsError("READY/output exists; refusing reseal")
    training=study.read(study.TRAINING/"READY.json");c32=study.read(study.C32/"READY.json")
    if (study.sha(study.TRAINING/"READY.json")!=study.TRAIN_READY_SHA or
        training.get("identity")!=study.TRAIN_READY_IDENTITY): raise ValueError("exact sealed one-update trainer required")
    for raw,expected in training["closure_sha256"].items():
        if study.sha(raw)!=expected: raise ValueError("training closure changed: "+raw)
    for raw,expected in c32["closure_sha256"].items():
        if study.sha(raw)!=expected: raise ValueError("c32 evaluator source closure changed: "+raw)
    command=[str(study.NATIVE),"-m","pytest","-q","test_eval.py"]
    completed=subprocess.run(command,cwd=study.ROOT,capture_output=True,text=True,timeout=90,
        env={**os.environ,"CUDA_VISIBLE_DEVICES":""})
    study.write_x(study.ROOT/"CPU_TESTS.json",{"schema":"qualified-fresh48-one-update-unseen-eval-tests-v1",
        "command":command,"returncode":completed.returncode,"stdout":completed.stdout,"stderr":completed.stderr,
        "actual_source_collector_built_with_facade":True,"zero_argument_binding_and_verify_executed":True,
        "no_update_rejection_exercised":True,"created_epoch":time.time()})
    if completed.returncode: raise ValueError("focused CPU tests failed")
    closure=dict(training["closure_sha256"])
    for raw,expected in c32["closure_sha256"].items():
        if raw in closure and closure[raw]!=expected: raise ValueError("training/c32 seals disagree: "+raw)
        closure[raw]=expected
    for path in list(study.ROOT.glob("*.py"))+[study.ROOT/"CPU_TESTS.json",study.TRAINING/"READY.json",
        study.TRAINING/"EVALUATION_INTERFACE.md",study.C32/"READY.json"]:
        closure[str(path)]=study.sha(path)
    ready={"schema":"qualified-fresh48-one-update-unseen-eval-ready-v1",
        "status":"CPU_READY_CONDITIONAL_ON_UPDATED_STEP1","created_epoch":time.time(),"gpu_launched":False,
        "training_ready_sha256":study.TRAIN_READY_SHA,"training_ready_identity":study.TRAIN_READY_IDENTITY,
        "source_c32_ready_identity":c32["identity"],"closure_sha256":closure,
        "panel_manifest_identity":study.panel()[0]["manifest_identity"],"schedule_sha256":study.digest(study.schedule()),
        "fixed_primary_checkpoint_step":1,"selection":"checkpoint-0001 only; no evaluation-driven checkpoint choice",
        "command":[str(study.NATIVE),str(study.ROOT/"owner.py"),"run","--outer-seconds","600"],
        "inner_cap_seconds":600,"external_timeout_seconds":700,"output":str(study.ATTEMPT),
        "inventory":{"physical_calls":64,"record_predictions":256,"trec_test":128,"ag_news_test":128,
            "batch_size":4,"temperature":0,"root_calls":0,"training_updates":0},
        "eligibility":"Requires exact UPDATED checkpoint-0001, full committed adapter/config/AdamW-step1/RNG/state/binding, all48 pre-step differentiable replay rows within token/sequence tolerances, unchanged passing frozen qualification, and exact child-only binding with root unchanged.",
        "request_policy":"Exact c32 baseline fixed256 64-call batch4 schedule, ordered schemas, seeds and temperature zero; only authenticated child checkpoint changes.",
        "claim_boundary":"Adaptive fixed256 helper-only readout of one offline update over saved actions from two familiar contexts; not pristine generalization, root performance, or the 32-question HF-reference treatment.",
        "launch_authority":"MAIN only under shared GPU flock; do not evaluate NO_UPDATE or incomplete training output",
        "cpu_tests":{"observed":completed.stdout.strip(),"real_collector_build":True,"runtime_qualification":"owner.py verify/qualify before service start"}}
    ready["identity"]=study.digest(ready)
    study.write_x(study.ROOT/"READY.json",ready)
    print(json.dumps({"identity":ready["identity"],"ready_sha256":study.sha(study.ROOT/"READY.json"),"closure_files":len(closure)},sort_keys=True))


if __name__=="__main__": main()
