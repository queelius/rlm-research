import hashlib
import json
import os
from pathlib import Path
import subprocess
import time


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
V1 = SIDE / "root-qs6-leaf-rloo-fresh-batch-invariant-one-update-v1"
PYTHON = Path("/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python")
OUTPUT = ROOT / "outputs/attempt-001"


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(value): return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",", ":")).encode()).hexdigest()
def write_x(path,value):
    with Path(path).open("x") as stream: stream.write(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+"\n")


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "": raise ValueError("CPU-only seal requires CUDA hidden")
    if OUTPUT.exists() or (ROOT/"READY.json").exists(): raise FileExistsError("V2 output or READY exists")
    command=[str(PYTHON),"-m","pytest","-q","test_train_v2.py"]
    started=time.monotonic();done=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=90,env={**os.environ,"CUDA_VISIBLE_DEVICES":""})
    tests={"schema":"fresh48-one-update-v2-cpu-tests-v1","command":command,"returncode":done.returncode,"stdout":done.stdout,"stderr":done.stderr,"elapsed_seconds":time.monotonic()-started,"actual_numpy_seed_failure_and_repair_exercised":True,"v1_failure_preserved":True}
    write_x(ROOT/"CPU_TESTS.json",tests)
    if done.returncode: raise RuntimeError("focused tests failed")
    old=json.loads((V1/"READY.json").read_text());closure=dict(old["closure_sha256"])
    for path in [ROOT/"train.py",ROOT/"test_train_v2.py",ROOT/"seal.py",ROOT/"EVALUATION_INTERFACE.md",ROOT/"CPU_TESTS.json",V1/"READY.json",V1/"train.py",V1/"outputs/attempt-001/START.json",V1/"outputs/attempt-001/FAILURE.json",PYTHON]: closure[str(path)]=sha(path)
    ready={"schema":"qualified-fresh48-leaf-rloo-one-update-ready-v2","status":"CPU_READY_MAIN_REVIEW_REQUIRED","created_epoch":time.time(),"gpu_launched":False,"repair":{"root_cause":"V1 passed master seed 202609121401 to NumPy legacy RandomState, outside uint32 range","v1_ready_sha256":sha(V1/"READY.json"),"v1_failure_sha256":sha(V1/"outputs/attempt-001/FAILURE.json"),"v1_optimizer_steps":0,"only_behavioral_change":"np.random.seed uses master_seed modulo 2**32","rng_seeds":{"master":202609121401,"python":202609121401,"numpy_legacy":745658489,"torch":202609121401,"torch_cuda_all":202609121401}},"training":old["training"],"environment":old["environment"],"command":[str(PYTHON),str(ROOT/"train.py"),"--output",str(OUTPUT),"--cap-seconds","900"],"owner_cap_seconds":900,"external_cap_seconds":1000,"output":str(OUTPUT),"checkpoint":str(OUTPUT/"checkpoint-0001"),"evaluation_interface":str(ROOT/"EVALUATION_INTERFACE.md"),"closure_sha256":closure,"claim_boundary":old["claim_boundary"]+" Additive V2 repairs only NumPy legacy seed initialization; V1 failure remains immutable."}
    ready["identity"]=digest(ready);write_x(ROOT/"READY.json",ready)
    print(json.dumps({"identity":ready["identity"],"ready_sha256":sha(ROOT/"READY.json")},sort_keys=True))


if __name__=="__main__": main()
