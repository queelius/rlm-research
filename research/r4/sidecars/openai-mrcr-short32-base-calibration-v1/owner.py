"""Bounded GPU owner for the conditional short32 calibration."""

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
ATTEMPT = study.ATTEMPT
COLLECTOR = study.ROOT / "collect.py"
V7_ATTEMPT = study.V7 / "outputs/attempt-007"


def runtime_condition(attempt=V7_ATTEMPT):
    attempt = Path(attempt)
    terminal_path = attempt / "OWNER_TERMINAL.json"
    result_path = attempt / "science/RESULT.json"
    if not terminal_path.exists() or not result_path.exists():
        return {"qualified": False, "reason": "V7 terminal/result not yet present"}
    terminal = study.read(terminal_path)
    result = study.read(result_path)
    native_paths = sorted((attempt / "science/native-calls").glob("*-result.json"))
    native = [study.read(path) for path in native_paths]
    returned = sum(row.get("status") == "returned" for row in native)
    pending_turn_errors = sum(
        row.get("status") == "error"
        and (row.get("error") or {}).get("type") == "TypeError"
        and "PendingTurn" in (row.get("error") or {}).get("message", "")
        for row in native
    )
    if not native_paths:
        returned = int(result.get("native_result_files") or 0)
    qualified = bool(
        terminal.get("complete") is True
        and terminal.get("released") is True
        and not terminal.get("errors")
        and result.get("complete") is True
        and result.get("recorded") == 32
        and returned > 0
        and pending_turn_errors == 0
    )
    return {
        "qualified": qualified,
        "reason": None if qualified else "V7 did not complete a clean returned-native calibration",
        "observed_elapsed_seconds": terminal.get("elapsed_seconds"),
        "recorded": result.get("recorded"),
        "returned_native_responses": returned,
        "pending_turn_serialization_errors": pending_turn_errors,
        "terminal_sha256": study.sha(terminal_path),
        "result_sha256": study.sha(result_path),
    }


def verify():
    condition = runtime_condition()
    if not condition["qualified"]:
        raise ValueError("conditional V7 runtime prerequisite not met: " + str(condition))
    ready = study.read(study.ROOT / "READY.json")
    if ready["identity"] != study.digest(
        {key: value for key, value in ready.items() if key != "identity"}
    ):
        raise ValueError("READY identity changed")
    for path, expected in ready["closure_sha256"].items():
        if study.sha(path) != expected:
            raise ValueError("READY closure changed: " + path)
    if ready.get("v7_runtime_condition") != condition:
        raise ValueError("V7 runtime prerequisite receipt changed")
    return ready


def execute(output, outer_seconds):
    if output.resolve() != ATTEMPT.resolve() or output.exists():
        raise ValueError("exact unused additive attempt-001 required")
    if outer_seconds != OWNER_SECONDS:
        raise ValueError("exact 900-second owner cap required")
    ready = verify()
    gpu = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    if not gpu or "," in gpu or not os.environ.get("STRICT_RLM_CALIBRATION_API_KEY"):
        raise ValueError("one exclusive GPU and inherited private credential required")
    started = time.time()
    deadline = started + OWNER_SECONDS
    work = deadline - 60
    output.mkdir(parents=True)
    stage = output / "owned-service"
    stage.mkdir()
    study.write_x(
        output / "OWNER_RUN.json",
        {
            "started_epoch": started,
            "owner_seconds": OWNER_SECONDS,
            "science_seconds": SCIENCE_SECONDS,
            "ready_identity": ready["identity"],
            "planned_episodes": 32,
            "gpu": gpu,
            "optimizer_steps": 0,
            "collector_retries": 0,
            "harness_retries": 0,
            "max_completed_turns_cumulative_root_child_per_episode": 6,
            "wrapper_adds_no_model_attempts": True,
        },
    )
    suite = None
    released = False
    errors = []

    def stop(*_):
        raise TimeoutError("owner signal")

    previous = {
        sig: signal.signal(sig, stop) for sig in (signal.SIGALRM, signal.SIGTERM, signal.SIGINT)
    }
    signal.setitimer(signal.ITIMER_REAL, OWNER_SECONDS - 15)
    try:
        suite = study.dependencies()
        suite.start_service(stage, study.binding(), min(started + 240, work))
        endpoint = stage / "service/endpoint-original.json"
        science_deadline = min(work, time.time() + SCIENCE_SECONDS)
        argv = [
            str(study.NATIVE),
            str(COLLECTOR),
            "--spec",
            str(study.SPEC),
            "--endpoint",
            str(endpoint),
            "--output",
            str(output / "science"),
            "--deadline",
            str(float(science_deadline)),
        ]
        suite.command(
            stage,
            "openai-mrcr-short32-base-calibration",
            argv,
            min(SCIENCE_SECONDS, max(1, science_deadline - time.time())),
            science_deadline,
        )
    except BaseException as error:
        errors.append(
            {
                "type": type(error).__name__,
                "message": str(error),
                "traceback": traceback.format_exc(),
            }
        )
    finally:
        signal.setitimer(signal.ITIMER_REAL, max(1, deadline - time.time()))
        if suite is not None:
            try:
                suite.release_service(stage)
                released = True
            except BaseException as error:
                errors.append(
                    {"stage": "release", "type": type(error).__name__, "message": str(error)}
                )
        else:
            released = True
        result_path = output / "science/RESULT.json"
        result = study.read(result_path) if result_path.exists() else None
        terminal = {
            "complete": not errors and released and bool(result and result.get("complete")),
            "released": released,
            "errors": errors or None,
            "result": str(result_path) if result else None,
            "recorded": result.get("recorded") if result else None,
            "future_root_rl_eligible": result.get("future_root_rl_gate", {}).get("eligible")
            if result
            else None,
            "elapsed_seconds": time.time() - started,
            "optimizer_steps": 0,
            "no_retry": True,
        }
        path = output / "OWNER_TERMINAL.json"
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(terminal, indent=2, sort_keys=True) + "\n")
        temporary.replace(path)
        signal.setitimer(signal.ITIMER_REAL, 0)
        for sig, handler in previous.items():
            signal.signal(sig, handler)
    return terminal


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--output", type=Path, default=ATTEMPT)
    parser.add_argument("--outer-seconds", type=int, default=OWNER_SECONDS)
    args = parser.parse_args()
    if args.command == "verify":
        print(verify()["identity"])
    else:
        result = execute(args.output, args.outer_seconds)
        print(json.dumps(result, sort_keys=True))
        raise SystemExit(0 if result["complete"] else 1)
