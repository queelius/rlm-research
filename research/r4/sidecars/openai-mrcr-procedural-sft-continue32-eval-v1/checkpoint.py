"""Authenticate the fixed resumed checkpoint-0032 and derive a zero-base transport."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import time

import study


ARTIFACTS = study.ROOT / "checkpoint-artifacts"
ZERO = ARTIFACTS / "base-zero-adapter"
RECEIPT = ARTIFACTS / "CHECKPOINT_READY.json"


def _old_checkpoint():
    previous = sys.modules.get("study")
    sys.modules["study"] = study
    try:
        path = study.SOURCE_EVAL / "checkpoint.py"
        spec = importlib.util.spec_from_file_location("continue32_old_checkpoint", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        if previous is None:
            sys.modules.pop("study", None)
        else:
            sys.modules["study"] = previous


old = _old_checkpoint()
validate_zero_adapter = old.validate_zero_adapter
materialize_zero_adapter = old.materialize_zero_adapter


def validate_result_header(result: dict, output: Path) -> None:
    checkpoint = Path(output) / "checkpoint-0032"
    if (
        result.get("status") != "COMPLETED_32_TOTAL_UPDATES"
        or result.get("optimizer_steps") != 32
        or result.get("additional_optimizer_steps") != 28
        or Path(result.get("primary_checkpoint", "")).resolve() != checkpoint.resolve()
        or Path(result.get("evaluation_binding", "")).resolve()
        != (checkpoint / "EVAL_BINDING.json").resolve()
        or len(result.get("step_commits") or []) != 28
    ):
        raise ValueError("evaluation requires the fixed completed checkpoint-0032 continuation")


def _validate_commit(
    directory: Path, expected_step: int, previous: str, ready_identity: str, restored_sha: str
) -> tuple[dict, dict, str]:
    state_path = directory / "state.json"
    commit_path = directory / "STEP_COMMIT.json"
    state = study.read(state_path)
    commit = study.read(commit_path)
    if (
        state.get("schema") != "openai-mrcr-procedural-sft-state-v1"
        or state.get("step") != expected_step
        or state.get("optimizer_steps") != expected_step
        or state.get("additional_optimizer_steps") != expected_step - 4
        or state.get("ready_identity") != ready_identity
        or state.get("corpus_sha256") != "e4f5a2e71a435cebb732f13ad551f74edca1b784920b80230fb5ae282e1ecf56"
        or state.get("previous_step_commit_sha256") != previous
        or state.get("resume_parent_step_commit_sha256")
        != "50f3767f4a9d2622991bbdf96b9885620c422f84abe16c9e4e6e397c7427bd24"
        or state.get("restored_state_sha256") != restored_sha
        or commit.get("schema") != "openai-mrcr-procedural-sft-step-commit-v1"
        or commit.get("step") != expected_step
        or commit.get("optimizer_steps") != expected_step
        or commit.get("identity")
        != study.digest({key: value for key, value in commit.items() if key != "identity"})
    ):
        raise ValueError(f"checkpoint-{expected_step:04d} state/commit lineage differs")
    required = {"adapter_model.safetensors", "adapter_config.json", "optimizer.pt", "rng.pt", "EVAL_BINDING.json", "state.json"}
    if set(commit.get("files_sha256") or {}) != required:
        raise ValueError(f"checkpoint-{expected_step:04d} committed inventory differs")
    for name, expected in commit["files_sha256"].items():
        if study.sha(directory / name) != expected:
            raise ValueError(f"checkpoint-{expected_step:04d} file changed: {name}")
    return state, commit, study.sha(commit_path)


def qualify_training() -> dict:
    eval_ready = study.read(study.READY)
    ready_path = study.TRAINING / "READY_TRAINING.json"
    ready = study.read(ready_path)
    if (
        study.sha(ready_path) != eval_ready.get("training_ready_sha256")
        or ready.get("identity") != eval_ready.get("training_ready_identity")
    ):
        raise ValueError("fixed continuation training READY changed")
    for raw, expected in ready["closure_sha256"].items():
        if study.sha(Path(raw)) != expected:
            raise ValueError("continuation training closure changed: " + raw)
    result_path = study.TRAIN_OUTPUT / "RESULT.json"
    result = study.read(result_path)
    validate_result_header(result, study.TRAIN_OUTPUT)
    if (
        result.get("ready_identity") != ready["identity"]
        or result.get("corpus_sha256") != "e4f5a2e71a435cebb732f13ad551f74edca1b784920b80230fb5ae282e1ecf56"
    ):
        raise ValueError("continuation result source identity differs")
    parent = Path(result.get("resume_parent_checkpoint", ""))
    expected_parent = study.SOURCE_EVAL.parent / "openai-mrcr-procedural-sft-warmstart-v1/outputs/attempt-001/checkpoint-0004"
    parent_commit_path = parent / "STEP_COMMIT.json"
    if (
        parent.resolve() != expected_parent.resolve()
        or result.get("resume_parent_step_commit_sha256") != study.sha(parent_commit_path)
    ):
        raise ValueError("checkpoint4 resume parent differs")
    restored_path = study.TRAIN_OUTPUT / "RESTORED_STATE.json"
    restored = study.read(restored_path)
    restored_sha = study.sha(restored_path)
    if (
        result.get("restored_state_sha256") != restored_sha
        or restored.get("restored_step") != 4
        or restored.get("adapter_parameters_exact") is not True
        or restored.get("optimizer_state_exact") is not True
        or restored.get("cuda_rng_restored") is not True
        or restored.get("adapter_model_sha256") != study.sha(parent / "adapter_model.safetensors")
        or restored.get("optimizer_sha256") != study.sha(parent / "optimizer.pt")
        or restored.get("rng_sha256") != study.sha(parent / "rng.pt")
    ):
        raise ValueError("checkpoint4 adapter/Adam/RNG restoration receipt differs")
    previous = study.sha(parent_commit_path)
    lineage = []
    declared = result["step_commits"]
    for offset, step in enumerate(range(5, 33)):
        directory = study.TRAIN_OUTPUT / f"checkpoint-{step:04d}"
        state, commit, commit_sha = _validate_commit(
            directory, step, previous, ready["identity"], restored_sha
        )
        declared_row = declared[offset]
        if (
            Path(declared_row.get("path", "")).resolve() != (directory / "STEP_COMMIT.json").resolve()
            or declared_row.get("sha256") != commit_sha
            or declared_row.get("identity") != commit["identity"]
        ):
            raise ValueError("RESULT step commit list differs")
        previous = commit_sha
        lineage.append({"step": step, "state_sha256": study.sha(directory / "state.json"),
                        "commit_sha256": commit_sha, "optimizer_sha256": study.sha(directory / "optimizer.pt"),
                        "rng_sha256": study.sha(directory / "rng.pt")})
    checkpoint = study.TRAIN_OUTPUT / "checkpoint-0032"
    binding = study.read(checkpoint / "EVAL_BINDING.json")
    if (
        binding.get("root_only_update") is not True
        or binding.get("step") != 32
        or binding.get("fixed_primary_step") != 32
        or binding.get("training_ready_identity") != ready["identity"]
        or binding.get("resume_parent_checkpoint") != str(parent)
        or binding.get("resume_parent_step_commit_sha256") != study.sha(parent_commit_path)
        or binding.get("child", {}).get("adapter") is not None
        or binding.get("root", {}).get("adapter_model_sha256")
        != study.sha(checkpoint / "adapter_model.safetensors")
    ):
        raise ValueError("fixed checkpoint32 root/child evaluation binding differs")
    import torch

    optimizer = torch.load(checkpoint / "optimizer.pt", map_location="cpu", weights_only=True)
    rng = torch.load(checkpoint / "rng.pt", map_location="cpu", weights_only=False)
    if (
        {int(value["step"]) for value in optimizer.get("state", {}).values()} != {32}
        or len(optimizer.get("state", {})) != 504
        or set(rng) != {"python", "numpy", "torch_cpu", "torch_cuda"}
        or len(rng["torch_cuda"]) != 1
    ):
        raise ValueError("checkpoint32 Adam/RNG state differs")
    return {
        "eligible": True,
        "training_ready_identity": ready["identity"],
        "training_ready_sha256": study.sha(ready_path),
        "training_result_sha256": study.sha(result_path),
        "checkpoint": str(checkpoint),
        "adapter_model_sha256": study.sha(checkpoint / "adapter_model.safetensors"),
        "adapter_config_sha256": study.sha(checkpoint / "adapter_config.json"),
        "parent_checkpoint4_commit_sha256": study.sha(parent_commit_path),
        "restored_state_sha256": restored_sha,
        "lineage": lineage,
    }


def seal_checkpoint() -> dict:
    if RECEIPT.exists() or ARTIFACTS.exists():
        raise FileExistsError("checkpoint evaluation artifacts already exist")
    qualified = qualify_training()
    zero = materialize_zero_adapter(Path(qualified["checkpoint"]), ZERO)
    value = {
        "schema": "openai-mrcr-procedural-sft-continue32-evaluation-checkpoint-ready-v1",
        "created_epoch": time.time(),
        "training": qualified,
        "zero_adapter": {**zero, "path": str(ZERO)},
        "heldout_model_queries": 0,
        "fixed_primary_step": 32,
        "checkpoint_selection": False,
    }
    value["identity"] = study.digest(value)
    study.write_x(RECEIPT, value)
    return value


def verify_checkpoint() -> dict:
    value = study.read(RECEIPT)
    if value.get("identity") != study.digest({key: item for key, item in value.items() if key != "identity"}):
        raise ValueError("checkpoint evaluation receipt changed")
    if value.get("training") != qualify_training():
        raise ValueError("current checkpoint32 lineage differs from receipt")
    validate_zero_adapter(ZERO, value["zero_adapter"])
    return value


def ensure_checkpoint() -> dict:
    return verify_checkpoint() if RECEIPT.exists() else seal_checkpoint()


def binding(arm: str) -> dict:
    receipt = verify_checkpoint()
    zero = receipt["zero_adapter"]
    models = {study.BASE_ALIAS: {"path": str(ZERO), "adapter_sha256": zero["adapter_model_sha256"],
                                 "config_sha256": zero["adapter_config_sha256"]}}
    root = study.BASE_ALIAS
    if arm == "checkpoint32":
        trained = receipt["training"]
        root = study.ADAPTED_ALIAS
        models[root] = {"path": trained["checkpoint"],
                        "adapter_sha256": trained["adapter_model_sha256"],
                        "config_sha256": trained["adapter_config_sha256"]}
    elif arm != "base":
        raise ValueError("arm must be base or checkpoint32")
    return {
        "schema": "openai-mrcr-procedural-sft-continue32-fixed-root-child-binding-v1",
        "models": models,
        "role_map": {"root": root, "children": [study.BASE_ALIAS]},
        "fixed_child": study.BASE_ALIAS,
        "selection_path": str(RECEIPT),
        "selection_sha256": study.sha(RECEIPT),
        "selection_semantics": "fixed checkpoint32 continuation; zero-LoRA released-base transport",
        "post_training_or_evaluation_checkpoint_selection": False,
    }
