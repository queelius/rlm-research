import json
import os
from pathlib import Path
import subprocess
import time

import one_update_panel_study as study


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES")!="": raise ValueError("CPU-only seal requires CUDA hidden")
    if (study.ROOT/"READY.json").exists() or study.ATTEMPT.exists(): raise FileExistsError("READY/output exists")
    training=study.read(study.TRAINING/"READY.json");c32=study.read(study.C32/"READY.json")
    if study.sha(study.TRAINING/"READY.json")!=study.TRAIN_READY_SHA or training.get("identity")!=study.TRAIN_READY_IDENTITY: raise ValueError("exact V2 trainer required")
    for raw,expected in training["closure_sha256"].items():
        if study.sha(raw)!=expected: raise ValueError("training closure changed: "+raw)
    for raw,expected in c32["closure_sha256"].items():
        if study.sha(raw)!=expected: raise ValueError("c32 closure changed: "+raw)
    command=[str(study.NATIVE),"-m","pytest","-q","test_eval_v2.py"]
    started=time.monotonic();done=subprocess.run(command,cwd=study.ROOT,capture_output=True,text=True,timeout=90,env={**os.environ,"CUDA_VISIBLE_DEVICES":""})
    study.write_x(study.ROOT/"CPU_TESTS.json",{"schema":"fresh48-one-update-v2-unseen-eval-tests-v1","command":command,"returncode":done.returncode,"stdout":done.stdout,"stderr":done.stderr,"elapsed_seconds":time.monotonic()-started,"actual_collector_facade_built":True,"wrong_numpy_seed_receipt_rejected":True})
    if done.returncode: raise RuntimeError("focused tests failed")
    closure=dict(training["closure_sha256"])
    for raw,expected in c32["closure_sha256"].items():
        if raw in closure and closure[raw]!=expected: raise ValueError("source seals disagree: "+raw)
        closure[raw]=expected
    source_eval=study.SOURCE_EVAL
    for path in list(study.ROOT.glob("*.py"))+[study.ROOT/"CPU_TESTS.json",study.TRAINING/"READY.json",study.TRAINING/"EVALUATION_INTERFACE.md",study.C32/"READY.json",source_eval/"READY.json",source_eval/"one_update_panel_study.py",source_eval/"owner.py"]: closure[str(path)]=study.sha(path)
    ready={"schema":"qualified-fresh48-one-update-unseen-eval-ready-v2","status":"CPU_READY_CONDITIONAL_ON_UPDATED_STEP1_V2","created_epoch":time.time(),"gpu_launched":False,"training_ready_sha256":study.TRAIN_READY_SHA,"training_ready_identity":study.TRAIN_READY_IDENTITY,"source_c32_ready_identity":c32["identity"],"closure_sha256":closure,"panel_manifest_identity":study.panel()[0]["manifest_identity"],"schedule_sha256":study.digest(study.schedule()),"fixed_primary_checkpoint_step":1,"selection":"V2 checkpoint-0001 only; no evaluation-driven choice","command":[str(study.NATIVE),str(study.ROOT/"owner.py"),"run","--outer-seconds","600"],"inner_cap_seconds":600,"external_timeout_seconds":700,"output":str(study.ATTEMPT),"inventory":{"physical_calls":64,"record_predictions":256,"trec_test":128,"ag_news_test":128,"batch_size":4,"temperature":0,"root_calls":0,"training_updates":0},"eligibility":"Exact V2 UPDATED checkpoint, complete V1 full48 replay/step1 commit/binding contracts, plus authenticated master/Python/Torch seed 202609121401 and NumPy legacy seed 745658489 receipt.","request_policy":"Unchanged fixed256 c32 schedule/schema/seeds/T0; only authenticated child adapter changes.","claim_boundary":"Exploratory adaptive fixed256 readout after repaired-seed offline one-step update; not pristine generalization or root performance.","launch_authority":"MAIN only after training UPDATED and clean shared GPU release"}
    ready["identity"]=study.digest(ready);study.write_x(study.ROOT/"READY.json",ready)
    print(json.dumps({"identity":ready["identity"],"ready_sha256":study.sha(study.ROOT/"READY.json"),"closure_files":len(closure)},sort_keys=True))


if __name__=="__main__": main()
