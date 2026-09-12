"""Run focused CPU tests and seal exact two-arm argv."""
import json,os,subprocess,time
from pathlib import Path
import study
def main():
    if (study.ROOT/"RUN_READY.json").exists():raise FileExistsError("RUN_READY exists")
    ready=study.read(study.READY)
    for p,h in ready["closure_sha256"].items():
        if study.sha(Path(p))!=h:raise ValueError("closure changed: "+p)
    cmd=[str(study.NATIVE),"-m","pytest","-q","-p","no:cacheprovider","test_eval.py"];started=time.time();run=subprocess.run(cmd,cwd=study.ROOT,capture_output=True,text=True,timeout=180,env={**os.environ,"CUDA_VISIBLE_DEVICES":""})
    tests={"schema":"openai-mrcr-fourneedle-ordinal-transfer-tests-v1","command":cmd,"returncode":run.returncode,"stdout":run.stdout,"stderr":run.stderr,"elapsed_seconds":time.time()-started,"GPU_calls":0,"model_queries":0};study.write_x(study.ROOT/"CPU_TESTS.json",tests)
    if run.returncode:raise RuntimeError(run.stdout+run.stderr)
    argv={stage:[str(study.NATIVE),str(study.ROOT/"owner.py"),"run","--stage",stage,"--output",str(study.ROOT/f"outputs/{stage}-001"),"--outer-seconds","700"] for stage in ("base","checkpoint32")}
    value={"schema":"openai-mrcr-fourneedle-ordinal-transfer-run-ready-v1","scientific_ready":str(study.READY),"scientific_ready_sha256":study.sha(study.READY),"scientific_identity":ready["identity"],"cpu_tests_sha256":study.sha(study.ROOT/"CPU_TESTS.json"),"fixed_argv":argv,"external_seconds_each":800,"sequential_arms":True,"auto_launch":False,"GPU_calls_before_ready":0};value["identity"]=study.digest(value);study.write_x(study.ROOT/"RUN_READY.json",value);print(json.dumps({"identity":value["identity"],"sha256":study.sha(study.ROOT/"RUN_READY.json"),"tests":run.stdout.strip()},sort_keys=True))
if __name__=="__main__":main()
