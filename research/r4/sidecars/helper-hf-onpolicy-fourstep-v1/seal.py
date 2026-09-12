"""CPU qualification and exact closure for the approved training-only four-step pilot."""

import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

import core
from config import (
    BASE,
    BATCH,
    CAP,
    CHILD,
    CHILD_SHA,
    CLIP,
    DENOMINATOR,
    GLOBAL_SEED,
    GRAMMAR_PYTHON,
    GROUPS,
    LR,
    OUTER_CAP,
    PERMUTATION_SEED_BASE,
    ROOT,
    SAMPLER_SEED,
    SOURCE_BINDING,
    TRAIN_PYTHON,
    UPDATES,
    V1,
    V2,
)


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or sys.prefix != str(
        TRAIN_PYTHON.parent.parent
    ):
        raise ValueError("seal CPU-only using the pinned training environment")
    if (ROOT / "READY.json").exists():
        raise ValueError("preserve existing immutable READY")
    original = core.read(V1 / "READY.json")
    repair = core.read(V2 / "READY.json")
    expected = {**original["closure_sha256"], **repair["closure_sha256"]}
    if core.sha(CHILD / "adapter_model.safetensors") != CHILD_SHA:
        raise ValueError("original c32 weights changed")
    source_files = [
        V1 / name
        for name in (
            "train.py",
            "policy.py",
            "prepare.py",
            "settings.py",
            "grammar_client.py",
            "grammar_worker.py",
            "test_grammar.py",
            "inputs/GROUPS.json",
            "inputs/TRAIN_GOLD.json",
        )
    ] + [V2 / "runner.py", V2 / "CPU_TESTS.json"]
    source_pins = {}
    for path in source_files:
        if core.sha(path) != expected[str(path)]:
            raise ValueError("qualified source seam changed: " + str(path))
        source_pins[str(path)] = core.sha(path)
    groups = core.read(V1 / "inputs/GROUPS.json")
    gold = core.read(V1 / "inputs/TRAIN_GOLD.json")
    if len(groups) != 32 or len(gold) != 32 or {row["group_id"] for row in groups} != set(gold):
        raise ValueError("not the exact original32 training groups")
    if {row["context_id"] for row in groups} != {
        "question-sensitive-sft-train-05",
        "question-sensitive-sft-train-06",
    } or any(row["source_split"] != "train" for row in groups):
        raise ValueError("unexpected training context/split")
    core.write(ROOT / "inputs/GROUPS.json", groups)
    core.write(ROOT / "inputs/TRAIN_GOLD.json", gold)
    core.write(
        ROOT / "inputs/SOURCES.json",
        {
            "groups": 32,
            "gold_keys": 32,
            "source_inputs_sha256": {
                str(path): source_pins[str(path)]
                for path in source_files
                if path.parent.name == "inputs"
            },
            "training_inputs": ["GROUPS.json", "TRAIN_GOLD.json"],
            "evaluation_inventory_loaded": False,
            "training_selection": "same32; uniform seeded permutation",
            "source_exposure": "all32 previously consumed twice in original c32 helper SFT",
            "prior_policy": "original c32, not one-step HF-v2",
        },
    )
    command = [str(TRAIN_PYTHON), "-m", "pytest", "-q", "test_four.py"]
    start = time.monotonic()
    tests = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=180,
        env={**os.environ, "CUDA_VISIBLE_DEVICES": ""},
    )
    core.write(
        ROOT / "CPU_TESTS.json",
        {
            "command": command,
            "returncode": tests.returncode,
            "stdout": tests.stdout,
            "stderr": tests.stderr,
            "elapsed_seconds": time.monotonic() - start,
        },
    )
    if tests.returncode:
        raise ValueError("focused CPU qualification failed; no READY")
    if (
        core.v1.BATCH != BATCH
        or core.v1.SAMPLES != DENOMINATOR
        or core.v1.TEMPERATURE != 1.0
        or core.v1.MAX_NEW != 64
        or core.v1.TOKEN_TOLERANCE != 1e-5
    ):
        raise ValueError("qualified core constants differ from approved experiment")
    import peft.peft_model
    import torch.utils.checkpoint
    import transformers.modeling_layers
    from transformers.models.qwen3 import modeling_qwen3

    package_files = [
        Path(module.__file__)
        for module in (
            peft.peft_model,
            torch.utils.checkpoint,
            transformers.modeling_layers,
            modeling_qwen3,
        )
    ]
    model_manifest = core.read(BASE / "local-research-manifest.json")
    model_pins = {}
    for name, value in model_manifest["files"].items():
        path = BASE / name
        if core.sha(path) != value:
            raise ValueError("base revision asset changed: " + str(path))
        model_pins[str(path)] = value
    extra_paths = [
        CHILD / "adapter_model.safetensors",
        CHILD / "adapter_config.json",
        CHILD / "state.json",
        CHILD.parent / "INPUTS.json",
        SOURCE_BINDING,
        BASE / "local-research-manifest.json",
        TRAIN_PYTHON,
        GRAMMAR_PYTHON,
        TRAIN_PYTHON.parent.parent / "pyvenv.cfg",
        GRAMMAR_PYTHON.parent.parent / "pyvenv.cfg",
        TRAIN_PYTHON.parent.parent.parent / "uv.lock",
    ]
    manifest = {
        "schema": "helper-hf-fourstep-source-manifest-v1",
        "source_ready_identities": {str(V1): original["identity"], str(V2): repair["identity"]},
        "qualified_seams_sha256": source_pins,
        "runtime_package_source_sha256": {str(path): core.sha(path) for path in package_files},
        "model_revision_assets_sha256": model_pins,
        "source_model_environment_sha256": {str(path): core.sha(path) for path in extra_paths},
        "copied_training_inventory": str(ROOT / "inputs/SOURCES.json"),
        "evaluation_data_is_not_a_training_input": True,
    }
    core.write(ROOT / "SOURCE_MANIFEST.json", manifest)
    paths = list(ROOT.glob("*.py")) + list((ROOT / "inputs").glob("*.json"))
    paths += [
        ROOT / name
        for name in (
            "PLAN.md",
            "DESIGN.md",
            "EVALUATION_INTERFACE.md",
            "SOURCE_MANIFEST.json",
            "CPU_TESTS.json",
            "PREPARATION_REPORT.md",
        )
    ]
    closure = {str(path): core.sha(path) for path in paths}
    for category in (
        "qualified_seams_sha256",
        "runtime_package_source_sha256",
        "model_revision_assets_sha256",
        "source_model_environment_sha256",
    ):
        closure.update(manifest[category])
    with core.v1.GrammarClient() as worker:
        grammar = worker.init(groups[0]["schema_ordered_json"])["versions"]
    environments = {
        "training": {
            "python": platform.python_version(),
            "executable": str(TRAIN_PYTHON),
            "prefix": sys.prefix,
            "cuda_build": torch.version.cuda,
            "packages": {
                name: importlib.metadata.version(name)
                for name in ("torch", "transformers", "peft", "numpy", "safetensors")
            },
        },
        "grammar": {
            "executable": str(GRAMMAR_PYTHON),
            "packages": grammar,
            "python": subprocess.check_output(
                [str(GRAMMAR_PYTHON), "-c", "import platform;print(platform.python_version())"],
                text=True,
            ).strip(),
            "cuda_visible_devices": "",
        },
        "uv": original["environments"]["uv"],
    }
    identity = hashlib.sha256(
        json.dumps(closure, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    ready = {
        "schema": "helper-hf-onpolicy-fourstep-ready-v1",
        "status": "CPU_READY_MAIN_REVIEW_REQUIRED",
        "identity": identity,
        "created_epoch": time.time(),
        "gpu_launched": False,
        "closure_sha256": closure,
        "source_manifest_sha256": core.sha(ROOT / "SOURCE_MANIFEST.json"),
        "environments": environments,
        "command": [
            str(TRAIN_PYTHON),
            str(ROOT / "train_four.py"),
            "--output",
            str(ROOT / "outputs/attempt-001"),
            "--cap-seconds",
            str(CAP),
        ],
        "owner_cap_seconds": CAP,
        "external_timeout_seconds": OUTER_CAP,
        "launch_authority": "MAIN only under shared GPU flock; readiness is not launch approval",
        "inventory": {
            "updates": UPDATES,
            "groups_per_update": GROUPS,
            "actions_per_group": BATCH,
            "fresh_actions_per_update": 128,
            "total_fresh_actions": 512,
            "unique_training_records": 32,
            "evaluation_records_in_training": 0,
        },
        "optimizer": {
            "fresh_at_start": True,
            "carried_across_updates": True,
            "kind": "AdamW",
            "lr": LR,
            "weight_decay": 0,
            "clip_norm": CLIP,
        },
        "policy": {
            "initial_adapter_sha256": CHILD_SHA,
            "temperature": 1,
            "attention": "eager",
            "batch_size": BATCH,
            "kv_cache": False,
            "full_prefix": True,
            "model_mode": "eval/dropoutoff",
            "base_dtype": "bfloat16",
            "lora_dtype": "float32",
            "activation_storage": "nonreentrant per-decoder checkpoint during grad replay",
        },
        "seeds": {
            "global": GLOBAL_SEED,
            "sampler": SAMPLER_SEED,
            "permutation_base_plus_step": PERMUTATION_SEED_BASE,
        },
        "gates": {
            "token_logprob": 1e-5,
            "sequence_logprob": 1e-4,
            "first4_full_support_logprob": 1e-5,
            "denominator": DENOMINATOR,
            "all_groups_required_before_step": True,
            "stop_on_zero_signal_or_failure": True,
        },
        "checkpoint_policy": {
            "save_each_step": True,
            "primary_step": 4,
            "selection_by_eval": False,
            "optional_fixed_curve": [1, 2, 4],
            "automatic_resume": False,
            "rng_saved_after_every_group": True,
        },
        "evaluation_interface": str(ROOT / "EVALUATION_INTERFACE.md"),
        "claim_boundary": "exploratory helper optimization; no accuracy or root-performance claim",
    }
    core.write(ROOT / "READY.json", ready)
    print(
        json.dumps(
            {
                "ready": str(ROOT / "READY.json"),
                "sha256": core.sha(ROOT / "READY.json"),
                "identity": identity,
                "pins": len(closure),
                "tests": tests.stdout.strip(),
            }
        )
    )


if __name__ == "__main__":
    main()
