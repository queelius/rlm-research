"""CPU-only seal for the conditional AG four-step arm."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

import config


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def write_x(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("CPU-only seal requires CUDA hidden")
    ready_path = config.ROOT / "READY.json"
    if ready_path.exists():
        raise ValueError("preserve existing READY")
    command = [str(config.TRAIN_PYTHON), "-m", "pytest", "-q", "test_ag.py"]
    result = subprocess.run(
        command, cwd=config.ROOT, capture_output=True, text=True, timeout=180,
        env={**os.environ, "CUDA_VISIBLE_DEVICES": ""},
    )
    write_x(config.ROOT / "CPU_TESTS.json", {
        "command": command, "returncode": result.returncode,
        "stdout": result.stdout, "stderr": result.stderr,
    })
    if result.returncode:
        raise ValueError("focused AG tests failed")
    local = [
        config.ROOT / name for name in (
            "config.py", "ag_runtime.py", "prepare_inputs.py", "train_ag.py", "test_ag.py",
            "seal.py", "DESIGN.md", "EVALUATION_INTERFACE.md", "CPU_TESTS.json",
            "inputs/STEP_GROUPS.json", "inputs/TRAIN_GOLD.json", "inputs/BUILD_AUDIT.json",
        )
    ]
    frozen = config.SIDE / "helper-agnews-data-vs-mechanics-v1"
    sources = [
        frozen / "CPU_SELECTION_RECEIPT.json",
        frozen / "inputs/MANIFEST.json",
        frozen / "inputs/TRAIN_PUBLIC.json",
        frozen / "inputs/TRAIN_GOLD.json",
        frozen / "inputs/SELECTED_PROVENANCE.json",
        config.REFERENCE / "READY.json",
        config.REFERENCE / "core.py",
        config.REFERENCE / "rng_receipts.py",
        config.REFERENCE / "train_four.py",
        config.V1 / "train.py", config.V1 / "grammar_client.py", config.V1 / "grammar_worker.py",
        config.V2 / "runner.py",
        config.CHILD / "adapter_model.safetensors", config.CHILD / "adapter_config.json",
        config.CHILD / "state.json", config.SOURCE_BINDING,
        config.BASE / "local-research-manifest.json",
    ]
    reference_ready = json.loads((config.REFERENCE / "READY.json").read_text())
    for raw, expected in reference_ready["closure_sha256"].items():
        if sha(raw) != expected:
            raise ValueError("reference training closure changed: " + raw)
    closure = {str(path.resolve()): sha(path) for path in local + sources}
    closure.update(reference_ready["closure_sha256"])
    source_inventory = {
        "schema": "helper-agnews-fourstep-source-inventory-v1",
        "frozen_training_records": 128,
        "steps": 4,
        "groups_per_step": 32,
        "actions_per_group": 4,
        "training_gold_prompted": False,
        "evaluation_inventory_loaded": False,
        "reference_ready_identity": reference_ready["identity"],
        "reference_ready_sha256": sha(config.REFERENCE / "READY.json"),
        "frozen_selection_manifest_sha256": sha(frozen / "inputs/MANIFEST.json"),
        "source_sha256": {str(path.resolve()): sha(path) for path in sources},
    }
    write_x(config.ROOT / "SOURCE_INVENTORY.json", source_inventory)
    closure[str((config.ROOT / "SOURCE_INVENTORY.json").resolve())] = sha(config.ROOT / "SOURCE_INVENTORY.json")
    identity = digest(closure)
    ready = {
        "schema": "helper-agnews-onpolicy-fourstep-ready-v1",
        "status": "CPU_READY_MAIN_REVIEW_REQUIRED_CONDITIONAL_ADMISSION",
        "identity": identity,
        "created_epoch": time.time(),
        "gpu_launched": False,
        "question": "Does broader AG News supervision at the matched four-update true-HF dose improve a prospectively frozen AG heldout panel?",
        "conditional_admission": "Only after current fast48/paired mechanics readouts; freshadaptive and root-recursion remain higher harness priorities.",
        "command": [str(config.TRAIN_PYTHON), str(config.ROOT / "train_ag.py"), "--output", str(config.ROOT / "outputs/attempt-001"), "--cap-seconds", str(config.CAP)],
        "owner_cap_seconds": config.CAP,
        "external_timeout_seconds": config.OUTER_CAP,
        "inventory": {"updates": 4, "groups_per_update": 32, "unique_training_records": 128, "fresh_actions_per_update": 128, "total_fresh_actions": 512},
        "policy": {"start": str(config.CHILD), "start_adapter_sha256": config.CHILD_SHA, "temperature": 1.0, "batch": 4, "lr": 1e-5, "weight_decay": 0, "clip": 1.0, "loss": "RLOO sequence-sum/128", "probability_gates": "unchanged from authenticated reference"},
        "prompt_schema": {"definitions": "standard AG News builder", "labels": list(config.AG_VALUES), "full_request_replaced": True, "host_gold_prompted": False},
        "checkpoint_policy": "commit each successful update; primary fixed checkpoint-0004; no selection",
        "timeout_policy": "Longer AG prompts may hit the explicit cap; preserve as failure, never truncate input or reduce dose.",
        "closure_sha256": closure,
        "cpu_tests": {"path": str(config.ROOT / "CPU_TESTS.json"), "sha256": sha(config.ROOT / "CPU_TESTS.json")},
        "launch_authority": "MAIN only under exclusive GPU ownership; READY is not automatic admission",
    }
    write_x(ready_path, ready)
    print(json.dumps({"identity": identity, "ready_sha256": sha(ready_path)}, sort_keys=True))


if __name__ == "__main__":
    main()
