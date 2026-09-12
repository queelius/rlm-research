"""Additive missing-RNG-export repair, with exact committed HF action reuse."""

import argparse
import ast
import copy
import importlib.util
import math
import random
import shutil
import sys
import types
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parent
V1 = ROOT.parent / "helper-hf-onpolicy-other31-paired-onestep-v1"
FAILED = V1 / "outputs/attempt-001"


def load(name, path, aliases=None):
    prior = {key: sys.modules.get(key) for key in (aliases or {})}
    sys.modules.update(aliases or {})
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        for key, value in prior.items():
            if value is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = value


old = load("paired_repair_old_study", V1 / "study.py")
maths = load("paired_repair_old_math", V1 / "pair_math.py")
old_source = load("paired_repair_old_source", V1 / "source.py", {"study": old})
original = load(
    "paired_repair_original_trainer",
    V1 / "train_pair.py",
    {"study": old, "source": old_source, "pair_math": maths},
)


def implementation():
    value = old_source.load()
    # save_rng already originates in the sealed module containing this exact function.
    value.restore_rng = value.save_rng.__globals__["restore_rng"]
    return value


def equal_state(a, b):
    if isinstance(a, torch.Tensor):
        return isinstance(b, torch.Tensor) and torch.equal(a.cpu(), b.cpu())
    if isinstance(a, np.ndarray):
        return isinstance(b, np.ndarray) and np.array_equal(a, b)
    if isinstance(a, dict):
        return isinstance(b, dict) and set(a) == set(b) and all(equal_state(a[k], b[k]) for k in a)
    if isinstance(a, (list, tuple)):
        return (
            isinstance(b, type(a))
            and len(a) == len(b)
            and all(equal_state(x, y) for x, y in zip(a, b, strict=True))
        )
    return a == b


def initialize_branch(impl, model, snapshot, rng_path, generator):
    maths.restore_snapshot(model, snapshot)
    impl.restore_rng(rng_path, generator)
    expected = torch.load(rng_path, map_location="cpu", weights_only=False)
    actual = {
        "python": random.getstate(),
        "numpy": np.random.get_state(),
        "torch": torch.get_rng_state(),
        "cuda": torch.cuda.get_rng_state_all(),
        "sampling_generator": generator.get_state(),
        "sampling_device": str(generator.device),
    }
    if not equal_state(expected, actual):
        raise ValueError("actual branch RNG restoration differs")
    optimizer = torch.optim.AdamW(
        [p for _, p in impl.trainable_parameters(model)], lr=1e-5, weight_decay=0
    )
    if optimizer.state:
        raise ValueError("branch optimizer is not fresh")
    return optimizer, {
        "rng_identical": True,
        "rng_source_sha256": old.sha(rng_path),
        "trainable_tensor_identity_sha256": maths.snapshot_digest(snapshot),
        "optimizer_state_empty": True,
        "learning_rate": 1e-5,
        "weight_decay": 0,
    }


def validate_source(impl=None):
    impl = implementation() if impl is None else impl
    ready = old.verify()
    failure = old.read(FAILED / "FAILURE.json")
    if (
        failure != old.read(FAILED / "RESULT.json")
        or failure.get("status") != "STOP_FAILED"
        or failure.get("completed_branches") != []
    ):
        raise ValueError("source must be the observed pre-branch failure")
    if (
        failure.get("error_type") != "AttributeError"
        or failure.get("error")
        != "module 'other31_source_train_four' has no attribute 'restore_rng'"
    ):
        raise ValueError("source is not the diagnosed missing RNG export")
    if (
        (FAILED / "branches").exists()
        or list(FAILED.rglob("optimizer.pt"))
        or list(FAILED.rglob("checkpoint-*"))
    ):
        raise ValueError("source unexpectedly reached a branch/update")
    if old.read(FAILED / "START.json")["ready_identity"] != ready["identity"]:
        raise ValueError("source started with a different READY")
    collection = old.read(FAILED / "shared-collection/COLLECTION.json")
    if (
        collection["actions"] != 128
        or collection["groups"] != 32
        or collection["optimizer_created_during_collection"] is not False
        or collection["parent_adapter_sha256"] != impl.CHILD_SHA
        or collection["temperature"] != 1.0
    ):
        raise ValueError("source was not complete frozen-c32 collection")
    groups = old.read(V1 / "inputs/GROUPS.json")
    gold = old.read(V1 / "inputs/TRAIN_GOLD.json")
    order = list(range(32))
    random.Random(old.PERMUTATION_SEED).shuffle(order)
    if order != collection["group_source_indices"]:
        raise ValueError("source order changed")
    ordered = [groups[index] for index in order]
    records, pins = [], {}
    for path in [
        V1 / "READY.json",
        FAILED / "START.json",
        FAILED / "FAILURE.json",
        FAILED / "RESULT.json",
        FAILED / "C32_SNAPSHOT.json",
        FAILED / "C32_TRAINABLE_SNAPSHOT.pt",
        *sorted((FAILED / "shared-collection").glob("*.*")),
    ]:
        if path.is_file():
            pins[str(path)] = old.sha(path)
    inventory = collection["action_inventory"]
    for index, group in enumerate(ordered):
        directory = FAILED / f"shared-collection/groups/group-{index:03d}"
        path = directory / "GROUP_COMMIT.json"
        commit = old.read(path)
        if (
            old.sha(path) != collection["group_commit_sha256"][str(path)]
            or commit["ready_identity"] != ready["identity"]
            or commit["parent_identity"] != impl.CHILD_SHA
            or commit["group_index"] != index
            or commit["group_id"] != group["group_id"]
        ):
            raise ValueError("source group commit identity differs")
        pins[str(path)] = old.sha(path)
        for raw, expected in commit["files_sha256"].items():
            if old.sha(raw) != expected:
                raise ValueError("source group artifact changed")
            pins[raw] = expected
        record = old.read(directory / "ROLLOUT.json")
        expected = inventory[index]
        if (
            record["group_id"] != group["group_id"]
            or record["group_index"] != index
            or record["schema_sha256"] != group["schema_ordered_sha256"]
            or old.sha(directory / "MASKS.npz") != record["masks_sha256"]
        ):
            raise ValueError("source group/schema/masks differ")
        completions = [[] for _ in range(4)]
        for step in record["steps"]:
            if any(len(step[k]) != 4 for k in ("actions", "active", "old_logprobs")):
                raise ValueError("source B4 differs")
            for row, active in enumerate(step["active"]):
                if not math.isfinite(step["old_logprobs"][row]):
                    raise ValueError("nonfinite source log probability")
                if active:
                    completions[row].append(step["actions"][row])
                elif (
                    step["actions"][row] != impl.core.v1.STOP_IDS[0]
                    or step["old_logprobs"][row] != 0
                ):
                    raise ValueError("inactive source action differs")
        rewards = [
            impl.core.v1.local_reward(
                text, group["public_record"]["id"], gold[group["group_id"]], terminated
            )
            for text, terminated in zip(record["contents"], record["terminated"], strict=True)
        ]
        if (
            completions != record["completion_ids"]
            or rewards != record["rewards"]
            or expected["completion_ids"] != completions
            or expected["rewards"] != rewards
            or expected["rollout_sha256"] != old.sha(directory / "ROLLOUT.json")
            or expected["masks_sha256"] != record["masks_sha256"]
            or expected["commit_sha256"] != old.sha(path)
        ):
            raise ValueError("source actions/rewards/inventory differ")
        records.append(record)
    advantages = maths.paired_advantages([record["rewards"] for record in records])
    if any(
        record["paired_advantages"] != expected
        for record, expected in zip(records, advantages, strict=True)
    ):
        raise ValueError("source paired advantage math differs")
    if (
        sum(sum(record["rewards"]) for record in records) != collection["correct"]
        or sum(len(set(record["rewards"])) > 1 for record in records) != collection["mixed_groups"]
    ):
        raise ValueError("source collection aggregates differ")
    if (
        old.sha(FAILED / "shared-collection/AFTER_COLLECTION_RNG.pt")
        != collection["after_collection_rng_sha256"]
    ):
        raise ValueError("after-collection RNG changed")
    snapshot = torch.load(
        FAILED / "C32_TRAINABLE_SNAPSHOT.pt", map_location="cpu", weights_only=True
    )
    receipt = old.read(FAILED / "C32_SNAPSHOT.json")
    if receipt["serialized_sha256"] != old.sha(FAILED / "C32_TRAINABLE_SNAPSHOT.pt") or receipt[
        "tensor_identity_sha256"
    ] != maths.snapshot_digest(snapshot):
        raise ValueError("source c32 tensor snapshot differs")
    proof = {
        "source_attempt": str(FAILED),
        "source_ready_identity": ready["identity"],
        "source_ready_sha256": old.sha(V1 / "READY.json"),
        "source_files_sha256": pins,
        "source_collection_sha256": old.sha(FAILED / "shared-collection/COLLECTION.json"),
        "source_tensor_identity_sha256": receipt["tensor_identity_sha256"],
        "actions": 128,
        "groups": 32,
        "correct": collection["correct"],
        "mixed_groups": collection["mixed_groups"],
        "all_failure_group_ids": collection["all_failure_group_ids"],
        "completed_branches": [],
        "source_optimizer_steps": 0,
        "source_elapsed_seconds": failure["elapsed_seconds"],
        "source_reusable_conditionally": "Both new branches must pass all32 unchanged "
        "exact-policy replay gates before their step.",
    }
    return proof, ordered, records, collection


def reuse_collection(impl, model, _worker, tokenizer, groups, _gold, _generator, output, ready):
    proof, ordered, records, original_collection = validate_source(impl)
    actual = maths.snapshot_digest(maths.snapshot_trainable(model))
    if actual != proof["source_tensor_identity_sha256"]:
        raise ValueError("freshly loaded c32 differs from source sampling tensors")
    if groups != old.read(V1 / "inputs/GROUPS.json"):
        raise ValueError("repair training input changed")
    for record in records:
        if [
            tokenizer.decode(ids, skip_special_tokens=True) for ids in record["completion_ids"]
        ] != record["contents"]:
            raise ValueError("source completion tokens do not decode to saved reward content")
    directory = output / "shared-collection"
    directory.mkdir()
    for name in ("START_RNG.pt", "AFTER_COLLECTION_RNG.pt"):
        shutil.copyfile(FAILED / "shared-collection" / name, directory / name)
    old.write(
        directory / "START.json",
        {
            "ready_identity": ready["identity"],
            "source_reuse": proof,
            "fresh_model_calls_in_repair": 0,
            "planned_actions": 128,
        },
    )
    collection = copy.deepcopy(original_collection)
    collection.update(
        freshly_sampled=False,
        reused_exact_hf_actions=True,
        fresh_model_calls_in_repair=0,
        source_reuse=proof,
        source_sampling_was_fresh=True,
        group_commit_sha256={},
    )
    for index, record in enumerate(records):
        target = directory / f"groups/group-{index:03d}"
        target.mkdir(parents=True)
        source_dir = FAILED / f"shared-collection/groups/group-{index:03d}"
        for name in ("ROLLOUT.json", "MASKS.npz", "AFTER_GROUP_RNG.pt"):
            shutil.copyfile(source_dir / name, target / name)
        impl.commit_files(
            target / "GROUP_COMMIT.json",
            [target / name for name in ("ROLLOUT.json", "MASKS.npz", "AFTER_GROUP_RNG.pt")],
            {
                "ready_identity": ready["identity"],
                "parent_identity": impl.CHILD_SHA,
                "group_index": index,
                "group_id": record["group_id"],
                "actions_shared_by_both_branches": True,
                "source_commit_sha256": old.sha(source_dir / "GROUP_COMMIT.json"),
            },
        )
        commit_sha = old.sha(target / "GROUP_COMMIT.json")
        collection["group_commit_sha256"][str(target / "GROUP_COMMIT.json")] = commit_sha
        collection["action_inventory"][index]["commit_sha256"] = commit_sha
    old.write(directory / "COLLECTION.json", collection)
    old.write(output / "SOURCE_REUSE.json", proof)
    return ordered, records, collection


def plan():
    value = old.plan()
    value.update(
        schema="helper-hf-other31-paired-repair-ready-v2",
        output=str(ROOT / "outputs/attempt-001"),
        command=[
            str(old.TRAIN_PYTHON),
            str(ROOT / "repair.py"),
            "run",
            "--cap-seconds",
            str(old.CAP),
        ],
    )
    value["inventory"] = {
        **value["inventory"],
        "shared_fresh_actions": 0,
        "reused_exact_hf_actions": 128,
    }
    value["repair"] = (
        "Missing restore_rng export only; new local receipts for unchanged source actions."
    )
    return value


def verify():
    ready = old.read(ROOT / "READY.json")
    if old.digest({k: v for k, v in ready.items() if k != "identity"}) != ready["identity"]:
        raise ValueError("V2 READY identity differs")
    for key, expected in plan().items():
        if ready.get(key) != expected:
            raise ValueError("V2 fixed plan differs")
    for path, expected in ready["closure_sha256"].items():
        if old.sha(path) != expected:
            raise ValueError("V2 closure changed: " + path)
    return ready


def build():
    study = types.SimpleNamespace(**{k: v for k, v in vars(old).items() if not k.startswith("__")})
    study.ROOT, study.OUTPUT, study.verify, study.plan = (
        ROOT,
        ROOT / "outputs/attempt-001",
        verify,
        plan,
    )
    module = types.ModuleType("paired_v2_exact_original_branch_runner")
    module.__dict__.update(vars(original))
    module.study = study
    module.source = types.SimpleNamespace(load=implementation)
    module._collect = reuse_collection
    module.initialize_branch = initialize_branch
    text = (V1 / "train_pair.py").read_text()
    before = """    optimizer = torch.optim.AdamW(
        [parameter for _, parameter in implementation.trainable_parameters(model)],
        lr=1e-5,
        weight_decay=0,
    )"""
    after = """    optimizer, initial_receipt = initialize_branch(
        implementation, model, snapshot,
        output / "shared-collection/AFTER_COLLECTION_RNG.pt", generator)
    implementation.core.write(directory / "BRANCH_INITIAL_STATE.json", initial_receipt)"""
    if text.count(before) != 1:
        raise ValueError("sealed branch optimizer-initialization seam changed")
    tree = ast.parse(text.replace(before, after))
    functions = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in ("run", "_branch")
    ]
    if len(functions) != 2:
        raise ValueError("sealed runner functions missing")
    exec(
        compile(
            ast.Module(body=functions, type_ignores=[]), str(V1 / "train_pair.py") + ":v2", "exec"
        ),
        module.__dict__,
    )
    return module


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--cap-seconds", type=int, default=old.CAP)
    args = parser.parse_args()
    if args.command == "verify":
        print(verify()["identity"])
    else:
        print(build().run(ROOT / "outputs/attempt-001", args.cap_seconds))
