"""Seal collector-compatible V3 evaluator receipts; preserve all prior receipts."""

import copy,json,os,subprocess,time
import arm_eval_study as base


def main():
 if os.environ.get("CUDA_VISIBLE_DEVICES")!="":raise ValueError("CPU-only seal")
 outputs={"t2_lr1e5":"READY_T2_V3.json","t1_lr1e4":"READY_LR10X_V3.json"}
 if any((base.ROOT/x).exists() for x in outputs.values()):raise FileExistsError("V3 READY exists")
 tests=subprocess.run([str(base.NATIVE),"-m","pytest","-q","test_eval.py","test_eval_v2.py","test_eval_v3.py"],cwd=base.ROOT,capture_output=True,text=True,timeout=60,env={**os.environ,"CUDA_VISIBLE_DEVICES":""});base.write_x(base.ROOT/"CPU_TESTS_V3.json",{"returncode":tests.returncode,"stdout":tests.stdout,"stderr":tests.stderr})
 if tests.returncode:raise ValueError("tests failed")
 for name,filename in outputs.items():
  prior_name="READY_T2_V2.json" if name=="t2_lr1e5" else "READY_LR10X_V2.json";prior=base.ROOT/prior_name;value=copy.deepcopy(base.read(prior));value.pop("identity");value.update(schema="helper-hf-fourstep-temperature-lr-unseen-eval-ready-v3",created_epoch=time.time(),supersedes_unlaunched_ready=str(prior),supersedes_unlaunched_ready_sha256=base.sha(prior),command=[str(base.NATIVE),str(base.ROOT/"owner_v3.py"),"run","--arm",name,"--outer-seconds","600"],collector_verify_interface="zero-argument verify resolves the already selected sealed arm",cpu_tests=tests.stdout.strip())
  closure=dict(value["closure_sha256"]);paths=[prior,base.ROOT/"arm_eval_study_v3.py",base.ROOT/"owner_v3.py",base.ROOT/"test_eval_v3.py",base.ROOT/"CPU_TESTS_V3.json"]
  closure.update({str(p):base.sha(p) for p in paths});value["closure_sha256"]=closure;value["identity"]=base.digest(value);base.write_x(base.ROOT/filename,value)
 print(json.dumps({n:{"sha256":base.sha(base.ROOT/f),"identity":base.read(base.ROOT/f)["identity"]} for n,f in outputs.items()},sort_keys=True))


if __name__=="__main__":main()
