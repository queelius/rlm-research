"""Small evaluator handoff validator for either paired step-1 branch."""

import hashlib
from pathlib import Path


EXPERIMENT = "helper-hf-onpolicy-other31-paired-onestep-v1"
BASELINES = {
    "rloo": "within-question leave-one-action-out RLOO",
    "other31": "detached leave-current-question-out other31x4 mean",
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_handoff(checkpoint, state, binding):
    checkpoint = Path(checkpoint)
    branch = state.get("branch")
    if branch not in BASELINES:
        raise ValueError("unknown branch")
    if (
        state.get("schema") != "helper-hf-onpolicy-other31-paired-state-v1"
        or state.get("step") != 1
        or state.get("optimizer_state_steps") != [1]
        or state.get("baseline") != BASELINES[branch]
    ):
        raise ValueError("state branch/step/baseline differs")
    update = binding.get("child_only_update", {})
    if update.get("branch") != branch:
        raise ValueError("binding branch differs")
    if (
        update.get("experiment") != EXPERIMENT
        or update.get("step") != 1
        or update.get("baseline") != BASELINES[branch]
        or update.get("shared_collection_sha256") != state.get("shared_collection_sha256")
        or update.get("root_unchanged") is not True
    ):
        raise ValueError("binding update differs")
    alias = binding.get("fixed_child")
    if binding.get("role_map", {}).get("children") != [alias]:
        raise ValueError("fixed child role differs")
    child = binding.get("models", {}).get(alias, {})
    if (
        Path(child.get("path", "")).resolve() != checkpoint.resolve()
        or child.get("adapter_sha256") != sha(checkpoint / "adapter_model.safetensors")
        or child.get("config_sha256") != sha(checkpoint / "adapter_config.json")
    ):
        raise ValueError("checkpoint child binding differs")
    return {
        "eligible": True,
        "branch": branch,
        "checkpoint": str(checkpoint),
        "shared_collection_sha256": state["shared_collection_sha256"],
    }
