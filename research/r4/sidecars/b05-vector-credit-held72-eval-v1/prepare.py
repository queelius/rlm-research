"""Conditionally seal the frozen held72 readout after both fixed updates qualify."""
from datetime import datetime,timezone
import json,os,subprocess
from pathlib import Path
import study
def main():
    assert not study.READY.exists() and not study.ATTEMPT.exists()
    endpoints={"local":study.endpoint(study.LOCAL),"joint":study.endpoint(study.JOINT)}
    assert all(value["eligible"] and value["fixed_sole_step1"] for value in endpoints.values())
    binding=study.binding();study.write_x(study.ROOT/"BINDING.json",binding)
    closure={}
    for root in (study.LOCAL,study.JOINT):
        ready=study.read(root/"READY.json");closure.update(ready["closure_sha256"]);closure[str(root/"READY.json")]=study.sha(root/"READY.json")
        for path in (root/"outputs/attempt-001/OWNER_TERMINAL.json",root/"outputs/attempt-001/RESULT.json",root/"outputs/attempt-001/checkpoint-0001/STEP_COMMIT.json"):
            closure[str(path)]=study.sha(path)
        commit=study.read(root/"outputs/attempt-001/checkpoint-0001/STEP_COMMIT.json");closure.update(commit["artifacts_sha256"])
    for prior in (study.ROLLOUT/"CPU_READY.json",study.EVAL/"READY.json"):
        value=study.read(prior);closure.update(value["closure_sha256"]);closure[str(prior)]=study.sha(prior)
    for path in list(study.ROOT.glob("*.py"))+list(study.ROOT.glob("*.md"))+[study.INPUTS,study.HOST,study.ROOT/"BINDING.json"]:closure[str(path)]=study.sha(path)
    for path,want in closure.items():assert study.sha(path)==want,path
    ready={"schema":"b05-vector-credit-held72-ready-v1","status":"CPU_READY_MAIN_REVIEW_NOT_GPU_ADMITTED","created_utc":datetime.now(timezone.utc).isoformat(),
      "question":"held-only base versus candidate-local versus response-joint fixed step1","planned_calls":72,"context_units":12,"seeds_per_context":2,
      "arms":list(study.ARMS),"source_schedule_sha256":study.sha(study.INPUTS),"source_host_sha256":study.sha(study.HOST),
      "local_endpoint":endpoints["local"],"joint_endpoint":endpoints["joint"],"binding_sha256":study.sha(study.ROOT/"BINDING.json"),
      "temperature":0.5,"max_tokens":384,"max_model_len":8192,"science_seconds":600,"owner_seconds":700,"external_seconds":800,
      "no_training_context_calls":True,"no_checkpoint_or_arm_selection":True,"unknown_is_not_wrong":True,
      "argv":[str(study.NATIVE),str(study.ROOT/"owner.py"),"run","--outer-seconds","700"],"launch_authority":"MAIN only","closure_sha256":dict(sorted(closure.items()))}
    ready["identity"]=study.digest(ready);study.write_x(study.READY,ready)
    env=dict(os.environ);env["CUDA_VISIBLE_DEVICES"]="";env["STRICT_RLM_CALIBRATION_API_KEY"]="cpu-placeholder"
    command=[str(study.NATIVE),"-m","pytest","-q","-p","no:cacheprovider",str(study.ROOT/"test_eval.py")]
    result=subprocess.run(command,cwd=study.ROOT,env=env,capture_output=True,text=True)
    assert result.returncode==0,result.stdout+result.stderr
    receipt={"schema":"b05-vector-credit-held72-cpu-proof-v1","command":command,"returncode":result.returncode,"stdout":result.stdout,"stderr":result.stderr,
      "ready_sha256":study.sha(study.READY),"identity":ready["identity"],"both_checkpoint_qualifiers_passed":True,"GPU_calls":0,"model_calls":0}
    study.write_x(study.ROOT/"CPU_TESTS.json",receipt);print(json.dumps(receipt,indent=2))
if __name__=="__main__":main()
