"""Seal a conditional CPU-ready campaign; actual V7 runtime remains mandatory."""

import json
import os
from pathlib import Path
import subprocess
import time

import collect
import owner
import study


def receipt_value(test, dependency):
    return {
        "schema": "openai-mrcr-short32-base-calibration-cpu-ready-conditional-v1",
        "status": "CPU_READY_CONDITIONAL_ON_ACTUAL_V7_RUNTIME",
        "created_epoch": time.time(),
        "data_ready_v2_sha256": study.sha(study.DATA / "DATA_READY_V2.json"),
        "parent_ready_v7_sha256": study.sha(study.V7 / "READY_V7.json"),
        "current_v7_runtime_condition": owner.runtime_condition(),
        "fixed_argv": [
            str(study.NATIVE),
            str(study.ROOT / "owner.py"),
            "run",
            "--output",
            str(study.ATTEMPT),
            "--outer-seconds",
            "900",
        ],
        "external_cap_seconds": 1000,
        "science": {
            "selected_train_records": 8,
            "rollouts_per_record": 4,
            "planned_episodes": 32,
            "heldout_model_queries": 0,
            "temperature": 0.5,
            "max_tokens_per_call": 2048,
            "max_depth": 1,
            "max_completed_turns_cumulative_root_child": 6,
            "root_policy": study.MODEL_ALIAS,
            "child_policy": study.MODEL_ALIAS,
            "adapter": None,
            "collector_retries": 0,
            "harness_retries": 0,
            "optimizer_steps": 0,
        },
        "caps": {
            "science_seconds": 600,
            "owner_seconds": 900,
            "external_seconds": 1000,
            "status": "tentative_until_actual_V7_completes32_within_science_cap",
        },
        "focused_tests": test,
        "dependency_qualification": dependency,
        "claim_boundary": (
            "Eight frozen train contexts only; heldout16 receive no model query and do not affect "
            "selection or gates. Delegation subgroup summaries are observational, not causal."
        ),
    }


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("CPU-only preparation requires CUDA hidden")
    destination = study.ROOT / "CPU_READY_CONDITIONAL.json"
    if destination.exists() or (study.ROOT / "READY.json").exists():
        raise FileExistsError("conditional/final receipt already exists")
    if study.ATTEMPT.exists():
        raise FileExistsError("attempt-001 must remain unused")
    data = study.verify_data()
    if data.get("records") != {"train": 32, "heldout": 16}:
        raise ValueError("frozen DATA_READY_V2 inventory changed")
    prepared = study.prepare_inputs()
    if prepared["tasks"] != 32 or prepared["heldout_records_read"] != 0:
        raise ValueError("short32 prepared inventory changed")
    smoke = study.read(study.ROOT / "CPU_SMOKE.json")
    if not (
        smoke.get("passed") is True
        and smoke.get("native_returned") == smoke.get("provider_requests") == 2
        and smoke.get("native_mapping_complete") is True
        and smoke.get("second_pending_turn_prefix_nodes", 0) > 0
        and smoke.get("second_pending_turn_path_len", 0) > 0
        and smoke.get("successful_exact_context_json_read") is True
        and smoke.get("first_prompt_contains_host_answer") is False
        and smoke.get("official_reward") == 1.0
        and smoke.get("gpu_calls") == smoke.get("weighted_model_calls") == 0
    ):
        raise ValueError("actual short32 runtime/renderer/V7-recorder CPU smoke invalid")
    suite = study.dependencies()
    dependency = {
        "module": suite.__name__,
        "path": str(Path(suite.__file__).resolve()),
        "required_interfaces": {
            name: callable(getattr(suite, name, None))
            for name in ("start_service", "release_service", "command")
        },
        "v7_recorder_path": str(Path(collect.v7_recorder().__file__).resolve()),
    }
    if not all(dependency["required_interfaces"].values()):
        raise ValueError("service dependency interface incomplete")
    command = [str(study.NATIVE), "-m", "pytest", "-q", "test_short32.py"]
    result = subprocess.run(
        command,
        cwd=study.ROOT,
        env={**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if result.returncode:
        raise ValueError(result.stdout + result.stderr)
    test = {
        "argv": command,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
    files = [
        study.ROOT / name
        for name in (
            "study.py",
            "collect.py",
            "owner.py",
            "finalize_after_v7.py",
            "prepare.py",
            "test_short32.py",
            "DESIGN.md",
            "DESIGN.json",
            "SPEC.json",
            "CPU_SMOKE.json",
            "cpu_smoke.py",
            "inputs/tasks.json",
            "inputs/PUBLIC.json",
            "inputs/HOST_GOLD.json",
        )
    ]
    files += sorted((study.INPUTS / "contexts").glob("*.json"))
    files += [
        study.DATA / "DATA_READY_V2.json",
        study.DATA / "MODEL_INPUTS_V2.json",
        study.DATA / "official_score.py",
        study.V7 / "READY_V7.json",
        study.V7 / "collect_v7.py",
    ]
    value = receipt_value(test, dependency)
    value["cpu_smoke_sha256"] = study.sha(study.ROOT / "CPU_SMOKE.json")
    value["selected_record_ids"] = [row["id"] for row in study.selected()]
    value["closure_sha256"] = {str(path): study.sha(path) for path in files}
    value["identity"] = study.digest(value)
    study.write_x(destination, value)
    print(
        json.dumps(
            {
                "conditional_ready_sha256": study.sha(destination),
                "identity": value["identity"],
                "status": value["status"],
                "tests": result.stdout.strip(),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
