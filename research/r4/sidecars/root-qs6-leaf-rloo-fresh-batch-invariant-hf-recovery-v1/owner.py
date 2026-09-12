"""Bounded owner for HF-only scoring; starts no native service and performs no optimizer step."""

import argparse
import json
import os
import subprocess
import time

import study


def run(seconds):
    ready=study.verify()
    if seconds!=study.CAP:raise ValueError("exact 360-second cap required")
    if (study.ATTEMPT/"OWNER_RUN.json").exists() or (study.ATTEMPT/"RESULT.json").exists():raise FileExistsError("recovery already launched")
    if not os.environ.get("CUDA_VISIBLE_DEVICES") or "," in os.environ["CUDA_VISIBLE_DEVICES"]:raise ValueError("MAIN must assign one GPU")
    command=[str(study.TRAIN_PYTHON),str(study.ROOT/"score.py"),"--run"]
    study.write_x(study.ATTEMPT/"OWNER_RUN.json",{"started_epoch":time.time(),"cap_seconds":seconds,"ready_identity":ready["identity"],"command":command,"native_service_started":False,"optimizer_steps":0})
    started=time.time();completed=subprocess.run(command,capture_output=True,text=True,timeout=seconds-10,env=os.environ.copy())
    (study.ATTEMPT/"HF_SCORE.stdout.log").write_text(completed.stdout);(study.ATTEMPT/"HF_SCORE.stderr.log").write_text(completed.stderr)
    terminal={"complete":completed.returncode==0 and (study.ATTEMPT/"RESULT.json").exists(),"returncode":completed.returncode,"elapsed_seconds":time.time()-started,"optimizer_steps":0,"native_service_started":False,"source_v2_service_remained_released":True}
    study.write_x(study.ATTEMPT/"OWNER_TERMINAL.json",terminal);return terminal


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("command",choices=("verify","run"));parser.add_argument("--outer-seconds",type=int,default=study.CAP);args=parser.parse_args()
    if args.command=="verify":print(study.verify()["identity"])
    else:
        value=run(args.outer_seconds);print(json.dumps(value,sort_keys=True));raise SystemExit(0 if value["complete"] else 1)
