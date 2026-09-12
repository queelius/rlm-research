"""Authenticate the fixed one-update checkpoint and derive an exact-zero base adapter."""

from __future__ import annotations

from pathlib import Path
import shutil
import time

import study


TRAIN_READY_SHA = "0ff060b68b78753b3d44c7acc239955efb3b6c77f5c202cb16d5e59c06c8e1e5"
TRAIN_READY_IDENTITY = "7df2ea75a3bdfa7285fb9408a3263001854abd8a910a460da2b213b6ca8225f9"
ARTIFACTS = study.ROOT / "checkpoint-artifacts"
ZERO = ARTIFACTS / "base-zero-adapter"
RECEIPT = ARTIFACTS / "CHECKPOINT_READY.json"


def validate_result_header(result: dict, output: Path) -> None:
    expected = Path(output) / "checkpoint-0001"
    if (
        result.get("status") != "UPDATED"
        or result.get("optimizer_steps") != 1
        or Path(result.get("checkpoint", "")).resolve() != expected.resolve()
    ):
        raise ValueError("evaluation requires exact shaped one-update checkpoint-0001")


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
    save_file(
        {name: torch.zeros_like(value) for name, value in tensors.items()},
        destination / "adapter_model.safetensors",
    )
    shutil.copyfile(source / "adapter_config.json", destination / "adapter_config.json")
    value = {
        "schema": "openai-mrcr-shaped-root-zero-base-adapter-v1",
        "source_adapter_sha256": study.sha(source / "adapter_model.safetensors"),
        "adapter_model_sha256": study.sha(destination / "adapter_model.safetensors"),
        "adapter_config_sha256": study.sha(destination / "adapter_config.json"),
        "tensors": len(tensors),
        "all_tensors_zero": True,
        "semantics": "zero LoRA transport; mathematically identical to released base weights",
    }
    validate_zero_adapter(destination, value)
    return value


def _validate_files(files: dict) -> None:
    for raw, expected in files.items():
        if study.sha(Path(raw)) != expected:
            raise ValueError("checkpoint committed file changed: " + raw)


def qualify_training(output=study.TRAIN_OUTPUT) -> dict:
    output = Path(output)
    ready_path = study.TRAINING / "RUN_READY.json"
    ready = study.read(ready_path)
    if study.sha(ready_path) != TRAIN_READY_SHA or ready.get("identity") != TRAIN_READY_IDENTITY:
        raise ValueError("sealed shaped-root training READY changed")
    for raw, expected in ready["closure_sha256"].items():
        if study.sha(Path(raw)) != expected:
            raise ValueError("shaped-root training closure changed: " + raw)
    result_path = output / "RESULT.json"
    result = study.read(result_path)
    validate_result_header(result, output)
    checkpoint = output / "checkpoint-0001"
    state_path = checkpoint / "state.json"
    commit_path = checkpoint / "STEP_COMMIT.json"
    binding_path = checkpoint / "EVAL_BINDING.json"
    state = study.read(state_path)
    commit = study.read(commit_path)
    binding = study.read(binding_path)
    if (
        result.get("state_sha256") != study.sha(state_path)
        or result.get("step_commit_sha256") != study.sha(commit_path)
        or state.get("step") != 1
        or state.get("optimizer_steps") != 1
        or state.get("episodes") != 24
        or state.get("groups") != 6
        or state.get("child_unchanged") is not True
        or state.get("inputs_sha256") != study.sha(study.TRAINING / "TRAIN_INPUTS.json")
        or "sequence-SUM/24" not in state.get("objective", "")
        or commit.get("status") != "UPDATED"
        or commit.get("optimizer_steps") != 1
    ):
        raise ValueError("shaped one-update state/commit differs")
    _validate_files(commit.get("files_sha256") or {})
    root_alias = binding.get("role_map", {}).get("root")
    child_aliases = binding.get("role_map", {}).get("children")
    root = binding.get("models", {}).get(root_alias, {})
    if (
        binding.get("root_only_update", {}).get("step") != 1
        or binding["root_only_update"].get("fixed_child") is not True
        or child_aliases != ["Qwen3-4B-Instruct-2507-no-research-adapter"]
        or root.get("adapter_sha256") != study.sha(checkpoint / "adapter_model.safetensors")
        or root.get("config_sha256") != study.sha(checkpoint / "adapter_config.json")
    ):
        raise ValueError("root-only evaluation binding differs")
    return {
        "eligible": True,
        "training_ready_identity": ready["identity"],
        "training_result_sha256": study.sha(result_path),
        "checkpoint": str(checkpoint),
        "adapter_model_sha256": study.sha(checkpoint / "adapter_model.safetensors"),
        "adapter_config_sha256": study.sha(checkpoint / "adapter_config.json"),
        "state_sha256": study.sha(state_path),
        "step_commit_sha256": study.sha(commit_path),
        "eval_binding_sha256": study.sha(binding_path),
        "optimizer_sha256": study.sha(checkpoint / "optimizer.pt"),
        "rng_sha256": study.sha(checkpoint / "rng_state.pt"),
        "postupdate_likelihood_shift_measured": False,
    }


def seal_checkpoint() -> dict:
    if RECEIPT.exists() or ARTIFACTS.exists():
        raise FileExistsError("checkpoint evaluation artifacts already exist")
    qualified = qualify_training()
    zero = materialize_zero_adapter(Path(qualified["checkpoint"]), ZERO)
    value = {
        "schema": "openai-mrcr-shaped-root-evaluation-checkpoint-ready-v1",
        "created_epoch": time.time(),
        "training": qualified,
        "zero_adapter": {**zero, "path": str(ZERO)},
        "heldout_model_queries": 0,
        "fixed_checkpoint": 1,
        "checkpoint_selection": False,
    }
    value["identity"] = study.digest(value)
    study.write_x(RECEIPT, value)
    return value


def ensure_checkpoint() -> dict:
    if not RECEIPT.exists():
        return seal_checkpoint()
    return verify_checkpoint()


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
    if arm == "updated":
        trained = receipt["training"]
        root = study.UPDATED_ALIAS
        models[root] = {
            "path": trained["checkpoint"],
            "adapter_sha256": trained["adapter_model_sha256"],
            "config_sha256": trained["adapter_config_sha256"],
        }
    elif arm != "base":
        raise ValueError("arm must be base or updated")
    return {
        "schema": "openai-mrcr-shaped-root-fixed-root-child-binding-v1",
        "models": models,
        "role_map": {"root": root, "children": [study.BASE_ALIAS]},
        "fixed_child": study.BASE_ALIAS,
        "selection_path": str(RECEIPT),
        "selection_sha256": study.sha(RECEIPT),
        "selection_semantics": "fixed step1; zero-LoRA released-base transport",
        "post_training_or_evaluation_checkpoint_selection": False,
    }
