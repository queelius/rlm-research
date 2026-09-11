"""One-GPU owner: two serial root services under one 3,570-second ownership clock."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import signal
import sys
import time
import traceback

sys.path.insert(0, str(Path(__file__).resolve().parent))
import study as s


POLICY_ORDER = ("sft6", "unchanged")
QUALIFIED_ROOT = s.QS
sys.path.insert(0, str(QUALIFIED_ROOT))
import qs_owner as qualified


def budget(started):
    return {
        "outer_deadline": started + 3600,
        "owned_deadline": started + 3570,
        "work_deadline": started + 3420,
    }


def clock_metadata(clocks):
    return {key + "_epoch": value for key, value in clocks.items()}


def error(caught):
    return {"type": type(caught).__name__, "message": str(caught), "traceback": traceback.format_exc()}


def inventory(output):
    return [
        {
            "policy": row["policy"],
            "harness_arm": row["harness_arm"],
            "coordinate_id": row["id"],
            "path": str(output / row["policy"] / "free" / row["id"] / "RESULT.json"),
            "recorded": False,
            "cause": "not_started_no_artifacts",
        }
        for row in s.read(s.ROOT / "inputs/FREE_PLAN.json")
    ]


def collector_argv(stage, arm, destination, deadline):
    return [
        str(s.NATIVE),
        str(s.ROOT / "collect.py"),
        "--mode",
        "free",
        "--plan",
        "FREE_PLAN_SFT6.json" if arm == "sft6" else "FREE_PLAN_UNCHANGED.json",
        "--start",
        "0",
        "--stop",
        "32",
        "--binding",
        str(stage / "BINDING.json"),
        "--endpoint",
        str(stage / "service/endpoint-original.json"),
        "--output",
        str(destination),
        "--deadline",
        str(float(deadline)),
    ]


def execute(output):
    output = Path(output)
    started = time.time()
    clocks = budget(started)
    if output.resolve() != s.ATTEMPT.resolve() or output.exists():
        raise ValueError("exact unused attempt namespace; no retry")
    ready = s.verify()
    s.runtime()
    gpu = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if not gpu or "," in gpu or not os.environ.get("STRICT_RLM_CALIBRATION_API_KEY"):
        raise ValueError("one assigned GPU and private credential required")
    output.mkdir(parents=True)
    suite = qualified.dependencies()
    planned = inventory(output)
    s.write(output / "PLANNED.json", planned)
    s.write(
        output / "OWNER_RUN.json",
        {
            "identity": ready["identity"],
            "started_epoch": started,
            **clock_metadata(clocks),
            "outer_seconds": 3600,
            "owned_seconds": 3570,
            "work_seconds": 3420,
            "policy_order": list(POLICY_ORDER),
            "service_architecture": "serial roots; harness arms interleaved within each policy plan",
            "planned": 64,
            "no_training": True,
            "no_retry": True,
            "gpu": gpu,
            "credential_present": True,
            "credential_value_logged": False,
        },
    )

    def expired(sig, frame):
        if sig in (signal.SIGINT, signal.SIGTERM):
            raise qualified.MainTermination("MAIN cancellation")
        raise TimeoutError("shared diagnostic cap")

    handlers = {
        sig: signal.signal(sig, expired) for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGALRM)
    }
    active = None
    errors = []
    stages = []
    terminate = False
    try:
        for index, arm in enumerate(POLICY_ORDER):
            if terminate:
                break
            stage = output / ("service-" + arm)
            stage.mkdir()
            active = stage
            stage_end = min(started + (index + 1) * 1710, clocks["work_deadline"])
            status = {"policy": arm, "started_epoch": time.time(), "deadline_epoch": stage_end}
            try:
                startup = min(time.time() + 180, stage_end - 90)
                qualified.alarm(startup)
                suite.start_service(stage, s.binding(arm), startup)
                collection_deadline = stage_end - 90
                qualified.alarm(collection_deadline)
                suite.command(
                    stage,
                    "readout32",
                    collector_argv(stage, arm, output / arm / "free", collection_deadline),
                    qualified.remaining(collection_deadline),
                    collection_deadline,
                )
                status["work_complete"] = True
            except BaseException as caught:
                status["error"] = error(caught)
                errors.append({"stage": arm, **status["error"]})
                if not isinstance(caught, Exception):
                    terminate = True
            finally:
                qualified.alarm(min(clocks["owned_deadline"], stage_end))
                try:
                    suite.release_service(stage)
                    active = None
                except BaseException as caught:
                    status["release_error"] = error(caught)
                    errors.append({"stage": arm, **status["release_error"]})
                    terminate = True
                status["ended_epoch"] = time.time()
                s.write(stage / "PHASE_TERMINAL.json", status)
                stages.append(status)
    finally:
        qualified.alarm(clocks["owned_deadline"])
        rows = qualified.harvest(output, planned)
        s.write(output / "COST_LEDGER.json", qualified.ledger(output))
        terminal = {
            "identity": ready["identity"],
            "complete": not errors and all(row["recorded"] for row in rows),
            "released": active is None,
            "active_unreleased_service": str(active) if active else None,
            "error": errors or None,
            "stages": stages,
            "inventory": rows,
            "planned": 64,
            "elapsed_seconds": time.time() - started,
            "no_retry": True,
            "orchestrator_complete_not_native_availability": True,
        }
        s.write(output / "OWNER_TERMINAL.json", terminal)
        signal.setitimer(signal.ITIMER_REAL, 0)
        for sig, handler in handlers.items():
            signal.signal(sig, handler)
    return terminal


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--output", type=Path, default=s.ATTEMPT)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.command == "verify":
        print(s.verify()["identity"])
    else:
        result = execute(args.output)
        print({"complete": result["complete"], "released": result["released"]})
        raise SystemExit(0 if result["complete"] else 1)
