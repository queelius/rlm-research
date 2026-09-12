"""Seal the additive strict-outcome/exact-causal-mapping conditional campaign."""

import json
import os
from pathlib import Path
import subprocess
import time

import collect
import owner_v2
import study


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("CPU-only preparation requires CUDA hidden")
    destination = study.ROOT / "CPU_READY_CONDITIONAL_V2.json"
    if destination.exists() or (study.ROOT / "READY_V2.json").exists():
        raise FileExistsError("V2 receipt already exists")
    if owner_v2.ATTEMPT.exists():
        raise FileExistsError("attempt-002 must remain unused")
    if study.sha(study.ROOT / "CPU_READY_CONDITIONAL.json") != (
        "cfcfead1d224c5002bda33afbe0ca8aebb571e98d4c706e59a68817fbc180a51"
    ):
        raise ValueError("preserved V1 conditional receipt changed")
    child_smoke = study.read(study.ROOT / "CPU_CHILD_ROLE_SMOKE_V2.json")
    if not (
        child_smoke.get("passed") is True
        and child_smoke.get("provider_requests") == child_smoke.get("native_returned") == 4
        and child_smoke.get("native_mapping_complete") is True
        and child_smoke.get("root_actions") == child_smoke.get("child_actions") == 2
        and child_smoke.get("child_invocations") == 1
        and child_smoke.get("roles") == ["root", "child", "child", "root"]
        and child_smoke.get("official_reward") == 1.0
        and child_smoke.get("gpu_calls") == child_smoke.get("weighted_model_calls") == 0
    ):
        raise ValueError("actual two-root/two-child RLM graph smoke failed")
    suite = study.dependencies()
    dependency = {
        "module": suite.__name__,
        "path": str(Path(suite.__file__).resolve()),
        "interfaces": {
            name: callable(getattr(suite, name, None))
            for name in ("start_service", "release_service", "command")
        },
        "v7_recorder_path": str(Path(collect.v7_recorder().__file__).resolve()),
    }
    if not all(dependency["interfaces"].values()):
        raise ValueError("service dependency interface incomplete")
    command = [str(study.NATIVE), "-m", "pytest", "-q", "test_short32_v2.py"]
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
    files = [
        study.ROOT / name
        for name in (
            "study.py",
            "collect.py",
            "owner.py",
            "classify_v2.py",
            "causal_map_v2.py",
            "collect_v2.py",
            "owner_v2.py",
            "finalize_after_v7_v2.py",
            "prepare_v2.py",
            "test_short32_v2.py",
            "REVIEW_AMENDMENT_V2.json",
            "SPEC.json",
            "DESIGN.md",
            "DESIGN.json",
            "CPU_READY_CONDITIONAL.json",
            "CPU_CHILD_ROLE_SMOKE_V2.json",
            "cpu_child_smoke_v2.py",
            "cpu-child-smoke-v2/EPISODE.json",
            "cpu-child-smoke-v2/PROVIDER_REQUESTS.json",
            "inputs/tasks.json",
            "inputs/PUBLIC.json",
            "inputs/HOST_GOLD.json",
        )
    ]
    files += sorted((study.ROOT / "cpu-child-smoke-v2/native-calls").glob("*.json"))
    files += sorted((study.INPUTS / "contexts").glob("*.json"))
    files += [
        study.DATA / "DATA_READY_V2.json",
        study.DATA / "MODEL_INPUTS_V2.json",
        study.DATA / "official_score.py",
        study.V7 / "READY_V7.json",
        study.V7 / "collect_v7.py",
        Path(
            "/project/alex_phd/runs/rlm-research-r4/sidecars/"
            "root-operator-composition-transfer-v1/outputs/attempt-001/sft6/free/"
            "c91a2a543aa54382e8140e820f08a9fb83536517674befaede776655f3e45d4b/"
            "EPISODE.json"
        ),
    ]
    value = {
        "schema": "openai-mrcr-short32-base-calibration-cpu-ready-conditional-v2",
        "status": "CPU_READY_CONDITIONAL_ON_ACTUAL_V7_RUNTIME",
        "created_epoch": time.time(),
        "supersedes_launch_authority_of": "CPU_READY_CONDITIONAL.json",
        "data_ready_v2_sha256": study.sha(study.DATA / "DATA_READY_V2.json"),
        "parent_ready_v7_sha256": study.sha(study.V7 / "READY_V7.json"),
        "current_v7_runtime_condition": owner_v2.runtime_condition(),
        "fixed_argv": [
            str(study.NATIVE),
            str(study.ROOT / "owner_v2.py"),
            "run",
            "--output",
            str(owner_v2.ATTEMPT),
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
            "strict_model_zero_stop_allowlist": True,
            "exact_native_trace_bijection": True,
            "role_from_physical_branch_semantics": True,
        },
        "caps": {
            "science_seconds": 600,
            "owner_seconds": 900,
            "external_seconds": 1000,
            "status": "tentative_until_actual_V7_whole_owner_bound_is_within600",
            "timing_evidence": "whole-owner elapsed is conservative, not science interval",
        },
        "focused_tests": {
            "argv": command,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        },
        "dependency_qualification": dependency,
        "child_role_smoke_sha256": study.sha(study.ROOT / "CPU_CHILD_ROLE_SMOKE_V2.json"),
        "selected_record_ids": [row["id"] for row in study.selected()],
        "claim_boundary": (
            "Eight frozen train contexts only; heldout16 receive no model query and do not "
            "affect selection or gates. Delegation subgroup summaries are observational. "
            "The context is instructed read-only but filesystem immutability is not enforced."
        ),
        "closure_sha256": {str(path): study.sha(path) for path in files},
    }
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
