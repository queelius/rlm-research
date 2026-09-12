"""Authenticate both token-TIS branches and create an exact-zero transport adapter."""

from __future__ import annotations

import math
from pathlib import Path
import shutil
import time

import study


TRAIN_READY_SHA256 = "71f1a67df3d0e3dfb4521ae79e68b0df1add2948885825e577860cc77fc58a73"
TRAIN_READY_IDENTITY = "a1654f6ec577e592da71bb12ef3d7e4d2e0ba357f028380a6081bdcd8f1e864e"
ARTIFACTS = study.ROOT / "checkpoint-artifacts"
ZERO = ARTIFACTS / "base-zero-adapter"
RECEIPT = ARTIFACTS / "CHECKPOINT_READY.json"


def validate_result_header(result: dict, output: Path) -> None:
    output = Path(output)
    if result.get("status") != "UPDATED_TWO_INDEPENDENT_BRANCHES":
        raise ValueError("evaluation requires both independent step1 branches")
    branches = result.get("branches") or {}
    if set(branches) != {"lr1e-5", "lr1e-4"}:
        raise ValueError("evaluation requires both independent step1 branches")
    for name, row in branches.items():
        expected = output / "branches" / name / "checkpoint-0001"
        if (
            row.get("status") != "UPDATED"
            or row.get("optimizer_steps") != 1
            or Path(row.get("checkpoint", "")).resolve() != expected.resolve()
        ):
            raise ValueError("evaluation requires both independent step1 branches")


def validate_zero_adapter(directory: Path, receipt: dict) -> None:
    import torch
    from safetensors.torch import load_file

    tensors = load_file(Path(directory) / "adapter_model.safetensors", device="cpu")
    if not tensors or any("lora_" not in name for name in tensors):
        raise ValueError("zero adapter inventory differs")
    if any(torch.count_nonzero(value).item() for value in tensors.values()):
        raise ValueError("base transport adapter is not exactly zero")
    config = study.read(Path(directory) / "adapter_config.json")
    if config.get("bias") != "none" or float(config.get("lora_dropout", -1)) != 0:
        raise ValueError("zero adapter config differs")
    if (
        receipt.get("all_tensors_zero") is not True
        or receipt.get("tensors") != len(tensors)
        or receipt.get("adapter_model_sha256")
        != study.sha(Path(directory) / "adapter_model.safetensors")
        or receipt.get("adapter_config_sha256")
        != study.sha(Path(directory) / "adapter_config.json")
    ):
        raise ValueError("zero adapter receipt differs")


def materialize_zero_adapter(source: Path, destination: Path) -> dict:
    import torch
    from safetensors.torch import load_file, save_file

    if destination.exists():
        raise FileExistsError(destination)
    tensors = load_file(Path(source) / "adapter_model.safetensors", device="cpu")
    if not tensors or any("lora_" not in name for name in tensors):
        raise ValueError("checkpoint is not pure LoRA")
    destination.mkdir(parents=True)
    save_file(
        {name: torch.zeros_like(value) for name, value in tensors.items()},
        destination / "adapter_model.safetensors",
    )
    shutil.copyfile(source / "adapter_config.json", destination / "adapter_config.json")
    receipt = {
        "schema": "mrcr-token-tis-zero-transport-v1",
        "source_adapter_sha256": study.sha(source / "adapter_model.safetensors"),
        "adapter_model_sha256": study.sha(destination / "adapter_model.safetensors"),
        "adapter_config_sha256": study.sha(destination / "adapter_config.json"),
        "tensors": len(tensors),
        "all_tensors_zero": True,
    }
    validate_zero_adapter(destination, receipt)
    return receipt


def _validate_committed(checkpoint: Path, expected_branch: str) -> dict:
    state_path = checkpoint / "state.json"
    commit_path = checkpoint / "STEP_COMMIT.json"
    binding_path = checkpoint / "EVAL_BINDING.json"
    state = study.read(state_path)
    commit = study.read(commit_path)
    binding = study.read(binding_path)
    if (
        state.get("schema") != "mrcr-root-token-tis-independent-step1-state-v1"
        or state.get("branch") != expected_branch
        or state.get("optimizer_steps") != 1
        or state.get("optimizer_state_steps") != [1]
        or state.get("weight_decay") != 0.0
        or state.get("episodes") != 24
        or state.get("groups") != 6
        or state.get("root_turns") != 74
        or state.get("root_action_tokens") != 15602
        or state.get("new_generation_calls") != 0
        or state.get("heldout_queries") != 0
        or state.get("inputs_sha256") != study.sha(study.TRAIN_INPUTS)
        or not math.isfinite(float(state.get("adapter_delta_l2", 0)))
        or float(state.get("adapter_delta_l2", 0)) <= 0
        or commit.get("status") != "UPDATED"
        or commit.get("branch") != expected_branch
        or commit.get("optimizer_steps") != 1
    ):
        raise ValueError("token-TIS branch state differs")
    for raw, expected in commit.get("files_sha256", {}).items():
        if study.sha(Path(raw)) != expected:
            raise ValueError("branch committed file changed: " + raw)
    root_alias = binding.get("role_map", {}).get("root")
    root = binding.get("models", {}).get(root_alias, {})
    if (
        binding.get("root_only_update", {}).get("branch") != expected_branch
        or binding["root_only_update"].get("fixed_child") is not True
        or binding.get("role_map", {}).get("children")
        != ["Qwen3-4B-Instruct-2507-no-research-adapter"]
        or root.get("adapter_sha256") != study.sha(checkpoint / "adapter_model.safetensors")
        or root.get("config_sha256") != study.sha(checkpoint / "adapter_config.json")
    ):
        raise ValueError("token-TIS evaluation binding differs")
    return {
        "checkpoint": str(checkpoint),
        "adapter_model_sha256": study.sha(checkpoint / "adapter_model.safetensors"),
        "adapter_config_sha256": study.sha(checkpoint / "adapter_config.json"),
        "state_sha256": study.sha(state_path),
        "step_commit_sha256": study.sha(commit_path),
        "eval_binding_sha256": study.sha(binding_path),
        "learning_rate": state["learning_rate"],
        "adapter_delta_l2": state["adapter_delta_l2"],
    }


def qualify_training() -> dict:
    ready_path = study.TRAINING / "CPU_READY_V2.json"
    ready = study.read(ready_path)
    if study.sha(ready_path) != TRAIN_READY_SHA256 or ready.get("identity") != TRAIN_READY_IDENTITY:
        raise ValueError("token-TIS training READY changed")
    for raw, expected in ready["closure_sha256"].items():
        if study.sha(Path(raw)) != expected:
            raise ValueError("token-TIS training closure changed: " + raw)
    result_path = study.TRAIN_OUTPUT / "RESULT.json"
    result = study.read(result_path)
    validate_result_header(result, study.TRAIN_OUTPUT)
    relation_path = study.TRAIN_OUTPUT / "BRANCH_RELATION.json"
    relation = study.read(relation_path)
    if relation.get("passed") is not True or not math.isclose(
        float(relation.get("delta_norm_ratio", 0)), 10.0, rel_tol=0.005
    ):
        raise ValueError("10x fixed-dose relation did not pass")
    branches = {
        name: _validate_committed(
            study.TRAIN_OUTPUT / "branches" / name / "checkpoint-0001", name
        )
        for name in ("lr1e-5", "lr1e-4")
    }
    if result.get("same_initial_trainable_identity_sha256") is None:
        raise ValueError("shared initial identity absent")
    return {
        "eligible": True,
        "training_ready_identity": ready["identity"],
        "training_ready_sha256": study.sha(ready_path),
        "training_result_sha256": study.sha(result_path),
        "branch_relation_sha256": study.sha(relation_path),
        "same_initial_trainable_identity_sha256": result["same_initial_trainable_identity_sha256"],
        "same_saved_gradient_sha256": result["same_saved_gradient_sha256"],
        "branches": branches,
    }


def seal_checkpoint() -> dict:
    if ARTIFACTS.exists():
        raise FileExistsError("evaluation checkpoint artifacts already exist")
    qualified = qualify_training()
    low = Path(qualified["branches"]["lr1e-5"]["checkpoint"])
    zero = materialize_zero_adapter(low, ZERO)
    value = {
        "schema": "mrcr-token-tis-held16-checkpoint-ready-v1",
        "created_epoch": time.time(),
        "training": qualified,
        "branches": qualified["branches"],
        "zero_adapter": {**zero, "path": str(ZERO)},
        "fixed_branches": ["lr1e-5", "lr1e-4"],
        "checkpoint_selection": False,
        "heldout_model_queries": 0,
    }
    value["identity"] = study.digest(value)
    study.write_x(RECEIPT, value)
    return value


def verify_checkpoint() -> dict:
    value = study.read(RECEIPT)
    if value.get("identity") != study.digest({key: row for key, row in value.items() if key != "identity"}):
        raise ValueError("checkpoint receipt identity changed")
    if value.get("training") != qualify_training():
        raise ValueError("current token-TIS training lineage differs")
    validate_zero_adapter(ZERO, value["zero_adapter"])
    return value


def ensure_checkpoint() -> dict:
    return verify_checkpoint() if RECEIPT.exists() else seal_checkpoint()


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
    root_alias = study.BASE_ALIAS
    if arm in study.BRANCH_ALIASES:
        root_alias = study.BRANCH_ALIASES[arm]
        branch = receipt["branches"][arm]
        models[root_alias] = {
            "path": branch["checkpoint"],
            "adapter_sha256": branch["adapter_model_sha256"],
            "config_sha256": branch["adapter_config_sha256"],
        }
    elif arm != "base":
        raise ValueError("unknown fixed held16 arm")
    return {
        "schema": "mrcr-token-tis-held16-binding-v1",
        "models": models,
        "role_map": {"root": root_alias, "children": [study.BASE_ALIAS]},
        "fixed_child": study.BASE_ALIAS,
        "selection_path": str(RECEIPT),
        "selection_sha256": study.sha(RECEIPT),
        "post_training_checkpoint_selection": False,
    }
