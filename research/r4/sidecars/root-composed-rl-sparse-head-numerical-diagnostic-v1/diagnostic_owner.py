import argparse,json,os,signal,subprocess,time,traceback
from pathlib import Path
import diagnostic_study as study
def budget(start):return {"started":start,"work":start+270,"owned":start+290,"outer":start+300}
def diagnostic_argv(output,deadline):return [str(study.TRAIN),str(study.ROOT/"diagnostic_run.py"),"--group",str(study.GROUP),"--generation",str(study.GENERATION),"--checkpoint",str(study.CHECKPOINT),"--output",str(output/"measurement"),"--deadline",str(float(deadline))]
def execute(output):
    output=Path(output)
    if output.resolve()!=study.ATTEMPT.resolve():raise ValueError("exact attempt-001 only")
    if output.exists():raise FileExistsError("attempt retained")
    campaign=study.verify_prepared()
    if not os.environ.get("CUDA_VISIBLE_DEVICES") or "," in os.environ["CUDA_VISIBLE_DEVICES"]:raise ValueError("MAIN assigns one GPU")
    output.mkdir(parents=True);(output/"measurement").mkdir();started=time.time();limits=budget(started);error=None
    argv=diagnostic_argv(output,limits["work"]);study.write(output/"COMMAND.json",{"argv":argv,"started_epoch":started,"deadline_epoch":limits["work"],"optimizer_authorized":False})
    with (output/"process.log").open("x") as log:
        process=subprocess.Popen(argv,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"})
        try:
            if process.wait(timeout=max(.001,limits["work"]-time.time())):raise RuntimeError("diagnostic subprocess failed")
        except BaseException as caught:
            error={"type":type(caught).__name__,"message":str(caught),"traceback":traceback.format_exc()}
            if process.poll() is None:os.killpg(process.pid,signal.SIGTERM);process.wait(timeout=20)
    terminal={"complete":error is None and (output/"measurement/RESULT.json").exists(),"error":error,"optimizer_steps":0,"released":process.poll() is not None,"elapsed_seconds":time.time()-started,"campaign_identity":campaign["identity"]};study.write(output/"OWNER_TERMINAL.json",terminal);return terminal
def parse_args(argv=None):
    p=argparse.ArgumentParser();p.add_argument("command",choices=("verify","run"));p.add_argument("--output",type=Path,default=study.ATTEMPT);return p.parse_args(argv)
if __name__=="__main__":
    a=parse_args();v=study.verify_prepared() if a.command=="verify" else execute(a.output);print(json.dumps(v,sort_keys=True));raise SystemExit(0 if a.command=="verify" or v["complete"] else 1)
