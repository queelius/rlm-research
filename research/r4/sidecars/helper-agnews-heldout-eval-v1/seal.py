"""Seal three separate owners over one frozen prospective AG heldout schedule."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

import study


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES")!="": raise ValueError("CPU-only seal requires CUDA hidden")
    command=[str(study.NATIVE),"-m","pytest","-q","test_eval.py"]
    result=subprocess.run(command,cwd=study.ROOT,capture_output=True,text=True,timeout=180,env={**os.environ,"CUDA_VISIBLE_DEVICES":"","STRICT_RLM_CALIBRATION_API_KEY":"cpu-test-placeholder"})
    study.write_x(study.ROOT/"CPU_TESTS.json",{"command":command,"returncode":result.returncode,"stdout":result.stdout,"stderr":result.stderr,"credential":"non-secret test placeholder only"})
    if result.returncode: raise ValueError("focused evaluator tests failed")
    local=[study.ROOT/name for name in ("prepare_eval.py","study.py","owner.py","test_eval.py","seal.py","EVALUATION_INTERFACE.md","CPU_TESTS.json","inputs/PUBLIC.json","inputs/HOST_GOLD.json","inputs/REQUESTS.json","inputs/BUILD_AUDIT.json")]
    frozen=study.SIDE/"helper-agnews-data-vs-mechanics-v1"
    sources=[frozen/"CPU_SELECTION_RECEIPT.json",frozen/"inputs/MANIFEST.json",frozen/"inputs/HELDOUT_PUBLIC.json",frozen/"inputs/HELDOUT_GOLD.json",study.BASELINE/"unseen_panel_study.py",study.BASELINE/"owner.py",study.BASELINE/"READY.json",study.REFERENCE_EVAL/"fourstep_panel_study.py",study.REFERENCE_EVAL/"READY.json",study.REFERENCE_TRAIN/"READY.json",study.AG_TRAIN/"READY.json",study.SOURCE_BINDING,study.MODEL/"tokenizer_config.json"]
    closure={str(path.resolve()):study.sha(path) for path in local+sources}
    for ready_path in (study.BASELINE/"READY.json",study.REFERENCE_EVAL/"READY.json",study.REFERENCE_TRAIN/"READY.json",study.AG_TRAIN/"READY.json"):
        value=study.read(ready_path)
        if "closure_sha256" in value: closure.update(value["closure_sha256"])
    # Current arms must resolve now; new AG remains intentionally conditional.
    study.binding("c32");study.binding("reference_t1")
    for arm in study.ARMS:
        plan=study.plan(arm);identity=study.digest({"plan":plan,"closure":closure})
        ready={**plan,"identity":identity,"created_epoch":time.time(),"status":"CPU_READY_MAIN_REVIEW_REQUIRED" if arm!="ag_step4" else "CPU_READY_CONDITIONAL_EXACT_AG_STEP4","question":"How do c32, reference T1 step4, and AG-trained step4 compare on the same prospectively frozen AG News heldout256?","gold_isolation":"HOST_GOLD is owner-side only and absent from every request body","metrics":["paired correctness","exact-four maps","per-label confusion","invalid/unavailable","physical calls/tokens/time"],"checkpoint_selection":False,"closure_sha256":closure,"cpu_tests":{"path":str(study.ROOT/"CPU_TESTS.json"),"sha256":study.sha(study.ROOT/"CPU_TESTS.json")},"launch_authority":"MAIN only; each arm independent and no automatic launch"}
        study.write_x(study.ready_path(arm),ready)
        print(json.dumps({"arm":arm,"identity":identity,"ready_sha256":study.sha(study.ready_path(arm))},sort_keys=True))


if __name__=="__main__": main()
