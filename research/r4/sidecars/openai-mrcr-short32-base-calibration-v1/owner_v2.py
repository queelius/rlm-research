"""Additive attempt-002 owner for the strict outcome-stop taxonomy."""

import argparse
import json
from pathlib import Path

import owner as base
import study


ATTEMPT = study.ROOT / "outputs/attempt-002"
COLLECTOR = study.ROOT / "collect_v2.py"
OWNER_SECONDS = base.OWNER_SECONDS
SCIENCE_SECONDS = base.SCIENCE_SECONDS


def runtime_condition(attempt=base.V7_ATTEMPT):
    """Qualify V7 only from authentic raw status=returned evidence."""
    attempt = Path(attempt)
    terminal_path = attempt / "OWNER_TERMINAL.json"
    result_path = attempt / "science/RESULT.json"
    if not terminal_path.exists() or not result_path.exists():
        return {"qualified": False, "reason": "V7 terminal/result not yet present"}
    terminal = study.read(terminal_path)
    result = study.read(result_path)
    native_dir = attempt / "science/native-calls"
    starts = sorted(native_dir.glob("*-start.json"))
    result_paths = sorted(native_dir.glob("*-result.json"))
    native = [study.read(path) for path in result_paths]
    returned = sum(row.get("status") == "returned" for row in native)
    errors = sum(row.get("status") == "error" for row in native)
    other = len(native) - returned - errors
    start_indices = {path.name.removesuffix("-start.json") for path in starts}
    result_indices = {path.name.removesuffix("-result.json") for path in result_paths}
    orphan_starts = len(start_indices - result_indices)
    orphan_results = len(result_indices - start_indices)
    pending_turn_errors = sum(
        row.get("status") == "error"
        and (row.get("error") or {}).get("type") == "TypeError"
        and "PendingTurn" in (row.get("error") or {}).get("message", "")
        for row in native
    )
    qualified = bool(
        terminal.get("complete") is True
        and terminal.get("released") is True
        and not terminal.get("errors")
        and result.get("complete") is True
        and result.get("recorded") == 32
        and returned > 0
        and errors == 0
        and other == 0
        and orphan_starts == 0
        and orphan_results == 0
        and pending_turn_errors == 0
    )
    return {
        "qualified": qualified,
        "reason": None if qualified else "V7 did not complete a clean returned-native calibration",
        "observed_elapsed_seconds": terminal.get("elapsed_seconds"),
        "elapsed_bound_kind": "whole_owner_conservative_bound_not_science_interval",
        "recorded": result.get("recorded"),
        "native_start_files": len(starts),
        "native_result_files": len(result_paths),
        "returned_native_responses": returned,
        "native_error_results": errors,
        "native_other_results": other,
        "orphan_native_starts": orphan_starts,
        "orphan_native_results": orphan_results,
        "pending_turn_serialization_errors": pending_turn_errors,
        "terminal_sha256": study.sha(terminal_path),
        "result_sha256": study.sha(result_path),
    }


def verify():
    condition = runtime_condition()
    if not condition["qualified"]:
        raise ValueError("conditional V7 runtime prerequisite not met: " + str(condition))
    ready = study.read(study.ROOT / "READY_V2.json")
    if ready["identity"] != study.digest(
        {key: value for key, value in ready.items() if key != "identity"}
    ):
        raise ValueError("READY_V2 identity changed")
    for path, expected in ready["closure_sha256"].items():
        if study.sha(path) != expected:
            raise ValueError("READY_V2 closure changed: " + path)
    if ready.get("v7_runtime_condition") != condition:
        raise ValueError("V7 runtime condition receipt changed")
    return ready


def execute(output, outer_seconds):
    original = (base.ATTEMPT, base.COLLECTOR, base.verify)
    base.ATTEMPT, base.COLLECTOR, base.verify = ATTEMPT, COLLECTOR, verify
    try:
        return base.execute(output, outer_seconds)
    finally:
        base.ATTEMPT, base.COLLECTOR, base.verify = original


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
