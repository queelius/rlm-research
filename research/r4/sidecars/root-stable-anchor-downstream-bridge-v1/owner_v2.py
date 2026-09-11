"""MAIN-only V2 owner; one service, minimum120 calls, 2400 seconds."""

import argparse
import os
from pathlib import Path
import signal
import time
import traceback

import study_v2 as s
old = s.load("downstream_v1_owner_explicit", s.ROOT / "owner.py",
    "72d84c66cb73687f57b48f991e02a22847d88499e8897b4bb3488c9eec328a52", {"study": __import__("study")})
qualified = old.qualified


def collector_argv(stage, output, deadline):
    return [str(s.NATIVE), str(s.ROOT / "collect_v2.py"), "--binding", str(stage / "BINDING.json"),
        "--endpoint", str(stage / "service/endpoint-original.json"), "--output", str(output), "--deadline", str(float(deadline))]


def execute(output):
    started = time.time(); work = started + 2250; owned = started + 2370
    if output.resolve() != s.ATTEMPT.resolve() or output.exists(): raise ValueError("exact unused V2 attempt")
    ready = s.verify(); gpu = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if not gpu or "," in gpu or not os.environ.get("STRICT_RLM_CALIBRATION_API_KEY"): raise ValueError("one MAIN GPU/private credential")
    output.mkdir(parents=True); stage = output / "service"; stage.mkdir(); active = True; errors = []
    s.write(output / "OWNER_RUN.json", {"identity": ready["identity"], "started_epoch": started,
        "work_deadline_epoch": work, "owned_deadline_epoch": owned, "outer_seconds": 2400,
        "planned_leaf": 24, "planned_root": 96, "leaf_model": s.BASE_ALIAS, "gpu": gpu, "no_retry": True})
    def stop(sig, frame): raise TimeoutError("V2 ownership deadline")
    handlers = {sig: signal.signal(sig, stop) for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGALRM)}; suite = qualified.dependencies()
    try:
        startup = min(started + 180, work - 90); qualified.alarm(startup); suite.start_service(stage, s.binding(), startup)
        deadline = work - 90; qualified.alarm(deadline); suite.command(stage, "bridge120",
            collector_argv(stage, output / "science", deadline), qualified.remaining(deadline), deadline)
    except BaseException as error:
        errors.append({"type": type(error).__name__, "message": str(error), "traceback": traceback.format_exc()})
    finally:
        qualified.alarm(min(owned, time.time() + 90))
        try: suite.release_service(stage); active = False
        except BaseException as error: errors.append({"release": type(error).__name__, "message": str(error)})
        status_path = output / "science/STATUS.json"; complete = not errors and status_path.exists() and s.read(status_path).get("complete") is True
        terminal = {"identity": ready["identity"], "complete": complete, "released": not active,
            "active_unreleased_service": str(stage) if active else None, "error": errors or None,
            "planned": 120, "elapsed_seconds": time.time() - started, "no_retry": True}
        s.write(output / "OWNER_TERMINAL.json", terminal); signal.setitimer(signal.ITIMER_REAL, 0)
        for sig, handler in handlers.items(): signal.signal(sig, handler)
    return terminal


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("verify", "run")); parser.add_argument("--output", type=Path, default=s.ATTEMPT); args = parser.parse_args()
    if args.command == "verify": print(s.verify()["identity"])
    else:
        result = execute(args.output); print(result); raise SystemExit(0 if result["complete"] else 1)
