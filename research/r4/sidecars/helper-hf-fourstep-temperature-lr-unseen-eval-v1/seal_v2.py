"""Additively seal corrected arm-root binding evaluators, preserving V1 receipts."""

import copy
import json
import os
import subprocess
import time

import arm_eval_study as base


def main():
 if os.environ.get("CUDA_VISIBLE_DEVICES")!="":raise ValueError("CPU-only seal requires hidden GPU")
 outputs={"t2_lr1e5":"READY_T2_V2.json","t1_lr1e4":"READY_LR10X_V2.json"}
 if any((base.ROOT/name).exists() for name in outputs.values()):raise FileExistsError("corrected READY exists")
 tests=subprocess.run([str(base.NATIVE),"-m","pytest","-q","test_eval.py","test_eval_v2.py"],cwd=base.ROOT,capture_output=True,text=True,timeout=60,env={**os.environ,"CUDA_VISIBLE_DEVICES":""});base.write_x(base.ROOT/"CPU_TESTS_V2.json",{"returncode":tests.returncode,"stdout":tests.stdout,"stderr":tests.stderr})
 if tests.returncode:raise ValueError("focused tests failed")
 for name,filename in outputs.items():
  prior_name="READY_T2.json" if name=="t2_lr1e5" else "READY_LR10X.json";prior_path=base.ROOT/prior_name;value=copy.deepcopy(base.read(prior_path));value.pop("identity");value.update(schema="helper-hf-fourstep-temperature-lr-unseen-eval-ready-v2",created_epoch=time.time(),supersedes_unlaunched_ready=str(prior_path),supersedes_unlaunched_ready_sha256=base.sha(prior_path),command=[str(base.NATIVE),str(base.ROOT/"owner_v2.py"),"run","--arm",name,"--outer-seconds","600"],binding_experiment="exact arm root name: "+base.ARMS[name]["training_output"].parents[1].name,eligibility=value["eligibility"]+" Binding experiment must equal the arm root, not the parent multi-arm study.",cpu_tests=tests.stdout.strip())
  closure=dict(value["closure_sha256"]);paths=[prior_path,base.ROOT/"arm_eval_study_v2.py",base.ROOT/"owner_v2.py",base.ROOT/"test_eval_v2.py",base.ROOT/"CPU_TESTS_V2.json"]
  closure.update({str(path):base.sha(path) for path in paths});value["closure_sha256"]=closure;value["identity"]=base.digest(value);base.write_x(base.ROOT/filename,value)
 print(json.dumps({name:{"path":str(base.ROOT/filename),"sha256":base.sha(base.ROOT/filename),"identity":base.read(base.ROOT/filename)["identity"]} for name,filename in outputs.items()},sort_keys=True))


if __name__=="__main__":main()
