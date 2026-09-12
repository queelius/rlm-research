"""Authenticate fixed checkpoint4 and derive a mathematically zero base adapter."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import time

import study


TRAIN_READY_SHA = "b8cfa1a9112c9147b97802d6999d4b05e9e94ccf00bec0690224e9a54635acfb"
TRAIN_READY_IDENTITY = "f7311b709192290e6b311749fd105ae0fe52adffa4dccb7789e00cfb072e72f9"
ARTIFACTS = study.ROOT / "checkpoint-artifacts"
ZERO = ARTIFACTS / "base-zero-adapter"
RECEIPT = ARTIFACTS / "CHECKPOINT_READY.json"


def validate_result_header(result: dict, output: Path) -> None:
    checkpoint = Path(output) / "checkpoint-0004"
    if (
        result.get("status") != "COMPLETED_FOUR_UPDATES"
        or result.get("optimizer_steps") != 4
        or Path(result.get("primary_checkpoint", "")).resolve() != checkpoint.resolve()
        or Path(result.get("evaluation_binding", "")).resolve()
        != (checkpoint / "EVAL_BINDING.json").resolve()
        or len(result.get("step_commits") or []) != 4
    ):
        raise ValueError("evaluation requires fixed completed checkpoint-0004")


def validate_state_link(state: dict, step: int, previous: str | None) -> None:
    if state.get("step") != step or state.get("optimizer_steps") != step:
        raise ValueError("checkpoint state step differs")
    if state.get("previous_step_commit_sha256") != previous:
        raise ValueError("checkpoint previous commit link differs")


def validate_zero_adapter(directory: Path, receipt: dict) -> None:
    import torch
    from safetensors.torch import load_file

    directory = Path(directory)
    tensors = load_file(directory / "adapter_model.safetensors", device="cpu")
    if not tensors or not all("lora_" in name for name in tensors):
        raise ValueError("zero adapter has non-LoRA or empty tensor inventory")
    if any(torch.count_nonzero(value).item() for value in tensors.values()):
        raise ValueError("base transport adapter is not exactly zero")
    config = study.read(directory / "adapter_config.json")
    if config.get("bias") != "none" or float(config.get("lora_dropout", -1)) != 0.0:
        raise ValueError("zero adapter config could change base behavior")
    if (
        receipt.get("all_tensors_zero") is not True
        or receipt.get("tensors") != len(tensors)
        or receipt.get("adapter_model_sha256") != study.sha(directory / "adapter_model.safetensors")
        or receipt.get("adapter_config_sha256") != study.sha(directory / "adapter_config.json")
    ):
        raise ValueError("zero adapter receipt differs")


def materialize_zero_adapter(source: Path, destination: Path) -> dict:
    import torch
    from safetensors.torch import load_file, save_file

    source, destination = Path(source), Path(destination)
    if destination.exists():
        raise FileExistsError(destination)
    tensors = load_file(source / "adapter_model.safetensors", device="cpu")
    if not tensors or not all("lora_" in name for name in tensors):
        raise ValueError("checkpoint is not a pure LoRA adapter")
    destination.mkdir(parents=True)
    save_file({name: torch.zeros_like(value) for name, value in tensors.items()}, destination / "adapter_model.safetensors")
    shutil.copyfile(source / "adapter_config.json", destination / "adapter_config.json")
    value = {
        "schema": "openai-mrcr-procedural-sft-zero-base-adapter-v1",
        "source_adapter_sha256": study.sha(source / "adapter_model.safetensors"),
        "adapter_model_sha256": study.sha(destination / "adapter_model.safetensors"),
        "adapter_config_sha256": study.sha(destination / "adapter_config.json"),
        "tensors": len(tensors),
        "all_tensors_zero": True,
        "semantics": "zero LoRA transport; mathematically identical to released base weights",
    }
    validate_zero_adapter(destination, value)
    return value


def qualify_training(output=study.TRAIN_OUTPUT) -> dict:
    output = Path(output)
    ready_path = study.TRAINING / "READY_TRAINING.json"
    ready = study.read(ready_path)
    if study.sha(ready_path) != TRAIN_READY_SHA or ready.get("identity") != TRAIN_READY_IDENTITY:
        raise ValueError("sealed procedural training READY changed")
    for raw, expected in ready["closure_sha256"].items():
        if study.sha(Path(raw)) != expected:
            raise ValueError("procedural training closure changed: " + raw)
    training = study.load("procedural_sft_eval_training_contract", study.TRAINING / "training.py")
    result_path = output / "RESULT.json"
    result = study.read(result_path)
    validate_result_header(result, output)
    canonical = training.result_for(output)
    for key, value in canonical.items():
        if result.get(key) != value:
            raise ValueError("training RESULT differs from canonical commits: " + key)
    previous = None
    lineage = []
    for step in range(1, 5):
        directory = output / f"checkpoint-{step:04d}"
        state = study.read(directory / "state.json")
        validate_state_link(state, step, previous)
        commit_path = directory / "STEP_COMMIT.json"
        previous = study.sha(commit_path)
        lineage.append(
            {
                "step": step,
                "state_sha256": study.sha(directory / "state.json"),
                "commit_sha256": previous,
                "optimizer_sha256": study.sha(directory / "optimizer.pt"),
                "rng_sha256": study.sha(directory / "rng.pt"),
            }
        )
    checkpoint = output / "checkpoint-0004"
    binding = study.read(checkpoint / "EVAL_BINDING.json")
    if (
        binding.get("root_only_update") is not True
        or binding.get("step") != 4
        or binding.get("fixed_primary_step") != 4
        or binding.get("training_ready_identity") != ready["identity"]
        or binding.get("child", {}).get("adapter") is not None
        or binding.get("root", {}).get("adapter_model_sha256")
        != study.sha(checkpoint / "adapter_model.safetensors")
    ):
        raise ValueError("fixed root-only evaluation binding differs")
    return {
        "eligible": True,
        "training_ready_identity": ready["identity"],
        "training_result_sha256": study.sha(result_path),
        "checkpoint": str(checkpoint),
        "adapter_model_sha256": study.sha(checkpoint / "adapter_model.safetensors"),
        "adapter_config_sha256": study.sha(checkpoint / "adapter_config.json"),
        "lineage": lineage,
    }


def seal_checkpoint() -> dict:
    if RECEIPT.exists() or ARTIFACTS.exists():
        raise FileExistsError("checkpoint evaluation artifacts already exist")
    qualified = qualify_training()
    zero = materialize_zero_adapter(Path(qualified["checkpoint"]), ZERO)
    value = {
        "schema": "openai-mrcr-procedural-sft-evaluation-checkpoint-ready-v1",
        "created_epoch": time.time(),
        "training": qualified,
        "zero_adapter": {**zero, "path": str(ZERO)},
        "heldout_model_queries": 0,
        "fixed_primary_step": 4,
    }
    value["identity"] = study.digest(value)
    study.write_x(RECEIPT, value)
    return value


def verify_checkpoint() -> dict:
    value = study.read(RECEIPT)
    if value.get("identity") != study.digest({key: item for key, item in value.items() if key != "identity"}):
        raise ValueError("checkpoint evaluation receipt changed")
    if value.get("training") != qualify_training():
        raise ValueError("current training lineage differs from checkpoint receipt")
    validate_zero_adapter(ZERO, value["zero_adapter"])
    return value


def binding(arm: str) -> dict:
    receipt = verify_checkpoint()
    zero = receipt["zero_adapter"]
    models = {
        study.BASE_ALIAS: {
            "path": str(ZERO),
            "adapter_sha256": zero["adapter_model_sha256"],
            "config_sha256": zero["adapter_config_sha256"],
        }
    }
    root = study.BASE_ALIAS
    if arm == "checkpoint4":
        trained = receipt["training"]
        root = study.ADAPTED_ALIAS
        models[root] = {
            "path": trained["checkpoint"],
            "adapter_sha256": trained["adapter_model_sha256"],
            "config_sha256": trained["adapter_config_sha256"],
        }
    elif arm != "base":
        raise ValueError("arm must be base or checkpoint4")
    return {
        "schema": "openai-mrcr-procedural-sft-fixed-root-child-binding-v1",
        "models": models,
        "role_map": {"root": root, "children": [study.BASE_ALIAS]},
        "fixed_child": study.BASE_ALIAS,
        "selection_path": str(RECEIPT),
        "selection_sha256": study.sha(RECEIPT),
        "selection_semantics": "fixed checkpoint4; zero-LoRA released-base transport",
        "post_training_or_evaluation_checkpoint_selection": False,
    }
