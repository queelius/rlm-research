"""Attempt-003 owner using the unaliased, qualified source readout namespace."""
import argparse
import json
import os
import signal
import sys
import time
import traceback
from pathlib import Path

import readout_owner as prior
import readout_study_v5 as meta

sys.path.insert(0, str(meta.SOURCE))
import terminal_study as source_study  # noqa: E402
import terminal_common as common  # noqa: E402
import terminal_native as native  # noqa: E402
import terminal_collect as collect  # noqa: E402
import terminal_export as export  # noqa: E402
import terminal_owner as source_owner  # noqa: E402


def budget(start):
    return prior.budget(start)


def collector_argv(stage, deadline):
    return [str(meta.NATIVE), str(source_study.ROOT / "terminal_collect.py"),
            "--spec", str(stage / "CAPTURE_SPEC.json"), "--output", str(stage / "rollout"),
            "--deadline", str(float(deadline))]


def planned_inventory(output):
    return [{"phase": "readout", "arm": "checkpoint2", "capture_phase": "readout-rl_last",
             "coordinate": row, "export": str(Path(output) / "readout/export/EPISODES.json"),
             "reward": None, "available": False, "reason": "planned before service"}
            for row in source_study.read(source_study.ROOT / "inputs/PLANS.json")["readout"]]


def dependencies():
    return source_owner.dependencies()


def execute(output):
    output = Path(output)
    if output.resolve() != meta.ATTEMPT.resolve():
        raise ValueError("exact attempt-003 only")
    if output.exists():
        raise FileExistsError("attempt retained")
    campaign = meta.verify_prepared()
    decision = meta.checkpoint2_decision()
    started = time.time()
    limits = budget(started)
    output.mkdir(parents=True)
    meta.write(output / "PLANNED_NULL_ENDPOINTS.json", planned_inventory(output))
    if not decision["run"]:
        terminal = {"complete": False, "skipped": True, "reason": decision["reason"],
                    "planned": 72, "physical_requests": 0, "released": True,
                    "elapsed_seconds": time.time() - started}
        meta.write(output / "SKIP.json", terminal)
        meta.write(output / "OWNER_TERMINAL.json", terminal)
        return terminal
    if not os.environ.get("CUDA_VISIBLE_DEVICES") or "," in os.environ["CUDA_VISIBLE_DEVICES"]:
        raise ValueError("MAIN must assign exactly one GPU")
    suite = dependencies()
    service = output / "service"
    service.mkdir()
    active, errors, result = True, [], None
    previous = signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError("owned deadline")))
    try:
        startup = min(limits["work"], time.time() + 180)
        signal.setitimer(signal.ITIMER_REAL, max(.001, startup - time.time()))
        binding = collect.binding_for(decision["policy"])
        suite.start_service(service, binding, startup)
        stage = output / "readout"
        stage.mkdir()
        deadline = limits["work"]
        signal.setitimer(signal.ITIMER_REAL, max(.001, deadline - time.time()))
        collect.prepare_spec("readout-rl_last", service / "BINDING.json",
                             service / "service/endpoint-original.json",
                             stage / "CAPTURE_SPEC.json", max(.001, deadline - time.time()), None)
        suite.command(service, "collect-checkpoint2", collector_argv(stage, deadline),
                      max(.001, deadline - time.time()), deadline)
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
                "result": result, "planned": 72, "capture_phase": "readout-rl_last",
                "external_arm": "checkpoint2", "released": not active,
                "elapsed_seconds": time.time() - started, "campaign": campaign["identity"]}
    meta.write(output / "COST_LEDGER.json", prior.cost_ledger(output))
    meta.write(output / "OWNER_TERMINAL.json", terminal)
    return terminal


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--output", type=Path, default=meta.ATTEMPT)
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = parse_args()
    value = meta.verify_prepared() if args.command == "verify" else execute(args.output)
    print(json.dumps(value, sort_keys=True))
    raise SystemExit(0 if args.command == "verify" or value.get("complete") or value.get("skipped") else 1)
