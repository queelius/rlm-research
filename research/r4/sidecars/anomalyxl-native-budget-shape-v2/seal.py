import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

import budget_study as m


def digest(value): return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",", ":")).encode()).hexdigest()
def write_x(path,value):
    with Path(path).open("x") as stream: stream.write(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+"\n")


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES")!="": raise ValueError("CPU-only seal requires CUDA hidden")
    if (m.ROOT/"READY.json").exists() or m.ATTEMPT.exists(): raise FileExistsError("READY/output exists")
    old=m.read(m.V1/"READY.json")
    for raw,expected in old["closure_sha256"].items():
        if m.sha(raw)!=expected: raise ValueError("V1 source closure changed: "+raw)
    command=[str(m.NATIVE),"-m","pytest","-q","test_budget_shape.py"]
    started=time.monotonic();done=subprocess.run(command,cwd=m.ROOT,capture_output=True,text=True,timeout=90,env={**os.environ,"CUDA_VISIBLE_DEVICES":""})
    write_x(m.ROOT/"CPU_TESTS.json",{"schema":"anomalyxl-budget-shape-cpu-tests-v2","command":command,"returncode":done.returncode,"stdout":done.stdout,"stderr":done.stderr,"elapsed_seconds":time.monotonic()-started,"equal_total_budget_and_uniform_deadline_tested":True,"actual_v1_owner_service_seam_bound":True,"80_call_admission_tested":True})
    if done.returncode: raise RuntimeError("focused tests failed")
    closure=dict(old["closure_sha256"])
    for path in [m.ROOT/"budget_study.py",m.ROOT/"owner.py",m.ROOT/"seal.py",m.ROOT/"test_budget_shape.py",m.ROOT/"V1_INTERPRETATION.md",m.ROOT/"CPU_TESTS.json",m.V1/"READY.json",m.V1/"mini.py",m.V1/"owner.py",m.V1/"native_service.py",m.V1/"outputs/attempt-001/RESULT.json",m.V1/"outputs/attempt-001/OWNER_TERMINAL.json",m.V1/"inputs/PANEL.json",m.V1/"inputs/HOST_GOLD.json"]: closure[str(path)]=m.sha(path)
    ready={"schema":"anomalyxl-native-budget-shape-ready-v2","status":"CPU_READY_MAIN_REVIEW_REQUIRED","created_epoch":time.time(),"gpu_launched":False,"question":"With the same 2048-token total and 90-second episode cap, does one wide inspection or three narrow inspection/repair turns yield valid Python finals and better official score?","source_v1":{"ready_identity":old["identity"],"ready_sha256":m.sha(m.V1/"READY.json"),"result_sha256":m.sha(m.V1/"outputs/attempt-001/RESULT.json"),"python_final_answers":0,"diagnosis":"8 first-turn 512-token mid-code truncations; 2 repair trajectories timed out after valid code turns"},"constants":{"same_exposed_cases":10,"arms":["direct","python_wide1","python_repair3"],"episodes":30,"temperature":0,"master_seed":202609121431,"aggregate_output_tokens_per_episode":2048,"episode_cap_seconds_all_arms":90,"wide1":{"inspection_turns":1,"max_tokens_each":1536,"minimum_final_tokens":512},"repair3":{"inspection_turns":3,"max_tokens_each":512,"minimum_final_tokens":512},"direct":{"max_tokens":2048},"parser_unchanged":True,"executor_unchanged":True,"scorer_unchanged":True,"no_answer_fallback":True},"schedule":m.schedule(),"inventory":{"maximum_research_calls":70,"engineering_calls":2,"direct_calls":10,"wide1_maximum_calls":20,"repair3_maximum_calls":40},"command":[str(m.NATIVE),str(m.ROOT/"owner.py"),"run","--outer-seconds","1800"],"owner_cap_seconds":1800,"external_cap_seconds":1900,"output":str(m.ATTEMPT),"closure_sha256":closure,"primary_metrics":["answered Python finals per10","strict whole JSON per10","official primary mean and paired deltas","protocol/length/timeout failures","actual calls/tokens/time by arm"],"decision":"Promote an allocation only as an interface qualifier if at least 8/10 Python episodes reach a valid final and it has no fewer valid finals than the other allocation. Score is secondary until final-answer coverage is adequate.","claim_boundary":"Same ten outcome-exposed cases. V2 isolates turn allocation only within the new uniform90/total2048 setting; it changes deadline and prompt from V1, is not a clean Python-vs-direct effect, and provides no generalization or RL claim.","launch_authority":"MAIN only under shared GPU flock; no retry or continuation"};ready["identity"]=digest(ready);write_x(m.ROOT/"READY.json",ready);print(json.dumps({"identity":ready["identity"],"ready_sha256":m.sha(m.ROOT/"READY.json"),"closure_files":len(closure)},sort_keys=True))


if __name__=="__main__": main()
