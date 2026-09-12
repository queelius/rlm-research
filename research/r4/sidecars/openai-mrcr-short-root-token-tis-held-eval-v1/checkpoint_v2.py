"""Additive checkpoint-lineage repair for both token-TIS branches."""

from __future__ import annotations

import hashlib
import importlib.util
import math
from pathlib import Path
import sys

import torch

import study_v2 as study


def _load_base():
    previous = sys.modules.get("study")
    sys.modules["study"] = study
    try:
        path = study.ROOT / "checkpoint.py"
        spec = importlib.util.spec_from_file_location("token_tis_held_v1_checkpoint_source", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        if previous is None:
            sys.modules.pop("study", None)
        else:
            sys.modules["study"] = previous


base = _load_base()
TRAIN_READY_SHA256 = base.TRAIN_READY_SHA256
TRAIN_READY_IDENTITY = base.TRAIN_READY_IDENTITY
ARTIFACTS = study.ROOT / "checkpoint-artifacts-v2"
ZERO = ARTIFACTS / "base-zero-adapter"
RECEIPT = ARTIFACTS / "CHECKPOINT_READY.json"
validate_result_header = base.validate_result_header
validate_zero_adapter = base.validate_zero_adapter
materialize_zero_adapter = base.materialize_zero_adapter


def _tensor_digest(snapshot):
    digest = hashlib.sha256()
    for name in sorted(snapshot):
        value = snapshot[name].detach().cpu().contiguous()
        digest.update(name.encode())
        digest.update(str(value.dtype).encode())
        digest.update(str(tuple(value.shape)).encode())
        digest.update(value.numpy().tobytes(order="C"))
    return digest.hexdigest()


def _validate_branch(checkpoint: Path, branch: str, result_row: dict, shared: dict) -> dict:
    state_path = checkpoint / "state.json"
    commit_path = checkpoint / "STEP_COMMIT.json"
    binding_path = checkpoint / "EVAL_BINDING.json"
    state = study.read(state_path)
    commit = study.read(commit_path)
    binding = study.read(binding_path)
    if (
        result_row.get("state_sha256") != study.sha(state_path)
        or result_row.get("step_commit_sha256") != study.sha(commit_path)
        or state.get("schema") != "mrcr-root-token-tis-independent-step1-state-v1"
        or state.get("branch") != branch
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
        or state.get("starting_identity_sha256") != shared["initial_identity"]
        or state.get("saved_gradient_sha256") != shared["gradient_sha256"]
        or state.get("initial_rng_sha256") != shared["rng_sha256"]
        or not math.isfinite(float(state.get("adapter_delta_l2", 0)))
        or float(state.get("adapter_delta_l2", 0)) <= 0
        or commit.get("status") != "UPDATED"
        or commit.get("branch") != branch
        or commit.get("optimizer_steps") != 1
    ):
        raise ValueError("token-TIS branch state/result/shared provenance differs")
    for raw, expected in commit.get("files_sha256", {}).items():
        if study.sha(Path(raw)) != expected:
            raise ValueError("branch committed file changed: " + raw)
    root_alias = binding.get("role_map", {}).get("root")
    root = binding.get("models", {}).get(root_alias, {})
    if (
        binding.get("root_only_update", {}).get("branch") != branch
        or binding["root_only_update"].get("fixed_child") is not True
        or binding.get("role_map", {}).get("children")
        != ["Qwen3-4B-Instruct-2507-no-research-adapter"]
        or root.get("adapter_sha256") != study.sha(checkpoint / "adapter_model.safetensors")
        or root.get("config_sha256") != study.sha(checkpoint / "adapter_config.json")
    ):
        raise ValueError("token-TIS evaluation binding differs")
    likelihood = study.TRAIN_OUTPUT / "likelihood" / branch / "INVENTORY.json"
    if state.get("postupdate_likelihood_inventory_sha256") != study.sha(likelihood):
        raise ValueError("postupdate likelihood inventory changed")
    return {
        "checkpoint": str(checkpoint),
        "adapter_model_sha256": study.sha(checkpoint / "adapter_model.safetensors"),
        "adapter_config_sha256": study.sha(checkpoint / "adapter_config.json"),
        "state_sha256": study.sha(state_path),
        "step_commit_sha256": study.sha(commit_path),
        "eval_binding_sha256": study.sha(binding_path),
        "learning_rate": state["learning_rate"],
        "adapter_delta_l2": state["adapter_delta_l2"],
        "postupdate_likelihood_inventory_sha256": study.sha(likelihood),
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
    initial_path = study.TRAIN_OUTPUT / "INITIAL_TRAINABLE.pt"
    rng_path = study.TRAIN_OUTPUT / "INITIAL_RNG.pt"
    gradient_path = study.TRAIN_OUTPUT / "CLIPPED_GRADIENTS.pt"
    initial = torch.load(initial_path, map_location="cpu", weights_only=True)
    shared = {
        "initial_identity": _tensor_digest(initial),
        "rng_sha256": study.sha(rng_path),
        "gradient_sha256": study.sha(gradient_path),
    }
    if (
        result.get("same_initial_trainable_identity_sha256") != shared["initial_identity"]
        or result.get("same_saved_gradient_sha256") != shared["gradient_sha256"]
    ):
        raise ValueError("result does not authenticate initial tensors/gradient")
    relation_path = study.TRAIN_OUTPUT / "BRANCH_RELATION.json"
    relation = study.read(relation_path)
    if (
        result.get("branch_relation_sha256") != study.sha(relation_path)
        or relation.get("passed") is not True
        or not math.isclose(float(relation.get("delta_norm_ratio", 0)), 10.0, rel_tol=0.005)
    ):
        raise ValueError("result does not authenticate passing 10x relation")
    branches = {
        name: _validate_branch(
            study.TRAIN_OUTPUT / "branches" / name / "checkpoint-0001",
            name,
            result["branches"][name],
            shared,
        )
        for name in ("lr1e-5", "lr1e-4")
    }
    return {
        "eligible": True,
        "training_ready_identity": ready["identity"],
        "training_ready_sha256": study.sha(ready_path),
        "training_result_sha256": study.sha(result_path),
        "branch_relation_sha256": study.sha(relation_path),
        "initial_trainable_sha256": study.sha(initial_path),
        "initial_trainable_identity_sha256": shared["initial_identity"],
        "initial_rng_sha256": shared["rng_sha256"],
        "saved_gradient_sha256": shared["gradient_sha256"],
        "branches": branches,
    }


base.qualify_training = qualify_training
base.ARTIFACTS = ARTIFACTS
base.ZERO = ZERO
base.RECEIPT = RECEIPT
seal_checkpoint = base.seal_checkpoint
verify_checkpoint = base.verify_checkpoint
ensure_checkpoint = base.ensure_checkpoint
binding = base.binding
