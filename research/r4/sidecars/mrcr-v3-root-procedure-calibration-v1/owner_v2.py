"""Attempt-002 owner; only repair is the collector child PYTHONPATH boundary."""

import argparse
import json
import os
from pathlib import Path
import signal
import time
import traceback

import study


OWNER_SECONDS = study.OWNER_SECONDS
SCIENCE_SECONDS = study.SCIENCE_SECONDS
ATTEMPT = study.ROOT / "outputs/attempt-002"
COLLECTOR = study.ROOT / "collector_entry_v2.py"


def verify():
    study.verify_ready()
    ready = study.read(study.ROOT / "READY_V2.json")
    if ready["identity"] != study.digest({k: value for k, value in ready.items() if k != "identity"}):
        raise ValueError("READY_V2 identity changed")
    for path, expected in ready["closure_sha256"].items():
        if study.sha(path) != expected: raise ValueError("READY_V2 closure changed: " + path)
    return ready


def execute(output, outer_seconds):
    if output.resolve() != ATTEMPT.resolve() or output.exists():
        raise ValueError("exact unused additive attempt-002 required")
    if outer_seconds != OWNER_SECONDS: raise ValueError("exact 900-second owner cap required")
    ready = verify(); gpu = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if not gpu or "," in gpu or not os.environ.get("STRICT_RLM_CALIBRATION_API_KEY"):
        raise ValueError("one exclusive GPU and inherited private credential required")
    started = time.time(); deadline = started + OWNER_SECONDS; work = deadline - 60
    output.mkdir(parents=True); stage = output / "owned-service"; stage.mkdir()
    study.write_x(output / "OWNER_RUN.json", {"started_epoch": started,
        "owner_seconds": OWNER_SECONDS, "science_seconds": SCIENCE_SECONDS,
        "ready_identity": ready["identity"], "planned_episodes": 32, "gpu": gpu,
        "optimizer_steps": 0, "no_retry": True,
        "repair": "collector child exports sidecar PYTHONPATH for the context mount wrapper"})
    suite = None; released = False; errors = []
    def stop(*_): raise TimeoutError("owner signal")
    previous = {sig: signal.signal(sig, stop) for sig in (signal.SIGALRM, signal.SIGTERM, signal.SIGINT)}
    signal.setitimer(signal.ITIMER_REAL, OWNER_SECONDS - 15)
    try:
        suite = study.dependencies(); suite.start_service(stage, study.binding(), min(started + 240, work))
        endpoint = stage / "service/endpoint-original.json"; science_deadline = min(work, time.time()+SCIENCE_SECONDS)
        argv = [str(study.NATIVE), str(COLLECTOR), "--spec", str(study.ROOT / "SPEC.json"),
            "--endpoint", str(endpoint), "--output", str(output / "science"),
            "--deadline", str(float(science_deadline))]
        suite.command(stage, "mrcr-root-calibration-v2", argv,
            min(SCIENCE_SECONDS, max(1, science_deadline-time.time())), science_deadline)
    except BaseException as error:
        errors.append({"type": type(error).__name__, "message": str(error), "traceback": traceback.format_exc()})
    finally:
        signal.setitimer(signal.ITIMER_REAL, max(1, deadline-time.time()))
        if suite is not None:
            try: suite.release_service(stage); released = True
            except BaseException as error:
                errors.append({"stage": "release", "type": type(error).__name__, "message": str(error)})
        else: released = True
        result_path = output / "science/RESULT.json"; result = study.read(result_path) if result_path.exists() else None
        terminal = {"complete": not errors and released and bool(result and result.get("complete")),
            "released": released, "errors": errors or None, "result": str(result_path) if result else None,
            "recorded": result.get("recorded") if result else None,
            "future_root_rl_eligible": result.get("future_root_rl_gate", {}).get("eligible") if result else None,
            "elapsed_seconds": time.time()-started, "no_retry": True}
        path = output / "OWNER_TERMINAL.json"; temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(terminal, indent=2, sort_keys=True)+"\n"); temporary.replace(path)
        signal.setitimer(signal.ITIMER_REAL, 0)
        for sig, handler in previous.items(): signal.signal(sig, handler)
    return terminal


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--output", type=Path, default=ATTEMPT)
    parser.add_argument("--outer-seconds", type=int, default=OWNER_SECONDS); args = parser.parse_args()
    if args.command == "verify": print(verify()["identity"])
    else:
        result = execute(args.output, args.outer_seconds); print(json.dumps(result, sort_keys=True))
        raise SystemExit(0 if result["complete"] else 1)

