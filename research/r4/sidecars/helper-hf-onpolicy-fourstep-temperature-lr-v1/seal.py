"""CPU-test and independently seal the approved temperature and learning-rate arms."""

import os
import subprocess
import sys
import time

import arm_runtime
import study


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or sys.prefix != str(
        study.TRAIN_PYTHON.parent.parent
    ):
        raise ValueError("seal CPU-only in the pinned training environment")
    reference_ready = study.read(study.REFERENCE / "READY.json")
    if study.sha(study.REFERENCE / "READY.json") != (
        "1885e3c2b91acb51639aff88e39959dc06ee255662664f27e6b5e753a32d5289"
    ) or reference_ready.get("identity") != (
        "f0e01f9999652ada7ec1187a59b6efd2694fb89a0bd5d9d2b543d86009e13648"
    ):
        raise ValueError("completed reference READY differs")
    for raw, expected in reference_ready["closure_sha256"].items():
        if study.sha(raw) != expected:
            raise ValueError("completed reference closure changed: " + raw)
    source = arm_runtime.load_source()
    if (
        source.GLOBAL_SEED != 202609120700
        or source.SAMPLER_SEED != 202609120701
        or source.PERMUTATION_SEED_BASE != 202609120800
        or source.UPDATES != 4
        or source.GROUPS != 32
        or source.BATCH != 4
        or source.DENOMINATOR != 128
        or source.core.v1.TOKEN_TOLERANCE != 1e-5
        or source.core.v1.probability_gate.__globals__["SEQUENCE_TOLERANCE"] != 1e-4
        or source.core.v1.SUPPORT_AUDIT_GROUPS != 4
    ):
        raise ValueError("reference seeds/objective/gates differ from approved arms")
    groups = study.read(study.REFERENCE / "inputs/GROUPS.json")
    gold = study.read(study.REFERENCE / "inputs/TRAIN_GOLD.json")
    if len(groups) != 32 or len(gold) != 32 or {row["group_id"] for row in groups} != set(gold):
        raise ValueError("reference training-only inventory differs")
    for arm in study.ARMS.values():
        if (arm["root"] / "READY.json").exists() or (arm["root"] / "outputs").exists():
            raise ValueError("arm READY/output already exists: " + arm["name"])
        study.write(arm["root"] / "inputs/GROUPS.json", groups)
        study.write(arm["root"] / "inputs/TRAIN_GOLD.json", gold)
        study.write(
            arm["root"] / "inputs/SOURCES.json",
            {
                "schema": "helper-hf-fourstep-arm-training-inputs-v1",
                "arm": arm["name"],
                "groups": 32,
                "source_split": "train",
                "contexts": sorted({row["context_id"] for row in groups}),
                "source_sha256": {
                    str(study.REFERENCE / "inputs/GROUPS.json"): study.sha(
                        study.REFERENCE / "inputs/GROUPS.json"
                    ),
                    str(study.REFERENCE / "inputs/TRAIN_GOLD.json"): study.sha(
                        study.REFERENCE / "inputs/TRAIN_GOLD.json"
                    ),
                },
                "evaluation_inventory_loaded": False,
                "historical_actions_reused": False,
            },
        )
    command = [str(study.TRAIN_PYTHON), "-m", "pytest", "-q", "test_arms.py"]
    started = time.monotonic()
    completed = subprocess.run(
        command,
        cwd=study.ROOT,
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "CUDA_VISIBLE_DEVICES": ""},
    )
    tests = {
        "schema": "helper-hf-fourstep-arm-cpu-tests-v1",
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "elapsed_seconds": time.monotonic() - started,
        "actual_sealed_rollout_and_replay_functions_exercised": True,
        "optimizer_lr_and_state_metadata_regression": True,
    }
    study.write(study.ROOT / "CPU_TESTS.json", tests)
    if completed.returncode:
        raise RuntimeError("focused arm tests failed")
    shared = [
        study.ROOT / name
        for name in (
            "study.py",
            "arm_runtime.py",
            "train_arm.py",
            "test_arms.py",
            "seal.py",
            "CPU_TESTS.json",
            "EVALUATION_INTERFACE.md",
        )
    ] + [
        study.REFERENCE / "READY.json",
        study.REFERENCE / "train_four.py",
        study.REFERENCE / "core.py",
        study.REFERENCE / "rng_receipts.py",
        study.HF_V2 / "runner.py",
        study.HF_V1 / "train.py",
        study.HF_V1 / "policy.py",
        study.HF_V1 / "grammar_client.py",
        study.HF_V1 / "grammar_worker.py",
        study.CHILD / "adapter_model.safetensors",
        study.CHILD / "adapter_config.json",
        study.BASE / "config.json",
        study.SOURCE_BINDING,
        study.TRAIN_PYTHON,
    ]
    for arm_name, arm in study.ARMS.items():
        arm_paths = shared + sorted((arm["root"] / "inputs").glob("*.json"))
        ready = {
            **study.plan(arm_name),
            "closure_sha256": {str(path): study.sha(path) for path in arm_paths},
            "source_reference": {
                "path": str(study.REFERENCE),
                "ready_identity": reference_ready["identity"],
                "ready_sha256": study.sha(study.REFERENCE / "READY.json"),
                "completed_result_sha256": study.sha(
                    study.REFERENCE / "outputs/attempt-001/RESULT.json"
                ),
                "reference_is_comparison_not_parent_checkpoint": True,
            },
            "evaluation_interface": str(study.ROOT / "EVALUATION_INTERFACE.md"),
            "claim_boundary": (
                "Exploratory paired perturbation on previously used train contexts and an "
                "adaptively reused fixed evaluation panel; not an independent training "
                "replication, full factorial, pristine generalization, or root-performance claim."
            ),
            "created_epoch": time.time(),
        }
        ready["identity"] = study.digest(ready)
        study.write(arm["root"] / "READY.json", ready)
        alias = "READY_T2.json" if arm_name == "t2_lr1e5" else "READY_LR10X.json"
        study.write(study.ROOT / alias, ready)
    print(
        {
            arm_name: {
                "identity": study.read(arm["root"] / "READY.json")["identity"],
                "sha256": study.sha(arm["root"] / "READY.json"),
            }
            for arm_name, arm in study.ARMS.items()
        }
    )


if __name__ == "__main__":
    main()
