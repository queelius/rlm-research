"""Seal the already-tested long-transfer evaluator without launching it."""

from __future__ import annotations

import json
from pathlib import Path
import time

import checkpoint
import study


def source_inventory() -> list[Path]:
    paths = [
        study.ROOT / name
        for name in (
            "DESIGN.md", "RUNBOOK.md", "study.py", "checkpoint.py", "collect.py",
            "owner.py", "prepare.py", "test_long_eval.py", "CPU_TESTS.json",
        )
    ]
    paths += [
        study.DATA / "DATA_READY.json",
        study.DATA / "MANIFEST.json",
        study.DATA / "MODEL_INPUTS.json",
        study.DATA / "host/HOST_GOLD.json",
        study.TERMINAL_HOOK / "CPU_READY.json",
        study.TERMINAL_HOOK / "CPU_TESTS.json",
        study.TERMINAL_HOOK / "hooks.py",
        study.CHECKPOINT_EVAL / "checkpoint-artifacts/CHECKPOINT_READY.json",
        study.CHECKPOINT_EVAL / "checkpoint.py",
        study.CHECKPOINT_EVAL / "study.py",
        study.SOURCE_EVAL / "collect.py",
        study.SOURCE_EVAL / "owner.py",
        study.SOURCE_EVAL / "study.py",
        study.SOURCE / "causal_map_v2.py",
        study.SOURCE / "classify_v2.py",
    ]
    paths += sorted(path for path in study.INPUTS.rglob("*") if path.is_file())
    return paths


def build() -> dict:
    if study.READY.exists():
        raise FileExistsError("READY already exists")
    report = study.prepare_inputs()
    checkpoint_receipt = checkpoint.verify_checkpoint()
    hooks = study.terminal_hooks()
    contract = hooks.qualify()
    paths = source_inventory()
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError("seal inventory missing: " + str(missing))
    value = {
        "schema": "openai-mrcr-long-transfer-evaluation-ready-v1",
        "created_epoch": time.time(),
        "question": "Does procedural SFT checkpoint32 transfer to fixed 16k-32k external MRCR contexts?",
        "claim_boundary": "same-task length transfer; not neural context extension or broad generalization",
        "arms": ["base", "checkpoint32"],
        "inputs": {
            "data_ready": str(study.DATA / "DATA_READY.json"),
            "data_ready_sha256": study.sha(study.DATA / "DATA_READY.json"),
            "data_ready_identity": "609dc317e86aa09e18e03a1b6d131c374db4b266ee0a7a18cce974e30029598a",
            "schedule_sha256": report["schedule_sha256"],
            "records": 16,
            "episodes_per_arm": 16,
            "seed_namespace": "202609210000+fixed-row-index",
            "gold_in_model_input": False,
        },
        "sampling": {
            "temperature": 0.5,
            "top_p": 1.0,
            "top_k": -1,
            "min_p": 0.0,
            "max_tokens_per_action": 2048,
            "max_total_root_child_turns": 6,
            "neural_prefix_token_limit": 8192,
        },
        "checkpoint": {
            "receipt": str(checkpoint.RECEIPT),
            "receipt_sha256": study.sha(checkpoint.RECEIPT),
            "receipt_identity": checkpoint_receipt["identity"],
            "fixed_primary_step": 32,
            "checkpoint_selection": False,
            "child": "fixed zero-LoRA released-base transport in both arms",
        },
        "terminal_condition": {
            "name": "terminal-strip-disabled",
            "hooks_sha256": study.sha(study.TERMINAL_HOOK / "hooks.py"),
            "ready_sha256": study.sha(study.TERMINAL_HOOK / "CPU_READY.json"),
            "ready_identity": "f09078f6e68626be5d861752b7dabc6174572ec5c19e51d87222402f1d2efd31",
            "general_lossless_parser": False,
            "gold_repair": False,
            "contract": contract,
        },
        "metrics": {
            "primary": "raw exact official answer bytes",
            "diagnostics": ["official MRCR rfind similarity", "normalized exact", "procedure/action/usage"],
            "unavailable_not_wrong": True,
        },
        "caps_seconds_per_arm": {"science": 900, "owner": 1100, "external": 1200},
        "optimizer_steps": 0,
        "model_queries_before_ready": 0,
        "auto_launch": False,
        "outputs": {
            "base": str(study.ROOT / "outputs/base-001"),
            "checkpoint32": str(study.ROOT / "outputs/checkpoint32-001"),
        },
        "closure_sha256": {str(path): study.sha(path) for path in paths},
    }
    value["identity"] = study.digest(value)
    study.write_x(study.READY, value)
    return value


def verify() -> dict:
    ready = study.read(study.READY)
    if ready.get("identity") != study.digest(
        {key: value for key, value in ready.items() if key != "identity"}
    ):
        raise ValueError("READY identity changed")
    for raw, expected in ready["closure_sha256"].items():
        if study.sha(Path(raw)) != expected:
            raise ValueError("sealed file changed: " + raw)
    checkpoint.verify_checkpoint()
    study.terminal_hooks()
    return ready


if __name__ == "__main__":
    value = verify() if study.READY.exists() else build()
    print(json.dumps({"identity": value["identity"], "sha256": study.sha(study.READY)}, sort_keys=True))
