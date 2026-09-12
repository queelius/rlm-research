"""Seal the fixed cp32 on-policy G4 screen after CPU qualification."""

from __future__ import annotations

import json
from pathlib import Path
import time

import checkpoint
import study


def inventory() -> list[Path]:
    paths = [study.ROOT / name for name in (
        "QUESTION.md", "RUNBOOK.md", "study.py", "checkpoint.py", "collect.py", "owner.py",
        "prepare.py", "test_screen.py", "CPU_TESTS.json", "PREP_HOLD.json",
    )]
    paths += [
        study.DATA / "MODEL_INPUTS_V2.json", study.DATA / "host/HOST_GOLD.json",
        study.TERMINAL_HOOK / "CPU_READY.json", study.TERMINAL_HOOK / "CPU_TESTS.json",
        study.TERMINAL_HOOK / "hooks.py", study.CHECKPOINT_EVAL / "checkpoint.py",
        study.CHECKPOINT_EVAL / "checkpoint-artifacts/CHECKPOINT_READY.json",
        study.SOURCE_EVAL / "collect.py", study.SOURCE_EVAL / "study.py",
        study.SOURCE / "causal_map_v2.py", study.SOURCE / "classify_v2.py",
    ]
    paths += sorted(path for path in study.INPUTS.rglob("*") if path.is_file())
    return paths


def build() -> dict:
    if study.READY.exists():
        raise FileExistsError("CPU_READY already exists")
    report = study.prepare_inputs()
    checkpoint_receipt = checkpoint.verify_checkpoint()
    contract = study.terminal_hooks().qualify()
    paths = inventory()
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError("seal inventory missing: " + str(missing))
    value = {
        "schema": "openai-mrcr-procedural-sft32-onpolicy-screen-ready-v1",
        "created_epoch": time.time(),
        "question": "Does fixed procedural-SFT checkpoint32 yield mixed raw-exact G4 rewards?",
        "phase": "train", "arm": "checkpoint32", "optimizer_steps": 0,
        "inputs": {"records": 8, "episodes": 32, "groups": 8, "group_size": 4,
                   "schedule_sha256": report["schedule_sha256"],
                   "selection": "first eight records in frozen MODEL_INPUTS_V2 train order",
                   "seeds": [row["seed"] for row in study.schedule("train")],
                   "gold_in_model_input": False},
        "sampling": {"temperature": 0.5, "top_p": 1.0, "top_k": -1, "min_p": 0.0,
                     "max_tokens_per_action": 2048, "max_total_root_child_turns": 6},
        "checkpoint": {"receipt": str(checkpoint.RECEIPT),
                       "receipt_sha256": study.sha(checkpoint.RECEIPT),
                       "receipt_identity": checkpoint_receipt["identity"],
                       "fixed_primary_step": 32, "checkpoint_selection": False,
                       "child": "fixed zero-LoRA released-base transport"},
        "terminal_condition": {"name": "terminal-strip-disabled",
                               "hooks_sha256": study.sha(study.TERMINAL_HOOK / "hooks.py"),
                               "ready_sha256": study.sha(study.TERMINAL_HOOK / "CPU_READY.json"),
                               "ready_identity": "f09078f6e68626be5d861752b7dabc6174572ec5c19e51d87222402f1d2efd31",
                               "general_lossless_parser": False,
                               "gold_dependent_repair": False, "contract": contract},
        "metrics": {"primary": "raw exact", "diagnostics": ["official MRCR similarity",
                    "first program/stdout/terminal token transport", "mixed reward groups"],
                    "unavailable_not_wrong": True},
        "caps_seconds": {"science": 900, "owner": 1100, "external": 1200},
        "output": str(study.ROOT / "outputs/attempt-001"),
        "model_queries_before_ready": 0, "auto_launch": False,
        "closure_sha256": {str(path): study.sha(path) for path in paths},
    }
    value["identity"] = study.digest(value)
    study.write_x(study.READY, value)
    return value


def verify() -> dict:
    ready = study.read(study.READY)
    if ready.get("identity") != study.digest({key: value for key, value in ready.items() if key != "identity"}):
        raise ValueError("CPU_READY identity changed")
    for raw, expected in ready["closure_sha256"].items():
        if study.sha(Path(raw)) != expected:
            raise ValueError("sealed file changed: " + raw)
    checkpoint.verify_checkpoint()
    study.terminal_hooks()
    return ready


if __name__ == "__main__":
    value = verify() if study.READY.exists() else build()
    print(json.dumps({"identity": value["identity"], "sha256": study.sha(study.READY)}, sort_keys=True))
