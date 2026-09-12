"""Seal additive V2 launch authority only after authentic V7 completion."""

import json
import time

import owner_v2
import study


def validate_runtime(condition):
    if not condition.get("qualified"):
        raise ValueError("V7 runtime is not qualified")
    elapsed = condition.get("observed_elapsed_seconds")
    if not isinstance(elapsed, (int, float)) or elapsed > study.SCIENCE_SECONDS:
        raise ValueError("whole-owner conservative bound exceeds the 600-second science cap")
    if condition.get("elapsed_bound_kind") != "whole_owner_conservative_bound_not_science_interval":
        raise ValueError("V7 timing evidence label changed")
    if condition.get("recorded") != 32 or condition.get("returned_native_responses", 0) <= 0:
        raise ValueError("V7 actual inventory/returned-native evidence incomplete")
    for key in (
        "native_error_results",
        "native_other_results",
        "orphan_native_starts",
        "orphan_native_results",
        "pending_turn_serialization_errors",
    ):
        if condition.get(key) != 0:
            raise ValueError(f"V7 native boundary is not clean: {key}")
    return {
        "caps_retained": True,
        "basis": (
            "actual V7 completed32 and its whole-owner elapsed (a conservative upper bound, "
            "not a measured science interval) was within 600 seconds"
        ),
        "whole_owner_conservative_bound_seconds": elapsed,
        "science_cap_seconds": study.SCIENCE_SECONDS,
        "owner_cap_seconds": study.OWNER_SECONDS,
        "external_cap_seconds": 1000,
    }


def main():
    conditional_path = study.ROOT / "CPU_READY_CONDITIONAL_V2.json"
    ready_path = study.ROOT / "READY_V2.json"
    if ready_path.exists():
        raise FileExistsError(ready_path)
    conditional = study.read(conditional_path)
    for path, expected in conditional["closure_sha256"].items():
        if study.sha(path) != expected:
            raise ValueError("V2 conditional closure changed: " + path)
    condition = owner_v2.runtime_condition()
    value = {
        "schema": "openai-mrcr-short32-base-calibration-ready-v2",
        "status": "READY_FOR_MAIN_GPU_LAUNCH",
        "created_epoch": time.time(),
        "conditional_ready_sha256": study.sha(conditional_path),
        "v7_runtime_condition": condition,
        "cap_basis": validate_runtime(condition),
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
