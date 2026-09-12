"""Conditional fixed-panel readout of the LR10x policy stopped after checkpoint 3."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
UPSTREAM = SIDE / "helper-hf-fourstep-temperature-lr-unseen-eval-v1"
TRAINING = SIDE / "helper-hf-onpolicy-fourstep-temperature-lr-v1"
OUTPUT = TRAINING / "arms/t1-lr1e4/outputs/attempt-001"
ATTEMPT = ROOT / "outputs/attempt-001"
SOURCE_BINDING = SIDE / "root-qs6-feedback-diagnostic-v1/outputs/attempt-001/service/BINDING.json"
NATIVE = Path("/project/alex_phd/envs/prime-rl-5990b1b/bin/python")
CAP = 600
ARM = {"name": "t1_lr1e4", "temperature": 1.0, "learning_rate": 1e-4}
CHILD_ALIAS = "strict-rlm-qwen3-4b-role-sft-selected-v1"
CHILD_SHA = "c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3"


def read(path): return json.loads(Path(path).read_text())
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def write_x(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if path.exists():
        if path.read_text() != rendered: raise ValueError("immutable file differs: " + str(path))
    else:
        with path.open("x") as stream: stream.write(rendered)


def _load_upstream():
    sys.path.insert(0, str(UPSTREAM))
    try:
        spec = importlib.util.spec_from_file_location("stopped_step3_upstream", UPSTREAM / "arm_eval_study_v3.py")
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module
    finally:
        sys.path.remove(str(UPSTREAM))


upstream = _load_upstream()
base = upstream.corrected.base
C32 = base.C32
MODEL = base.MODEL
PANEL = base.PANEL
panel = base.panel
schedule = base.schedule
dependencies = base.dependencies


def _terminal_entries(result):
    expected = OUTPUT / "checkpoint-0003"
    if (result.get("status") != "STOP_ZERO_ADVANTAGE" or
            result.get("completed_optimizer_steps") != 3 or
            result.get("current_step_applied") is not False or
            result.get("primary_checkpoint_available") is not False or
            result.get("primary_checkpoint") is not None or
            result.get("primary_checkpoint_step") is not None):
        raise ValueError("exact zero-advantage step3 terminal required")
    entries = result.get("checkpoints")
    if not isinstance(entries, list) or [x.get("step") for x in entries] != [1, 2, 3]:
        raise ValueError("exact committed checkpoint inventory [1,2,3] required")
    if Path(entries[-1].get("checkpoint", "")).resolve() != expected.resolve():
        raise ValueError("terminal last checkpoint is not exact checkpoint-0003")
    if (OUTPUT / "checkpoint-0004").exists():
        raise ValueError("checkpoint-0004 exists despite stopped-policy condition")
    return entries


def _validate_update4(parent_identity, ready_identity, frozen_ids):
    update = OUTPUT / "updates/update-0004"
    start = read(update / "START.json"); collection = read(update / "COLLECTION.json")
    qualification = read(update / "QUALIFICATION.json"); terminal = read(update / "RESULT.json")
    if (start.get("step") != 4 or start.get("parent_identity") != parent_identity or
            start.get("ready_identity") != ready_identity or start.get("experimental_arm") != ARM or
            len(start.get("group_ids", [])) != 32 or set(start["group_ids"]) != frozen_ids):
        raise ValueError("update4 start differs")
    if (collection.get("groups") != 32 or collection.get("samples") != 128 or
            collection.get("correct") != 120.0 or collection.get("mixed_reward_groups") != 0 or
            collection.get("fresh_actions") is not True or collection.get("terminated") != 128 or
            collection.get("optimizer_steps_at_collection") != 3 or
            collection.get("parent_identity") != parent_identity or
            collection.get("start_sha256") != sha(update / "START.json") or
            collection.get("start_rng_sha256") != sha(update / "START_RNG.pt") or
            collection.get("experimental_arm") != ARM or
            collection.get("branching_entropy", {}).get("temperature") != 1.0):
        raise ValueError("update4 collection differs")
    groups = qualification.get("groups", [])
    if (qualification.get("all_passed") is not True or qualification.get("step") != 4 or
            qualification.get("computed_before_step") is not True or
            qualification.get("historical_behavior_probabilities_used") is not False or
            qualification.get("parent_identity") != parent_identity or len(groups) != 32):
        raise ValueError("update4 qualification differs")
    rewards = []
    group_patterns = []
    for index, group_id in enumerate(start["group_ids"]):
        directory = update / "groups" / f"group-{index:03d}"
        commit = read(directory / "GROUP_COMMIT.json")
        if (commit.get("step") != 4 or commit.get("group_index") != index or
                commit.get("group_id") != group_id or commit.get("parent_identity") != parent_identity or
                commit.get("ready_identity") != ready_identity):
            raise ValueError("update4 group lineage differs")
        base.source_eval().verify_hash_map(commit["files_sha256"])
        if collection["group_commit_sha256"].get(str(directory / "GROUP_COMMIT.json")) != sha(directory / "GROUP_COMMIT.json"):
            raise ValueError("update4 group commit hash differs")
        replay = read(directory / "REPLAY.json")
        base.source_eval().verify_probability_group(groups[index], index, replay)
        rollout = read(directory / "ROLLOUT.json")
        row = rollout.get("rewards")
        if not isinstance(row, list) or len(row) != 4 or any(x not in (0.0, 1.0) for x in row):
            raise ValueError("update4 reward row differs")
        if rollout.get("advantages") != [0.0] * 4 or replay.get("backward_steps") != 0:
            raise ValueError("update4 zero-RLOO evidence differs")
        rewards.extend(row); group_patterns.append(row)
    if sum(rewards) != 120.0 or sum(all(x == 1.0 for x in row) for row in group_patterns) != 30 or sum(all(x == 0.0 for x in row) for row in group_patterns) != 2:
        raise ValueError("update4 reward pattern differs")
    terminal_qualification = copy.deepcopy(qualification); terminal_qualification.pop("experimental_arm", None)
    if (terminal.get("status") != "STOP_ZERO_ADVANTAGE" or
            terminal.get("optimizer_step_applied") is not False or
            terminal.get("experimental_arm") != ARM or terminal.get("collection") != collection or
            terminal.get("qualification") != terminal_qualification):
        raise ValueError("update4 terminal differs")
    total = math.fsum(rewards)
    other31 = [(reward - ((total - math.fsum(row)) / 124.0)) for row in group_patterns for reward in row]
    if any(value == 0 for value in other31): raise ValueError("unexpected zero other31 hypothetical advantage")
    return {
        "schema": "lr10x-update4-action-eligibility-v1",
        "source": str(update), "source_hashes": {name: sha(update / name) for name in
            ("START.json", "START_RNG.pt", "COLLECTION.json", "QUALIFICATION.json", "RESULT.json")},
        "checkpoint_parent_identity": parent_identity, "fresh_actions": 128,
        "probability_qualified_actions": 128, "correct_actions": 120, "wrong_actions": 8,
        "all_correct_groups": 30, "all_wrong_groups": 2, "mixed_groups": 0,
        "within_question_rloo_nonzero_actions": 0,
        "hypothetical_other31_nonzero_actions": 128,
        "hypothetical_other31_positive_actions": sum(x > 0 for x in other31),
        "hypothetical_other31_negative_actions": sum(x < 0 for x in other31),
        "hypothetical_other31_positive_value": max(x for x in other31 if x > 0),
        "hypothetical_other31_negative_value": min(x for x in other31 if x < 0),
        "interpretation": "Saved checkpoint-3 on-policy actions are probability-qualified. Reuse with a detached other31 baseline is a different, unapproved objective; this receipt does not authorize an optimizer step.",
    }


def qualify():
    arm = base.ARMS["t1_lr1e4"]; ready_path = base.TRAINING / arm["training_ready"]
    ready = read(ready_path)
    if sha(ready_path) != arm["training_ready_sha256"] or ready.get("identity") != arm["training_ready_identity"]:
        raise ValueError("unexpected LR10x training READY")
    for path, expected in ready["closure_sha256"].items():
        if sha(path) != expected: raise ValueError("training closure changed: " + path)
    result_path = OUTPUT / "RESULT.json"; entries = _terminal_entries(read(result_path))
    receipt_path = OUTPUT / "ARM_RUNTIME_RECEIPT.json"; receipt = read(receipt_path)
    if (receipt.get("ready_identity") != ready["identity"] or receipt.get("experimental_arm") != ARM or
            receipt.get("temperature_paths") != ["replay", "rollout"] or
            receipt.get("poststep_extra_forward_sweep") is not False):
        raise ValueError("LR10x runtime receipt differs")
    start = read(OUTPUT / "START.json")
    if (start.get("ready_identity") != ready["identity"] or start.get("requested_updates") != 4 or
            start.get("primary_checkpoint_step") != 4 or start.get("starting_child_adapter_sha256") != CHILD_SHA or
            start.get("experimental_arm") != ARM):
        raise ValueError("LR10x training START differs")
    source_binding = read(SOURCE_BINDING); frozen_ids = {x["group_id"] for x in read(base.REFERENCE / "inputs/GROUPS.json")}
    parent_identity = CHILD_SHA; parent_commit = None; lineage = []; binding = None
    for step, entry in enumerate(entries, 1):
        checkpoint = OUTPUT / f"checkpoint-{step:04d}"; update = OUTPUT / "updates" / f"update-{step:04d}"
        state_path = checkpoint / "state.json"; commit_path = checkpoint / "STEP_COMMIT.json"
        state, commit = read(state_path), read(commit_path)
        if entry.get("state_sha256") != sha(state_path) or entry.get("step_commit") != {"path": str(commit_path), "sha256": sha(commit_path)}:
            raise ValueError("RESULT checkpoint receipt differs")
        base.source_eval().validate_lineage_header(step, state, commit, parent_identity, parent_commit, ready["identity"])
        base.validate_arm_state("t1_lr1e4", state)
        for filename, expected in state["files_sha256"].items():
            if sha(checkpoint / filename) != expected: raise ValueError("checkpoint file changed")
        base.source_eval().verify_hash_map(commit["files_sha256"])
        base.source_eval().verify_optimizer_steps(checkpoint / "optimizer.pt", step)
        # The upstream arm validator authenticates each applied collection, replay, and binding.
        start_u, collection, qualification = (read(update / name) for name in ("START.json", "COLLECTION.json", "QUALIFICATION.json"))
        if start_u.get("parent_identity") != parent_identity or collection.get("parent_identity") != parent_identity or qualification.get("parent_identity") != parent_identity:
            raise ValueError("applied update parent differs")
        for index, group_id in enumerate(start_u["group_ids"]):
            directory = update / "groups" / f"group-{index:03d}"
            base.source_eval().verify_probability_group(qualification["groups"][index], index, read(directory / "REPLAY.json"))
        binding = upstream.corrected.verify_binding(checkpoint, state, source_binding, step, "t1_lr1e4")
        lineage.append({"step": step, "checkpoint": str(checkpoint), "state_sha256": sha(state_path),
            "step_commit_sha256": sha(commit_path), "collection_sha256": sha(update / "COLLECTION.json"),
            "qualification_sha256": sha(update / "QUALIFICATION.json")})
        parent_identity = sha(state_path); parent_commit = {"path": str(commit_path), "sha256": sha(commit_path)}
    action_receipt = _validate_update4(parent_identity, ready["identity"], frozen_ids)
    checkpoint = OUTPUT / "checkpoint-0003"
    return {"eligible": True, "policy": "adaptive stopped policy checkpoint-0003",
        "fixed_fourstep_primary": False, "selection": "mechanistic terminal stop, not metric selection",
        "stop_reason": "STOP_ZERO_ADVANTAGE", "completed_optimizer_steps": 3,
        "training_ready_identity": ready["identity"], "training_result_sha256": sha(result_path),
        "arm_runtime_receipt_sha256": sha(receipt_path), "lineage": lineage,
        "checkpoint": str(checkpoint), "checkpoint_state_sha256": sha(checkpoint / "state.json"),
        "binding": binding, "binding_sha256": sha(checkpoint / "EVAL_BINDING.json"),
        "update4_action_eligibility": action_receipt}


def binding():
    receipt = qualify()
    if ATTEMPT.exists():
        write_x(ATTEMPT / "ELIGIBILITY.json", {k: v for k, v in receipt.items() if k != "update4_action_eligibility"})
        write_x(ATTEMPT / "UPDATE4_ACTION_ELIGIBILITY.json", receipt["update4_action_eligibility"])
    return receipt["binding"]


def verify(require_training=True):
    ready = read(ROOT / "READY.json")
    if ready.get("status") != "CPU_READY_CONDITIONAL_EXACT_LR10X_ZERO_ADVANTAGE_STEP3":
        raise ValueError("unexpected stopped-policy eval READY status")
    if digest({k: v for k, v in ready.items() if k != "identity"}) != ready.get("identity"):
        raise ValueError("READY identity differs")
    for path, expected in ready["closure_sha256"].items():
        if sha(path) != expected: raise ValueError("eval closure changed: " + path)
    if digest(schedule()) != ready["schedule_sha256"]: raise ValueError("fixed256 schedule changed")
    if require_training: qualify()
    return ready
