"""Separate conditional protected72 readout for the exact post-window8 fixed-last policy."""
import argparse
import json
import os
import signal
import time
import traceback
from pathlib import Path

import continuation_owner as training
import continuation_study as study

collect, export = study.collect, study.export


def budget(start):
    return {"started": start, "work": start + 2400, "owned": start + 2670,
            "outer": start + 2700}


def planned_inventory(output):
    return [{"phase": "readout", "arm": "continuation_fixed_last",
             "capture_phase": "readout-rl_last", "coordinate": row,
             "export": str(Path(output) / "readout/export/EPISODES.json"),
             "reward": None, "available": False, "reason": "planned before service"}
            for row in study.source_study.read(study.SOURCE / "inputs/PLANS.json")["readout"]]


def collector_argv(stage, deadline):
    return [str(study.NATIVE), str(study.SOURCE / "terminal_collect.py"), "--spec",
            str(stage / "CAPTURE_SPEC.json"), "--output", str(stage / "rollout"),
            "--deadline", str(float(deadline))]


def execute(output):
    output = Path(output)
    if output.resolve() != study.READOUT_ATTEMPT.resolve():
        raise ValueError("exact readout-attempt-001 only")
    if output.exists():
        raise FileExistsError("readout attempt retained")
    campaign = study.verify_prepared()
    decision = study.final_policy()
    started = time.time()
    limits = budget(started)
    output.mkdir(parents=True)
    study.write(output / "PLANNED_NULL_ENDPOINTS.json", planned_inventory(output))
    if not decision["run"]:
        terminal = {"complete": False, "skipped": True, "reason": decision["reason"],
                    "physical_requests": 0, "planned": 72, "released": True,
                    "elapsed_seconds": time.time() - started}
        study.write(output / "SKIP.json", terminal)
        study.write(output / "OWNER_TERMINAL.json", terminal)
        return terminal
    if not os.environ.get("CUDA_VISIBLE_DEVICES") or "," in os.environ["CUDA_VISIBLE_DEVICES"]:
        raise ValueError("MAIN assigns exactly one GPU")
    suite = study.source_owner.dependencies()
    service = output / "service"
    service.mkdir()
    active, errors, result = True, [], None
    previous = signal.signal(signal.SIGALRM,
                             lambda *_: (_ for _ in ()).throw(TimeoutError("owned deadline")))
    try:
        startup = min(limits["work"], time.time() + 180)
        signal.setitimer(signal.ITIMER_REAL, max(.001, startup - time.time()))
        suite.start_service(service, collect.binding_for(decision["policy"]), startup)
        stage = output / "readout"
        stage.mkdir()
        deadline = limits["work"]
        signal.setitimer(signal.ITIMER_REAL, max(.001, deadline - time.time()))
        collect.prepare_spec("readout-rl_last", service / "BINDING.json",
                             service / "service/endpoint-original.json",
                             stage / "CAPTURE_SPEC.json", max(.001, deadline - time.time()), None)
        suite.command(service, "collect-continuation-fixed-last",
                      collector_argv(stage, deadline), max(.001, deadline - time.time()), deadline)
        result = export.export_attempt(stage / "rollout", stage / "export")
    except BaseException as error:
        errors.append({"type": type(error).__name__, "message": str(error),
                       "traceback": traceback.format_exc()})
    finally:
        signal.setitimer(signal.ITIMER_REAL,
                         max(.001, min(limits["owned"], time.time() + 90) - time.time()))
        try:
            suite.release_service(service)
            active = False
        except BaseException as error:
            errors.append({"type": type(error).__name__, "message": str(error),
                           "release_failed": True})
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)
    terminal = {"complete": not errors and bool(result and result["complete"]),
                "skipped": False, "errors": errors, "policy": decision["policy"],
                "continuation_owner_terminal_sha256": decision["owner_terminal_sha256"],
                "result": result, "planned": 72, "released": not active,
                "elapsed_seconds": time.time() - started, "campaign": campaign["identity"]}
    study.write(output / "COST_LEDGER.json", training.cost_ledger(output))
    study.write(output / "OWNER_TERMINAL.json", terminal)
    return terminal


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--output", type=Path, default=study.READOUT_ATTEMPT)
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = parse_args()
    value = study.verify_prepared() if args.command == "verify" else execute(args.output)
    print(json.dumps(value, sort_keys=True, allow_nan=False))
    raise SystemExit(0 if args.command == "verify" or value.get("complete") or value.get("skipped") else 1)
