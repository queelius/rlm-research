"""Conditional bindings for the paired step-1 checkpoints on fixed unseen256."""

import copy
import functools
import hashlib
import importlib.util
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
TRAINING = SIDE / "helper-hf-onpolicy-other31-paired-onestep-v1"
SOURCE_EVAL = SIDE / "helper-hf-fourstep-unseen-eval-v1"
C32_EVAL = SIDE / "helper-unseen-generalization-c32-baseline-v1"
SOURCE_BINDING = SIDE / "root-qs6-feedback-diagnostic-v1/outputs/attempt-001/service/BINDING.json"
NATIVE = Path("/project/alex_phd/envs/prime-rl-5990b1b/bin/python")
CAP = 600
OUTER_CAP = 700
CHILD_ALIAS = "strict-rlm-qwen3-4b-role-sft-selected-v1"
CHILD_SHA = "c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3"
TRAIN_READY_SHA256 = "8935d346f9ef8de4cd67c8cfe545cf47246de5d20b9de86098eb2efc7e06a6e1"
TRAIN_READY_IDENTITY = "e349925bf8234a5c03771be69f4136d56b7c50d717d14233ceff204238d90779"
BASELINES = {
    "rloo": "within-question leave-one-action-out RLOO",
    "other31": "detached leave-current-question-out other31x4 mean",
}
ARMS = {
    name: {
        "attempt": ROOT / f"arms/{name}/outputs/attempt-001",
        "ready": ROOT / ("READY_RLOO.json" if name == "rloo" else "READY_OTHER31.json"),
        "checkpoint": TRAINING / f"outputs/attempt-001/branches/{name}/checkpoint-0001",
    }
    for name in BASELINES
}
CURRENT = None
ATTEMPT = None


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    digest_object = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest_object.update(chunk)
    return digest_object.hexdigest()


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def write_x(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if path.exists():
        if path.read_text() != rendered:
            raise ValueError("immutable file differs: " + str(path))
    else:
        with path.open("x") as stream:
            stream.write(rendered)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load " + str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@functools.lru_cache(maxsize=1)
def source_eval():
    return load("other31_paired_source_eval", SOURCE_EVAL / "fourstep_panel_study.py")


@functools.lru_cache(maxsize=1)
def pair_math():
    return load("other31_paired_source_math", TRAINING / "pair_math.py")


MODEL = source_eval().MODEL
panel = source_eval().panel
schedule = source_eval().schedule
dependencies = source_eval().dependencies


def select(branch):
    global ATTEMPT, CURRENT
    if branch not in ARMS:
        raise ValueError("unknown branch")
    CURRENT = branch
    ATTEMPT = ARMS[branch]["attempt"]


def resolve_branch(branch=None):
    if branch is None:
        branch = CURRENT
    if branch not in ARMS:
        raise ValueError("branch not selected before collector verification")
    return branch


def ready_path(branch):
    return ARMS[resolve_branch(branch)]["ready"]


def plan(branch):
    branch = resolve_branch(branch)
    rows = schedule()
    return {
        "schema": "helper-hf-other31-paired-unseen-eval-ready-v1",
        "status": "CPU_READY_CONDITIONAL_ON_EXACT_PAIRED_TRAINING",
        "branch": branch,
        "baseline": BASELINES[branch],
        "command": [
            str(NATIVE),
            str(ROOT / "owner.py"),
            "run",
            "--branch",
            branch,
            "--outer-seconds",
            str(CAP),
        ],
        "output": str(ARMS[branch]["attempt"]),
        "inner_cap_seconds": CAP,
        "external_timeout_seconds": OUTER_CAP,
        "launch_authority": "MAIN only after exact paired training completes and GPU releases",
        "inventory": {
            "physical_calls": len(rows),
            "predictions": sum(len(row["ids"]) for row in rows),
            "batch_size": 4,
            "root_calls": 0,
            "training_updates": 0,
        },
        "policy": {
            "temperature": 0,
            "schedule_sha256": digest(rows),
            "fixed_primary_checkpoint_step": 1,
            "selection": "none; exact branch checkpoint-0001 only",
        },
    }


def verify_hash_map(mapping):
    if not isinstance(mapping, dict) or not mapping:
        raise ValueError("empty committed file inventory")
    for raw, expected in mapping.items():
        if sha(raw) != expected:
            raise ValueError("committed file changed: " + raw)


def verify_binding(checkpoint, branch, shared_sha, state_sha, source_binding, binding):
    checkpoint = Path(checkpoint)
    child = binding.get("models", {}).get(CHILD_ALIAS, {})
    expected_child = {
        "path": str(checkpoint),
        "adapter_sha256": sha(checkpoint / "adapter_model.safetensors"),
        "config_sha256": sha(checkpoint / "adapter_config.json"),
    }
    if child != expected_child:
        raise ValueError("branch child binding files differ")
    update = binding.get("child_only_update", {})
    if (
        update.get("experiment") != TRAINING.name
        or update.get("branch") != branch
        or update.get("step") != 1
        or update.get("baseline") != BASELINES[branch]
        or update.get("shared_collection_sha256") != shared_sha
        or update.get("root_unchanged") is not True
        or update.get("state_sha256") != state_sha
        or update.get("source_child") != source_binding["models"][CHILD_ALIAS]
    ):
        raise ValueError("branch child-only update differs")
    expected = copy.deepcopy(source_binding)
    expected["models"][CHILD_ALIAS] = expected_child
    expected["child_only_update"] = update
    if binding != expected:
        raise ValueError("binding changed beyond authenticated child branch")
    root_alias = source_binding["role_map"]["root"]
    if binding["models"][root_alias] != source_binding["models"][root_alias]:
        raise ValueError("root binding changed")
    return binding


def verify_probability_group(row, replay, index):
    if row != replay:
        raise ValueError("qualification differs from branch replay")
    source_eval().verify_probability_group(row, index, replay)
    if row.get("branch") not in BASELINES or row.get("shared_rollout_sha256") is None:
        raise ValueError("branch replay provenance differs")


def qualify_pair(branch):
    branch = resolve_branch(branch)
    ready_path_training = TRAINING / "READY.json"
    ready = read(ready_path_training)
    if (
        sha(ready_path_training) != TRAIN_READY_SHA256
        or ready.get("identity") != TRAIN_READY_IDENTITY
    ):
        raise ValueError("paired training READY differs")
    for raw, expected in ready["closure_sha256"].items():
        if sha(raw) != expected:
            raise ValueError("paired training closure changed: " + raw)
    output = TRAINING / "outputs/attempt-001"
    result_path = output / "RESULT.json"
    result = read(result_path)
    shared_path = output / "shared-collection/COLLECTION.json"
    if (
        result.get("status") != "COMPLETED_PAIRED_ONE_STEP"
        or result.get("completed_branches") != ["rloo", "other31"]
        or result.get("optimizer_steps") != {"rloo": 1, "other31": 1}
        or Path(result.get("shared_collection", "")).resolve() != shared_path.resolve()
        or result.get("shared_collection_sha256") != sha(shared_path)
        or result.get("shared_actions") != 128
    ):
        raise ValueError("exact completed paired training result required")
    for name in BASELINES:
        branch_result_path = output / f"branches/{name}/RESULT.json"
        branch_result = read(branch_result_path)
        if (
            result.get("branches", {}).get(name) != branch_result
            or branch_result.get("status") != "UPDATED"
            or branch_result.get("optimizer_steps") != 1
            or branch_result.get("baseline") != BASELINES[name]
            or branch_result.get("shared_collection_sha256") != sha(shared_path)
        ):
            raise ValueError("both exact branch updates are required")
    start = read(output / "START.json")
    snapshot = read(output / "C32_SNAPSHOT.json")
    restore = read(output / "BRANCH_RESTORE.json")
    if (
        start.get("ready_identity") != ready["identity"]
        or start.get("planned_shared_actions") != 128
        or start.get("planned_branches") != ["rloo", "other31"]
        or start.get("optimizer_steps_per_branch") != 1
        or snapshot.get("serialized_sha256") != sha(output / "C32_TRAINABLE_SNAPSHOT.pt")
        or restore.get("after_branch") != "rloo"
        or restore.get("before_branch") != "other31"
        or restore.get("bit_identical_c32") is not True
        or restore.get("tensor_identity_sha256") != snapshot.get("tensor_identity_sha256")
        or restore.get("rng_restored_sha256")
        != sha(output / "shared-collection/AFTER_COLLECTION_RNG.pt")
        or restore.get("fresh_second_optimizer") is not True
    ):
        raise ValueError("paired c32 pre-step/restore receipt differs")
    collection = read(shared_path)
    if (
        collection.get("schema") != "helper-hf-other31-shared-fresh-collection-v1"
        or collection.get("groups") != 32
        or collection.get("actions") != 128
        or collection.get("freshly_sampled") is not True
        or collection.get("optimizer_created_during_collection") is not False
        or collection.get("parent_adapter_sha256") != CHILD_SHA
        or collection.get("temperature") != 1.0
        or collection.get("all_failure_actions_retained")
        != 4 * len(collection.get("all_failure_group_ids", []))
        or len(collection.get("action_inventory", [])) != 32
        or collection.get("after_collection_rng_sha256")
        != sha(output / "shared-collection/AFTER_COLLECTION_RNG.pt")
    ):
        raise ValueError("shared collection inventory differs")
    groups = read(TRAINING / "inputs/GROUPS.json")
    expected_ids = {row["group_id"] for row in groups}
    inventory = {row["group_id"]: row for row in collection["action_inventory"]}
    if set(inventory) != expected_ids or len(inventory) != 32:
        raise ValueError("shared source-coordinate inventory differs")
    reward_groups = []
    ordered_ids = []
    for index in range(32):
        directory = output / f"shared-collection/groups/group-{index:03d}"
        rollout = read(directory / "ROLLOUT.json")
        group_id = rollout.get("group_id")
        item = inventory.get(group_id)
        if item is None:
            raise ValueError("shared group missing from inventory")
        if (
            item.get("rollout_sha256") != sha(directory / "ROLLOUT.json")
            or item.get("masks_sha256") != sha(directory / "MASKS.npz")
            or item.get("commit_sha256") != sha(directory / "GROUP_COMMIT.json")
            or item.get("completion_ids") != rollout.get("completion_ids")
            or item.get("rewards") != rollout.get("rewards")
            or rollout.get("shared_actions_for_branches") != ["rloo", "other31"]
        ):
            raise ValueError("shared raw action or mask receipt differs")
        commit = read(directory / "GROUP_COMMIT.json")
        if (
            commit.get("ready_identity") != ready["identity"]
            or commit.get("parent_identity") != CHILD_SHA
            or commit.get("group_index") != index
            or commit.get("group_id") != group_id
            or commit.get("actions_shared_by_both_branches") is not True
        ):
            raise ValueError("shared group commit header differs")
        verify_hash_map(commit["files_sha256"])
        reward_groups.append(rollout["rewards"])
        ordered_ids.append(group_id)
    expected_advantages = pair_math().paired_advantages(reward_groups)
    source_binding = read(SOURCE_BINDING)
    lineage = {}
    for name in BASELINES:
        directory = output / f"branches/{name}"
        checkpoint = directory / "checkpoint-0001"
        branch_start = read(directory / "START.json")
        qualification = read(directory / "QUALIFICATION.json")
        state_path = checkpoint / "state.json"
        state = read(state_path)
        commit_path = checkpoint / "STEP_COMMIT.json"
        commit = read(commit_path)
        if (
            branch_start.get("branch") != name
            or branch_start.get("baseline") != BASELINES[name]
            or branch_start.get("parent_adapter_sha256") != CHILD_SHA
            or branch_start.get("shared_collection_sha256") != sha(shared_path)
            or branch_start.get("fresh_optimizer_state_empty") is not True
            or branch_start.get("sequence_reduction") != "sum"
            or branch_start.get("denominator") != 128
        ):
            raise ValueError("branch pre-step receipt differs")
        if (
            qualification.get("branch") != name
            or qualification.get("baseline") != BASELINES[name]
            or qualification.get("all32_passed") is not True
            or qualification.get("computed_before_step") is not True
            or qualification.get("shared_collection_sha256") != sha(shared_path)
            or qualification.get("same_actions_and_masks_for_both_branches") is not True
            or qualification.get("true_onpolicy_c32_before_step") is not True
            or qualification.get("importance_weights_used") is not False
            or qualification.get("sequence_reduction") != "sum"
            or qualification.get("denominator") != 128
            or len(qualification.get("groups", [])) != 32
        ):
            raise ValueError("branch probability qualification differs")
        for index, group_id in enumerate(ordered_ids):
            shared = output / f"shared-collection/groups/group-{index:03d}"
            shared_rollout = read(shared / "ROLLOUT.json")
            if shared_rollout.get("paired_advantages") != expected_advantages[index]:
                raise ValueError("paired advantage math differs")
            replay_path = directory / f"groups/group-{index:03d}/REPLAY.json"
            replay = read(replay_path)
            verify_probability_group(qualification["groups"][index], replay, index)
            if (
                replay.get("branch") != name
                or replay.get("baseline") != BASELINES[name]
                or replay.get("shared_rollout") != str(shared / "ROLLOUT.json")
                or replay.get("shared_rollout_sha256") != sha(shared / "ROLLOUT.json")
                or replay.get("shared_masks_sha256") != sha(shared / "MASKS.npz")
            ):
                raise ValueError("branch replay is not the shared action inventory")
        if (
            state.get("schema") != "helper-hf-onpolicy-other31-paired-state-v1"
            or state.get("branch") != name
            or state.get("baseline") != BASELINES[name]
            or state.get("step") != 1
            or state.get("optimizer_state_steps") != [1]
            or state.get("optimizer") != "fresh AdamW for this branch only"
            or state.get("learning_rate") != 1e-5
            or state.get("weight_decay") != 0
            or state.get("starting_adapter_sha256") != CHILD_SHA
            or state.get("shared_collection_sha256") != sha(shared_path)
            or state.get("qualification_sha256") != sha(directory / "QUALIFICATION.json")
            or state.get("sequence_reduction") != "sum"
            or state.get("denominator") != 128
            or not math.isfinite(state.get("gradient_norm_before_clip", math.nan))
            or state.get("gradient_norm_before_clip", 0) <= 0
            or not math.isfinite(state.get("adapter_delta_l2_from_c32", math.nan))
            or state.get("adapter_delta_l2_from_c32", 0) <= 0
        ):
            raise ValueError("branch checkpoint state differs")
        for filename, expected in state["files_sha256"].items():
            if sha(checkpoint / filename) != expected:
                raise ValueError("state-pinned branch file changed")
        source_eval().verify_optimizer_steps(checkpoint / "optimizer.pt", 1)
        if (
            commit.get("branch") != name
            or commit.get("step") != 1
            or commit.get("ready_identity") != ready["identity"]
            or commit.get("shared_collection_sha256") != sha(shared_path)
            or commit.get("status") != "UPDATED"
        ):
            raise ValueError("branch checkpoint commit header differs")
        verify_hash_map(commit["files_sha256"])
        required = {
            str((checkpoint / filename).resolve())
            for filename in (
                "adapter_model.safetensors",
                "adapter_config.json",
                "optimizer.pt",
                "rng_state.pt",
                "state.json",
                "EVAL_BINDING.json",
            )
        }
        required.add(str((directory / "QUALIFICATION.json").resolve()))
        if not required <= set(commit["files_sha256"]):
            raise ValueError("branch STEP_COMMIT lacks full checkpoint inventory")
        binding = read(checkpoint / "EVAL_BINDING.json")
        verify_binding(
            checkpoint, name, sha(shared_path), sha(state_path), source_binding, binding
        )
        lineage[name] = {
            "checkpoint": str(checkpoint),
            "state_sha256": sha(state_path),
            "step_commit_sha256": sha(commit_path),
            "optimizer_sha256": sha(checkpoint / "optimizer.pt"),
            "rng_sha256": sha(checkpoint / "rng_state.pt"),
            "binding": binding,
            "binding_sha256": sha(checkpoint / "EVAL_BINDING.json"),
        }
    chosen = lineage[branch]
    return {
        "schema": "helper-hf-other31-paired-eval-eligibility-v1",
        "eligible": True,
        "branch": branch,
        "baseline": BASELINES[branch],
        "training_ready_identity": ready["identity"],
        "training_result_sha256": sha(result_path),
        "shared_collection_sha256": sha(shared_path),
        "both_branches_updated_and_authenticated": True,
        "c32_prestep_and_other31_restore_authenticated": True,
        "lineage": {name: {key: value for key, value in row.items() if key != "binding"} for name, row in lineage.items()},
        "checkpoint": chosen["checkpoint"],
        "checkpoint_state_sha256": chosen["state_sha256"],
        "checkpoint_step_commit_sha256": chosen["step_commit_sha256"],
        "binding": chosen["binding"],
        "binding_sha256": chosen["binding_sha256"],
    }


def binding():
    receipt = qualify_pair(resolve_branch())
    if ATTEMPT is not None and ATTEMPT.exists():
        write_x(ATTEMPT / "ELIGIBILITY.json", receipt)
    return receipt["binding"]


def verify(branch=None, require_training=True):
    branch = resolve_branch(branch)
    select(branch)
    ready = read(ready_path(branch))
    for key, expected in plan(branch).items():
        if ready.get(key) != expected:
            raise ValueError("paired evaluator READY plan changed: " + key)
    if digest({key: value for key, value in ready.items() if key != "identity"}) != ready.get(
        "identity"
    ):
        raise ValueError("paired evaluator READY identity differs")
    for raw, expected in ready["closure_sha256"].items():
        if sha(raw) != expected:
            raise ValueError("paired evaluator closure changed: " + raw)
    if require_training:
        qualify_pair(branch)
    return ready
