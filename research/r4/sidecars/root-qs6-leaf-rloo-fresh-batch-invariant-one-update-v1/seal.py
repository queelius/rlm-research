"""CPU-test and seal the approved qualified fresh48 one-update job."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import time


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
TRAIN_PYTHON = Path(
    "/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/"
    "gpu/training/.venv/bin/python"
)
REC = SIDE / "root-qs6-leaf-rloo-fresh-batch-invariant-hf-recovery-v1"
REC_OUT = REC / "outputs/attempt-001"
V1 = SIDE / "root-qs6-leaf-rloo-onebatch-v1"
PROPOSAL = (
    SIDE.parent
    / "analyses/fresh-batch-invariant-one-update-proposal-2026-09-12"
)
SOURCE_BINDING = (
    SIDE / "root-qs6-feedback-diagnostic-v1/outputs/attempt-001/service/BINDING.json"
)
OUTPUT = ROOT / "outputs/attempt-001"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def write_x(path, value):
    text = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    with Path(path).open("x") as stream:
        stream.write(text)


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("seal must be CPU-only with CUDA_VISIBLE_DEVICES empty")
    if OUTPUT.exists() or (ROOT / "READY.json").exists():
        raise FileExistsError("READY or output already exists; refusing reseal")
    command = [str(TRAIN_PYTHON), "-m", "pytest", "-q", "test_train.py"]
    started = time.monotonic()
    completed = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "CUDA_VISIBLE_DEVICES": ""},
    )
    tests = {
        "schema": "qualified-fresh48-one-update-cpu-tests-v1",
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "elapsed_seconds": time.monotonic() - started,
        "actual_frozen_48_inventory_loaded": True,
        "objective_formula_and_detached_ratio_tested": True,
        "gradient_replay_failure_zero_optimizer_contract_tested": True,
        "checkpoint_output_path_contract_tested": True,
    }
    write_x(ROOT / "CPU_TESTS.json", tests)
    if completed.returncode:
        raise RuntimeError("focused CPU tests failed")

    dataset = json.loads(
        (REC_OUT / "qualification-inputs/DATASET.json").read_text()
    )
    child = Path(dataset["model"]["child_start"])
    base = Path(dataset["model"]["base"])
    paths = [
        ROOT / name
        for name in (
            "train.py",
            "test_train.py",
            "seal.py",
            "EVALUATION_INTERFACE.md",
            "CPU_TESTS.json",
        )
    ] + [
        PROPOSAL / "PROPOSAL.md",
        PROPOSAL / "PROPOSAL.json",
        REC / "READY.json",
        REC_OUT / "RESULT.json",
        REC_OUT / "OWNER_TERMINAL.json",
        REC_OUT / "SOURCE_INVENTORY.json",
        REC_OUT / "COLLECTION.json",
        REC_OUT / "PRESTEP_QUALIFICATION.json",
        REC_OUT / "qualification-inputs/DATASET.json",
        REC_OUT / "qualification-inputs/MASKS.npz",
        REC_OUT / "qualification-inputs/MASK_MANIFEST.json",
        V1 / "train.py",
        V1 / "leaf_math.py",
        V1 / "prepare.py",
        SOURCE_BINDING,
        child / "adapter_model.safetensors",
        child / "adapter_config.json",
        base / "config.json",
        TRAIN_PYTHON,
    ]
    ready = {
        "schema": "qualified-fresh48-leaf-rloo-one-update-ready-v1",
        "status": "CPU_READY_MAIN_REVIEW_REQUIRED",
        "question": (
            "Does one exact qualified importance-weighted leaf RLOO update change the "
            "fixed native helper readout from the original c32 checkpoint?"
        ),
        "approved_proposal": {
            "path": str(PROPOSAL / "PROPOSAL.md"),
            "sha256": sha(PROPOSAL / "PROPOSAL.md"),
        },
        "training": {
            "starting_checkpoint": str(child),
            "episodes": 48,
            "groups": 2,
            "action_tokens": 11901,
            "saved_actions_reused": True,
            "new_collection": False,
            "all_failure_samples_preserved": True,
            "reward": "fraction-correct-times-16 RLOO within each 24-sample group",
            "sequence_reduction": "sum",
            "batch_denominator": 48,
            "importance_weights": "frozen exact raw sequence ratios, detached, unclipped, not self-normalized",
            "learning_rate": 1e-5,
            "weight_decay": 0,
            "gradient_clip_norm": 1.0,
            "seed": 202609121401,
            "optimizer": "fresh AdamW; exactly one permitted step",
            "gradient_replay_gate": {
                "must_precede_optimizer_step": True,
                "all_48_required": True,
                "token_tolerance": 1e-5,
                "sequence_tolerance": 1e-4,
                "failure_action": "persist all rows and stop with optimizer_steps=0; no retry",
            },
        },
        "environment": {
            "python_executable": str(TRAIN_PYTHON),
            "python": "3.12.12",
            "torch": "2.13.0+cu130",
            "transformers": "5.15.1",
            "peft": "0.20.0",
            "numpy": "2.5.2",
            "local_files_only": True,
        },
        "command": [
            str(TRAIN_PYTHON),
            str(ROOT / "train.py"),
            "--output",
            str(OUTPUT),
            "--cap-seconds",
            "900",
        ],
        "owner_cap_seconds": 900,
        "external_cap_seconds": 1000,
        "output": str(OUTPUT),
        "checkpoint": str(OUTPUT / "checkpoint-0001"),
        "evaluation_interface": str(ROOT / "EVALUATION_INTERFACE.md"),
        "evaluation_panel": str(
            SIDE / "helper-unseen-generalization-c32-baseline-v1"
        ),
        "claim_boundary": (
            "Exploratory offline one-step update on 48 previously sampled, never-updated c32 "
            "actions from two familiar training contexts. It is not a newly collected batch, "
            "not the 32-question HF-reference treatment, and its adaptively reused fixed256 "
            "readout is not pristine generalization."
        ),
        "closure_sha256": {str(path): sha(path) for path in paths},
        "created_epoch": time.time(),
    }
    ready["identity"] = digest(ready)
    write_x(ROOT / "READY.json", ready)
    print(json.dumps({"identity": ready["identity"], "ready_sha256": sha(ROOT / "READY.json")}, sort_keys=True))


if __name__ == "__main__":
    main()
