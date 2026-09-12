"""Create launchable READY only after the actual V7 runtime condition is observed."""

import json
from pathlib import Path
import time

import owner
import study


def validate_runtime(condition):
    if not condition.get("qualified"):
        raise ValueError("V7 runtime is not qualified")
    elapsed = condition.get("observed_elapsed_seconds")
    if not isinstance(elapsed, (int, float)) or elapsed > study.SCIENCE_SECONDS:
        raise ValueError("actual V7 does not support the tentative 600-second science cap")
    if condition.get("recorded") != 32 or condition.get("returned_native_responses", 0) <= 0:
        raise ValueError("V7 actual inventory/returned-native evidence incomplete")
    if condition.get("pending_turn_serialization_errors") != 0:
        raise ValueError("V7 retains PendingTurn serialization failures")
    return {
        "caps_retained": True,
        "basis": "actual V7 completed32 runtime elapsed within the tentative science cap",
        "observed_elapsed_seconds": elapsed,
        "science_cap_seconds": study.SCIENCE_SECONDS,
        "owner_cap_seconds": study.OWNER_SECONDS,
        "external_cap_seconds": 1000,
    }


def main():
    conditional_path = study.ROOT / "CPU_READY_CONDITIONAL.json"
    ready_path = study.ROOT / "READY.json"
    if ready_path.exists():
        raise FileExistsError(ready_path)
    conditional = study.read(conditional_path)
    for path, expected in conditional["closure_sha256"].items():
        if study.sha(path) != expected:
            raise ValueError("conditional closure changed: " + path)
    condition = owner.runtime_condition()
    cap_basis = validate_runtime(condition)
    value = {
        "schema": "openai-mrcr-short32-base-calibration-ready-v1",
        "status": "READY_FOR_MAIN_GPU_LAUNCH",
        "created_epoch": time.time(),
        "conditional_ready_sha256": study.sha(conditional_path),
        "v7_runtime_condition": condition,
        "cap_basis": cap_basis,
        "fixed_argv": conditional["fixed_argv"],
        "external_cap_seconds": conditional["external_cap_seconds"],
        "planned_episodes": 32,
        "optimizer_steps": 0,
        "science": conditional["science"],
        "claim_boundary": conditional["claim_boundary"],
        "closure_sha256": conditional["closure_sha256"],
    }
    value["identity"] = study.digest(value)
    study.write_x(ready_path, value)
    print(json.dumps({"ready_sha256": study.sha(ready_path), "identity": value["identity"]}))


if __name__ == "__main__":
    main()
