"""One exact update2 under the explicit post-diagnostic engineering policy."""
import argparse,json,os,signal,subprocess,time,traceback
from pathlib import Path
import recovery2_study as study
def budget(start):return {"started":start,"work":start+1800,"owned":start+2070,"outer":start+2100}
def training_argv(output,deadline):return [str(study.TRAIN),str(study.V1/"sparse_train.py"),"--group",str(study.GROUP),"--generation",str(study.GENERATION),"--checkpoint",str(study.CHECKPOINT),"--output",str(output/"training"),"--deadline",str(float(deadline))]
def checkpoint2(output):
    checkpoint=output/"training/checkpoint-2";state=study.read(checkpoint/"state.json")
    if state["optimizer_steps"]!=2 or state["generation"]!=study.read(study.GENERATION):raise ValueError("update2 lineage")
    if tuple(state["metrics"][k] for k in ("episodes","root_turns","root_action_tokens"))!=(11,154,18517):raise ValueError("group metrics")
    for name,pin in state["files_sha256"].items():study.check(checkpoint/name,pin)
    result=study.read(output/"training/RESULT.json")
    if result["optimizer_steps"]!=2 or result["policy"]["state_sha256"]!=study.sha(checkpoint/"state.json"):raise ValueError("result policy")
    return result["policy"]
def execute(output):
    output=Path(output)
    if output.resolve()!=study.ATTEMPT.resolve():raise ValueError("exact attempt-001 only")
    if output.exists():raise FileExistsError("attempt retained")
    campaign=study.verify_prepared();study.verify_requalification()
    if not os.environ.get("CUDA_VISIBLE_DEVICES") or "," in os.environ["CUDA_VISIBLE_DEVICES"]:raise ValueError("MAIN assigns one GPU")
    output.mkdir(parents=True);started=time.time();limits=budget(started);argv=training_argv(output,limits["work"]);error=None;policy=None
    study.write(output/"OWNER_RUN.json",{"campaign_identity":campaign["identity"],"budget":limits,"optimizer_start":1,"target_optimizer_step":2,"qualification_rerun":False})
    with (output/"training.log").open("x") as log:
        process=subprocess.Popen(argv,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"})
        try:
            if process.wait(timeout=max(.001,limits["work"]-time.time())):raise RuntimeError("trainer failed")
            policy=checkpoint2(output)
        except BaseException as caught:
            error={"type":type(caught).__name__,"message":str(caught),"traceback":traceback.format_exc()}
            if process.poll() is None:os.killpg(process.pid,signal.SIGTERM);process.wait(timeout=30)
    terminal={"complete":error is None and policy is not None,"error":error,"policy":policy,"optimizer_start":1,"target_optimizer_step":2,"released":process.poll() is not None,"elapsed_seconds":time.time()-started};study.write(output/"OWNER_TERMINAL.json",terminal);return terminal
def parse_args(argv=None):
    p=argparse.ArgumentParser();p.add_argument("command",choices=("verify","run"));p.add_argument("--output",type=Path,default=study.ATTEMPT);return p.parse_args(argv)
if __name__=="__main__":
    a=parse_args();v=study.verify_prepared() if a.command=="verify" else execute(a.output);print(json.dumps(v,sort_keys=True));raise SystemExit(0 if a.command=="verify" or v["complete"] else 1)
