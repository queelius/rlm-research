"""Own one released-base service and the bounded MRCR calibration collector."""

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


def execute(output, outer_seconds):
    if output.resolve() != study.ATTEMPT.resolve() or output.exists():
        raise ValueError("exact unused attempt-001 required")
    if outer_seconds != OWNER_SECONDS: raise ValueError("exact 900-second owner cap required")
    ready = study.verify_ready(); gpu = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if not gpu or "," in gpu or not os.environ.get("STRICT_RLM_CALIBRATION_API_KEY"):
        raise ValueError("one exclusive GPU and inherited private credential required")
    started = time.time(); deadline = started + OWNER_SECONDS; work = deadline - 60
    output.mkdir(parents=True); stage = output / "owned-service"; stage.mkdir()
    study.write_x(output / "OWNER_RUN.json", {"started_epoch": started,
        "owner_seconds": OWNER_SECONDS, "science_seconds": SCIENCE_SECONDS,
        "ready_identity": ready["identity"], "planned_episodes": 32, "gpu": gpu,
        "optimizer_steps": 0, "no_retry": True})
    suite = None; released = False; errors = []
    previous = {sig: signal.signal(sig, lambda *_: (_ for _ in ()).throw(TimeoutError("owner signal")))
                for sig in (signal.SIGALRM, signal.SIGTERM, signal.SIGINT)}
    signal.setitimer(signal.ITIMER_REAL, OWNER_SECONDS - 15)
    try:
        suite = study.dependencies(); suite.start_service(stage, study.binding(), min(started + 240, work))
        endpoint = stage / "service/endpoint-original.json"
        science_deadline = min(work, time.time() + SCIENCE_SECONDS)
        argv = [str(study.NATIVE), str(study.ROOT / "collect.py"), "--spec", str(study.ROOT / "SPEC.json"),
            "--endpoint", str(endpoint), "--output", str(output / "science"),
            "--deadline", str(float(science_deadline))]
        suite.command(stage, "mrcr-root-calibration", argv,
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
        result_path = output / "science/RESULT.json"
        result = study.read(result_path) if result_path.exists() else None
        terminal = {"complete": not errors and released and bool(result and result.get("complete")),
            "released": released, "errors": errors or None, "result": str(result_path) if result else None,
            "recorded": result.get("recorded") if result else None,
            "future_root_rl_eligible": result.get("future_root_rl_gate", {}).get("eligible") if result else None,
            "elapsed_seconds": time.time()-started, "no_retry": True}
        path = output / "OWNER_TERMINAL.json"
        temporary = path.with_suffix(".tmp"); temporary.write_text(json.dumps(terminal, indent=2, sort_keys=True)+"\n")
        temporary.replace(path); signal.setitimer(signal.ITIMER_REAL, 0)
        for sig, handler in previous.items(): signal.signal(sig, handler)
    return terminal


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--output", type=Path, default=study.ATTEMPT)
    parser.add_argument("--outer-seconds", type=int, default=OWNER_SECONDS); args = parser.parse_args()
    if args.command == "verify": print(study.verify_ready()["identity"])
    else:
        result = execute(args.output, args.outer_seconds); print(json.dumps(result, sort_keys=True))
        raise SystemExit(0 if result["complete"] else 1)

