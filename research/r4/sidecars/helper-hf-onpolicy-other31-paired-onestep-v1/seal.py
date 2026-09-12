"""CPU-qualify and seal the paired RLOO versus other-31 one-step experiment."""

import os
import subprocess
import sys
import time

import source
import study


REFERENCE_READY_SHA256 = "1885e3c2b91acb51639aff88e39959dc06ee255662664f27e6b5e753a32d5289"
REFERENCE_READY_IDENTITY = "f0e01f9999652ada7ec1187a59b6efd2694fb89a0bd5d9d2b543d86009e13648"
APPROVED_PROPOSAL = (
    study.ROOT.parent.parent
    / "ideas/2026-09-12-other31-paired-single-step.md"
)


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or sys.prefix != str(
        study.TRAIN_PYTHON.parent.parent
    ):
        raise ValueError("seal CPU-only in the pinned training environment")
    if (study.ROOT / "READY.json").exists() or study.OUTPUT.exists():
        raise ValueError("preserve READY and require unused attempt-001")
    reference = study.read(study.REFERENCE / "READY.json")
    if (
        study.sha(study.REFERENCE / "READY.json") != REFERENCE_READY_SHA256
        or reference.get("identity") != REFERENCE_READY_IDENTITY
    ):
        raise ValueError("completed four-step source READY differs")
    for raw, expected in reference["closure_sha256"].items():
        if study.sha(raw) != expected:
            raise ValueError("recursive source closure changed: " + raw)
    implementation = source.load()
    if (
        implementation.GLOBAL_SEED != 202609120700
        or implementation.SAMPLER_SEED != 202609120701
        or implementation.PERMUTATION_SEED_BASE != 202609120800
        or implementation.UPDATES != 4
        or implementation.GROUPS != 32
        or implementation.BATCH != 4
        or implementation.DENOMINATOR != 128
        or implementation.LR != 1e-5
        or implementation.core.v1.TEMPERATURE != 1.0
        or implementation.core.v1.TOKEN_TOLERANCE != 1e-5
        or implementation.core.v1.probability_gate.__globals__["SEQUENCE_TOLERANCE"]
        != 1e-4
        or implementation.core.v1.SUPPORT_AUDIT_GROUPS != 4
    ):
        raise ValueError("proven source policy/objective/gates differ")
    groups_source = study.REFERENCE / "inputs/GROUPS.json"
    gold_source = study.REFERENCE / "inputs/TRAIN_GOLD.json"
    groups = study.read(groups_source)
    gold = study.read(gold_source)
    if (
        len(groups) != 32
        or len(gold) != 32
        or {row["group_id"] for row in groups} != set(gold)
        or any(row["source_split"] != "train" for row in groups)
    ):
        raise ValueError("exact 32-question training inventory differs")
    study.write(study.ROOT / "inputs/GROUPS.json", groups)
    study.write(study.ROOT / "inputs/TRAIN_GOLD.json", gold)
    study.write(
        study.ROOT / "inputs/SOURCES.json",
        {
            "schema": "helper-hf-other31-paired-training-inputs-v1",
            "groups": 32,
            "actions_per_group": 4,
            "source_split": "train",
            "contexts": sorted({row["context_id"] for row in groups}),
            "source_sha256": {
                str(groups_source): study.sha(groups_source),
                str(gold_source): study.sha(gold_source),
            },
            "fresh_actions": True,
            "evaluation_inventory_loaded": False,
            "same_actions_replayed_by_both_branches": True,
        },
    )
    command = [str(study.TRAIN_PYTHON), "-m", "pytest", "-q", "test_pair.py"]
    started = time.monotonic()
    completed = subprocess.run(
        command,
        cwd=study.ROOT,
        capture_output=True,
        text=True,
        timeout=180,
        env={**os.environ, "CUDA_VISIBLE_DEVICES": ""},
    )
    tests = {
        "schema": "helper-hf-other31-paired-cpu-tests-v1",
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "elapsed_seconds": time.monotonic() - started,
        "other31_exclusion_and_all_failure_math": True,
        "bit_identical_restore_and_fresh_adam": True,
        "actual_sealed_rollout_replay_and_denominator": True,
        "source_compatible_evaluator_handoff": True,
    }
    study.write(study.ROOT / "CPU_TESTS.json", tests)
    if completed.returncode:
        raise RuntimeError("focused paired CPU tests failed")
    own = [
        study.ROOT / name
        for name in (
            "study.py",
            "source.py",
            "pair_math.py",
            "train_pair.py",
            "eligibility.py",
            "test_pair.py",
            "seal.py",
            "CPU_TESTS.json",
            "EVALUATION_INTERFACE.md",
        )
    ] + sorted((study.ROOT / "inputs").glob("*.json"))
    direct_sources = [
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
        APPROVED_PROPOSAL,
    ]
    closure = dict(reference["closure_sha256"])
    closure.update({str(path): study.sha(path) for path in own + direct_sources})
    ready = {
        **study.plan(),
        "closure_sha256": closure,
        "source_reference": {
            "path": str(study.REFERENCE),
            "ready_identity": reference["identity"],
            "ready_sha256": study.sha(study.REFERENCE / "READY.json"),
            "recursive_closure_verified": True,
            "completed_result_sha256": study.sha(
                study.REFERENCE / "outputs/attempt-001/RESULT.json"
            ),
            "reference_is_implementation_source_not_parent_checkpoint": True,
        },
        "approved_proposal": {
            "path": str(APPROVED_PROPOSAL),
            "sha256": study.sha(APPROVED_PROPOSAL),
        },
        "evaluation_interface": str(study.ROOT / "EVALUATION_INTERFACE.md"),
        "claim_boundary": (
            "Other-question reward mean is a standard action-independent REINFORCE baseline, "
            "not a novel algorithm. This is one exploratory paired update on previously used "
            "training contexts; a fixed previously examined panel cannot establish pristine "
            "generalization or an independent training replication."
        ),
        "created_epoch": time.time(),
        "gpu_launched": False,
    }
    ready["identity"] = study.digest(ready)
    study.write(study.ROOT / "READY.json", ready)
    verified = study.verify()
    print(
        {
            "identity": verified["identity"],
            "sha256": study.sha(study.ROOT / "READY.json"),
            "tests": tests["stdout"].strip(),
        }
    )


if __name__ == "__main__":
    main()
