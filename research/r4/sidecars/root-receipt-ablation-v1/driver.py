"""Bounded parent-invoked owned evaluation. No acceptance or automatic queue here."""
import argparse
import asyncio
import fcntl
import json
import os
import sys
import time
from pathlib import Path
import experiment as e
import results

saved=sys.modules.get("study")
sys.modules["study"]=e.old
sys.path.insert(0,str(e.PRIOR))
inherited=e.private("receipt_original_driver",e.PRIOR/"driver.py")
sys.path.insert(0,str(e.ROOT))
if saved is None:
    sys.modules.pop("study",None)
else:
    sys.modules["study"]=saved
inherited.s,inherited.analysis=e,results
c=e.c


async def collect(spec,output):
    previous=e.capture.base
    e.capture.base=e.collector()
    try:
        return await inherited.collect(spec,output)
    finally:
        e.capture.base=previous


def verify_ready():
    spec=e.verify()
    ready=c.read(e.ROOT/"READY.json")
    c.authenticate(ready["artifact_sha256"])
    if ready["spec_sha256"]!=c.file_hash(e.ROOT/"SPEC.json") or ready["planned"]!=72:
        raise ValueError("READY does not authenticate 72 frozen episodes")
    proof=c.read(e.ROOT/"qualification-map-attempt-001/RESULT.json")
    if proof["provider_calls"]!=9 or proof["actual_model_calls"]!=0 or proof["conditions"]!=list(e.ARMS):
        raise ValueError("CPU qualification missing")
    return spec


def run(output):
    started=time.time()
    deadline,work_deadline=started+2400,started+2280
    spec=verify_ready()
    gpu=os.environ.get("CUDA_VISIBLE_DEVICES","")
    if not gpu or "," in gpu or not os.environ.get("STRICT_RLM_CALIBRATION_API_KEY"):
        raise ValueError("main must assign exclusive GPU and existing credential")
    output=Path(output).resolve()
    output.mkdir(parents=True,exist_ok=False)
    c.write_once(output/"RUN.json",{"started_epoch":started,"deadline_epoch":deadline,"work_deadline_epoch":work_deadline,
        "spec_sha256":c.file_hash(e.ROOT/"SPEC.json"),"ready_sha256":c.file_hash(e.ROOT/"READY.json"),"gpu":gpu})
    life,coordinator=inherited.lifecycle,inherited.coordinator
    life.install()
    e.native.binding_for=e.binding_for
    error,status=None,None
    service_dir=output/"services/step8"
    try:
        binding,endpoint=coordinator.start_service(service_dir,spec["policy"],work_deadline)
        try:
            phase=output/"phase-step8"
            phase.mkdir()
            cap=min(2100,work_deadline-time.time()-30)
            if cap<=60:
                raise TimeoutError("no collection budget after startup")
            e.phase_spec(binding,endpoint,phase/"CAPTURE_SPEC.json",cap)
            command=[str(c.NATIVE_PYTHON),str(e.ROOT/"driver.py"),"collect","--spec",str(phase/"CAPTURE_SPEC.json"),"--output",str(phase/"rollout")]
            c.write_once(phase/"COLLECT_COMMAND.json",{"argv":command,"cap_seconds":cap,"collector_gpu_visible":False})
            coordinator.owned_command(command,phase/"collection.log",min(cap+30,work_deadline-time.time()))
            status=c.read(phase/"rollout/STATUS.json")
            if status["recorded"]!=72 or status["stop_reason"] is not None:
                raise RuntimeError("incomplete/capped evaluation retained without retry")
        finally:
            life.stop_service(service_dir/"service")
    except BaseException as caught:
        error={"type":type(caught).__name__,"message":str(caught)}
    terminal={"complete":error is None,"error":error,"status":status,"elapsed_seconds":time.time()-started,
        "deadline_epoch":deadline,"global_cap_overrun_seconds":max(0,time.time()-deadline),
        "owned_service_release_records":[str(p) for p in output.glob("services/*/SERVICE_STOPPED.json")],
        "cpu_analysis":"Run analyze separately after coordinator releases GPU authority."}
    c.write_once(output/"TERMINAL.json",terminal)
    return terminal


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("command",choices=("verify","collect","run","analyze"))
    parser.add_argument("--output",type=Path,default=e.ROOT/"outputs/attempt-001")
    parser.add_argument("--spec",type=Path)
    args=parser.parse_args()
    if args.command=="collect":
        raise SystemExit(asyncio.run(collect(args.spec,args.output)))
    if args.command=="run":
        with (e.ROOT/"COORDINATOR.lock").open("a") as lease:
            fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
            value=run(args.output)
        print(json.dumps(value,sort_keys=True))
        raise SystemExit(0 if value["complete"] else 1)
    value=verify_ready() if args.command=="verify" else results.analyze(args.output)
    print(json.dumps({"command":args.command,"gpu_calls":0,"planned":len(value.get("plan",[])) or value.get("planned")}))
