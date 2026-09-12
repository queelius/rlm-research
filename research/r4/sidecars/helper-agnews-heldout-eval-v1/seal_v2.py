"""Additive seal for corrected AG-only denominators and claim boundary."""

import json
import os
from pathlib import Path
import subprocess
import time

import study


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES")!="": raise ValueError("CPU-only seal requires CUDA hidden")
    command=[str(study.NATIVE),"-m","pytest","-q","test_eval_v2.py"]
    result=subprocess.run(command,cwd=study.ROOT,capture_output=True,text=True,timeout=60,env={**os.environ,"CUDA_VISIBLE_DEVICES":""})
    study.write_x(study.ROOT/"CPU_TESTS_V2.json",{"command":command,"returncode":result.returncode,"stdout":result.stdout,"stderr":result.stderr})
    if result.returncode: raise ValueError("V2 scorer tests failed")
    additions=[study.ROOT/name for name in ("owner_v2.py","test_eval_v2.py","seal_v2.py","CPU_TESTS_V2.json")]
    for arm in study.ARMS:
        old_path=study.ready_path(arm);old=study.read(old_path);closure=dict(old["closure_sha256"])
        closure.update({str(path.resolve()):study.sha(path) for path in additions})
        command=[str(study.NATIVE),str(study.ROOT/"owner_v2.py"),"run","--arm",arm,"--outer-seconds",str(study.CAP)]
        ready={**old,"schema":"helper-agnews-heldout-eval-ready-v2","status":"CPU_READY_MAIN_REVIEW_REQUIRED" if arm!="ag_step4" else "CPU_READY_CONDITIONAL_EXACT_AG_STEP4","created_epoch":time.time(),"command":command,"scorer_contract":{"datasets":["ag_news"],"expected_calls":64,"expected_records":256,"unavailable_denominator":256,"phantom_trec_slot":False,"claim_boundary":"prospectively selected balanced AG News train-split heldout256"},"supersedes_unlaunched_ready":str(old_path),"closure_sha256":closure,"cpu_tests_v2":{"path":str(study.ROOT/"CPU_TESTS_V2.json"),"sha256":study.sha(study.ROOT/"CPU_TESTS_V2.json")}}
        ready["identity"]=study.digest({"arm":arm,"command":command,"closure":closure,"scorer_contract":ready["scorer_contract"]})
        path=study.ROOT/("READY_"+arm.upper()+"_V2.json");study.write_x(path,ready)
        print(json.dumps({"arm":arm,"identity":ready["identity"],"ready_sha256":study.sha(path)},sort_keys=True))


if __name__=="__main__": main()
