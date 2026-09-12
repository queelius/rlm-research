"""Seal additive attempt-002 after native HTTP path qualification."""

from __future__ import annotations

import json
from pathlib import Path
import time

import checkpoint
import study_v2 as study


def inventory() -> list[Path]:
    local = [
        study.ROOT / name
        for name in (
            "QUESTION.md",
            "RUNBOOK.md",
            "REPAIR_V2.md",
            "study.py",
            "checkpoint.py",
            "collect.py",
            "owner.py",
            "READY.json",
            "study_v2.py",
            "collect_v2.py",
            "owner_v2.py",
            "prepare_v2.py",
            "test_repair_v2.py",
            "CPU_TESTS_V2.json",
        )
    ]
    source = [
        study.SOURCE_READY,
        study.SOURCE_SCREEN / "study.py",
        study.SOURCE_SCREEN / "checkpoint.py",
        study.SOURCE_SCREEN / "collect.py",
        study.SOURCE_SCREEN / "owner.py",
        study.SOURCE_EVAL / "collect.py",
        study.SOURCE_EVAL / "study.py",
        study.CHECKPOINT_EVAL / "checkpoint.py",
        study.CHECKPOINT_EVAL / "checkpoint-artifacts/CHECKPOINT_READY.json",
        study.DATA / "MODEL_INPUTS_V2.json",
        study.DATA / "host/HOST_GOLD.json",
        study.SOURCE / "causal_map_v2.py",
        study.SOURCE / "classify_v2.py",
    ]
    hook = study.SIDE / "openai-mrcr-procedural-sft-terminal-strip-disabled-v1"
    source += [hook / "CPU_READY.json", hook / "CPU_TESTS.json", hook / "hooks.py"]
    return local + source + sorted(path for path in study.INPUTS.rglob("*") if path.is_file())


def build() -> dict:
    if study.READY.exists():
        raise FileExistsError("READY_V2 already exists")
    if not study.read(study.ROOT / "CPU_TESTS_V2.json").get("passed"):
        raise ValueError("native transport CPU tests did not pass")
    report = study.prepare_inputs()
    checkpoint_receipt = checkpoint.verify_checkpoint()
    contract = study.terminal_hooks().qualify()
    paths = inventory()
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError("V2 seal inventory missing: " + str(missing))
    value = {
        "schema": "openai-mrcr-procedural-sft32-onpolicy-t1-ready-v2",
        "created_epoch": time.time(),
        "question": "Does temperature 1.0 expose mixed raw-exact G4 rewards at fixed checkpoint32?",
        "phase": "train",
        "arm": "checkpoint32",
        "optimizer_steps": 0,
        "repair_only": {
            "predecessor_ready": str(study.ROOT / "READY.json"),
            "predecessor_ready_sha256": study.sha(study.ROOT / "READY.json"),
            "predecessor_output": str(study.ROOT / "outputs/attempt-001"),
            "predecessor_status": "infrastructure_failure_zero_provider_returns",
            "change": "derive exact proven T0.5 ModelContext then change only sampling.temperature",
            "exact_socket_cause_available": False,
            "scientific_inputs_changed": False,
        },
        "controlled_comparison": {
            "source_ready": str(study.SOURCE_READY),
            "source_ready_sha256": study.sha(study.SOURCE_READY),
            "source_temperature": 0.5,
            "treatment_temperature": 1.0,
            "same_requested_seed_integers": True,
            "not_a_new_seed_replication": True,
            "only_scientific_change": "sampling temperature 0.5 to 1.0",
        },
        "inputs": {
            "records": 8,
            "episodes": 32,
            "groups": 8,
            "group_size": 4,
            "schedule_sha256": report["schedule_sha256"],
            "selection": "first eight records in frozen MODEL_INPUTS_V2 train order",
            "seeds": [row["seed"] for row in study.schedule("train")],
            "gold_in_model_input": False,
        },
        "sampling": {
            "temperature": 1.0,
            "top_p": 1.0,
            "top_k": -1,
            "min_p": 0.0,
            "max_tokens_per_action": 2048,
            "max_total_root_child_turns": 6,
            "workers": 4,
        },
        "checkpoint": {
            "receipt": str(checkpoint.RECEIPT),
            "receipt_sha256": study.sha(checkpoint.RECEIPT),
            "receipt_identity": checkpoint_receipt["identity"],
            "fixed_primary_step": 32,
            "checkpoint_selection": False,
            "child": "fixed zero-LoRA released-base transport",
        },
        "terminal_condition": {
            "name": "terminal-strip-disabled",
            "contract": contract,
            "general_lossless_parser": False,
            "gold_dependent_repair": False,
        },
        "transport_fixture": {
            "receipt": str(study.ROOT / "CPU_TESTS_V2.json"),
            "receipt_sha256": study.sha(study.ROOT / "CPU_TESTS_V2.json"),
            "real_layers": [
                "frozen task",
                "environment run_slot",
                "interception server",
                "Qwen3 renderer",
                "TrainClient",
                "authenticated root-mounted native HTTP route",
            ],
            "provider": "CPU-local deterministic fixture; no model weights or GPU",
        },
        "metrics": {
            "primary": "complete mixed raw-exact G4 groups",
            "promotion_screen": "at least two complete mixed groups",
            "unavailable_not_wrong": True,
        },
        "caps_seconds": {"science": 900, "owner": 1100, "external": 1200},
        "output": str(study.ROOT / "outputs/attempt-002"),
        "model_queries_before_ready": 0,
        "auto_launch": False,
        "closure_sha256": {str(path): study.sha(path) for path in paths},
    }
    value["identity"] = study.digest(value)
    study.write_x(study.READY, value)
    return value


def verify() -> dict:
    value = study.read(study.READY)
    if value.get("identity") != study.digest(
        {key: item for key, item in value.items() if key != "identity"}
    ):
        raise ValueError("READY_V2 identity changed")
    for raw, expected in value["closure_sha256"].items():
        if study.sha(Path(raw)) != expected:
            raise ValueError("sealed V2 file changed: " + raw)
    checkpoint.verify_checkpoint()
    study.terminal_hooks()
    if study.digest(study.schedule("train")) != value["inputs"]["schedule_sha256"]:
        raise ValueError("V2 schedule changed")
    return value


if __name__ == "__main__":
    value = verify() if study.READY.exists() else build()
    print(json.dumps({"identity": value["identity"], "sha256": study.sha(study.READY)}, sort_keys=True))

