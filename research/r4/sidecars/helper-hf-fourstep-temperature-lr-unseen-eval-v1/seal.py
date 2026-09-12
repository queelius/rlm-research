"""Seal two arm-specific, conditional step4 fixed-panel evaluators."""

import json
import os
from pathlib import Path
import subprocess
import time

import arm_eval_study as study


def main():
 if os.environ.get("CUDA_VISIBLE_DEVICES")!="":raise ValueError("CPU-only seal requires hidden GPU")
 if any((study.ROOT/name).exists() for name in ("READY_T2.json","READY_LR10X.json")):raise FileExistsError("eval READY exists")
 tests=subprocess.run([str(study.NATIVE),"-m","pytest","-q","test_eval.py"],cwd=study.ROOT,capture_output=True,text=True,timeout=60,env={**os.environ,"CUDA_VISIBLE_DEVICES":""});study.write_x(study.ROOT/"CPU_TESTS.json",{"returncode":tests.returncode,"stdout":tests.stdout,"stderr":tests.stderr})
 if tests.returncode:raise ValueError("focused tests failed")
 c32=study.read(study.C32/"READY.json")
 for name,arm in study.ARMS.items():
  training_ready=study.read(study.TRAINING/arm["training_ready"]);closure=dict(training_ready["closure_sha256"])
  for path,expected in c32["closure_sha256"].items():
   if path in closure and closure[path]!=expected:raise ValueError("source closures disagree")
   closure[path]=expected
  files=list(study.ROOT.glob("*.py"))+[study.ROOT/"CPU_TESTS.json",study.TRAINING/arm["training_ready"],study.TRAINING/"EVALUATION_INTERFACE.md",study.SOURCE_EVAL/"fourstep_panel_study.py",study.C32/"READY.json"]
  closure.update({str(path):study.sha(path) for path in files})
  value={"schema":"helper-hf-fourstep-temperature-lr-unseen-eval-ready-v1","status":"CPU_READY_CONDITIONAL_ON_EXACT_ARM_COMPLETED_STEP4","created_epoch":time.time(),"closure_sha256":closure,"training_arm":study.experimental_arm(name),"training_ready_sha256":arm["training_ready_sha256"],"training_ready_identity":arm["training_ready_identity"],"training_output":str(arm["training_output"]),"evaluation_interface_sha256":study.sha(study.TRAINING/"EVALUATION_INTERFACE.md"),"fixed_primary_checkpoint_step":4,"selection":"step4 only; no evaluation-driven selection","source_c32_ready_identity":c32["identity"],"panel_manifest_identity":study.panel()[0]["manifest_identity"],"schedule_sha256":study.digest(study.schedule()),"command":[str(study.NATIVE),str(study.ROOT/"owner.py"),"run","--arm",name,"--outer-seconds","600"],"output":str(arm["attempt"]),"inner_cap_seconds":600,"external_timeout_seconds":700,"launch_authority":"MAIN only after exact arm training completion and clean GPU","inventory":{"physical_calls":64,"predictions":256,"trec_test":128,"ag_news_test":128,"batch_size":4,"root_calls":0,"training_updates":0},"policy":{"temperature":0,"request_bodies":"exact frozen c32 unseen schedule","ordered_schemas":True,"service":"fresh; only authenticated arm step4 child binding changes"},"eligibility":"Four valid arm-specific commits; exact arm temperature/LR/state/runtime receipt; complete fresh collection and replay gates; serialized cumulative Adam step4; root unchanged.","claim_boundary":"Adaptive reuse of fixed256; final step4 primary only; no pristine-generalization, root, or faithfulness claim.","cpu_tests":tests.stdout.strip()}
  value["identity"]=study.digest(value);study.write_x(study.ROOT/arm["ready"],value)
 print(json.dumps({name:{"path":str(study.ROOT/arm["ready"]),"sha256":study.sha(study.ROOT/arm["ready"]),"identity":study.read(study.ROOT/arm["ready"])["identity"]} for name,arm in study.ARMS.items()},sort_keys=True))


if __name__=="__main__":main()
