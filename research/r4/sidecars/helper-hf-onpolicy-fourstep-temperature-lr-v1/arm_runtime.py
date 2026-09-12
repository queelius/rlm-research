"""Isolated, arm-local instrumentation around the sealed four-step implementation."""

import copy
import importlib.util
import math
import sys

import torch

import study


def load_source():
    """Load a fresh source module graph; each GPU owner process configures exactly one arm."""
    names = (
        "config",
        "core",
        "rng_receipts",
        "train_four",
        "runner",
        "train",
        "settings",
        "prepare",
        "policy",
        "grammar_client",
        "grammar_worker",
    )
    for name in names:
        sys.modules.pop(name, None)
    before = list(sys.path)
    try:
        sys.path.insert(0, str(study.REFERENCE))
        spec = importlib.util.spec_from_file_location(
            "paired_arm_source_train_four", study.REFERENCE / "train_four.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path[:] = before


def _arm_public(arm):
    return {
        "name": arm["name"],
        "temperature": arm["temperature"],
        "learning_rate": arm["learning_rate"],
    }


def install(source, arm):
    """Bind one freshly loaded source graph to one arm and add no extra model forwards."""
    public = _arm_public(arm)
    source.ROOT = arm["root"]
    source.CAP = study.CAP
    source.LR = arm["learning_rate"]
    source.core.v1.TEMPERATURE = arm["temperature"]
    raw_write = source.core.write
    original_constrained = source.core.v1.constrained_logprobs
    original_rollout = source.core.v1.rollout_group
    original_replay = source.core.v1.replay_group
    original_execute = source.execute_update
    original_changed_binding = source.core.v1.changed_binding
    state = {
        "phase": None,
        "entropy_calls": [],
        "update_rollouts": [],
        "temperature_paths": set(),
    }

    def annotated_write(path, value):
        value = copy.deepcopy(value)
        if isinstance(value, dict) and path.name in {
            "START.json",
            "COLLECTION.json",
            "QUALIFICATION.json",
            "RESULT.json",
            "REPLAY.json",
            "state.json",
        }:
            value["experimental_arm"] = public
        if isinstance(value, dict) and path.name == "state.json":
            value["schema"] = "helper-hf-onpolicy-fourstep-arm-state-v1"
            value["temperature"] = arm["temperature"]
            value["learning_rate"] = arm["learning_rate"]
            value["poststep_extra_forward_sweep"] = False
        raw_write(path, value)

    def constrained(logits, allowed, temperature):
        if temperature != arm["temperature"]:
            raise ValueError("sampling/replay temperature differs from sealed arm")
        result = original_constrained(logits, allowed, temperature)
        if state["phase"] in {"rollout", "replay"}:
            state["temperature_paths"].add(state["phase"])
        if state["phase"] == "rollout":
            finite = torch.isfinite(result)
            probability = torch.where(finite, result.exp(), torch.zeros_like(result))
            terms = torch.where(finite, -probability * result, torch.zeros_like(result))
            state["entropy_calls"].append(
                (terms.sum(dim=-1).detach(), finite.sum(dim=-1).detach())
            )
        return result

    def rollout(*args, **kwargs):
        state["phase"] = "rollout"
        state["entropy_calls"] = []
        try:
            record = original_rollout(*args, **kwargs)
        finally:
            state["phase"] = None
        calls = state["entropy_calls"]
        if len(calls) != len(record["steps"]):
            raise ValueError("entropy calls do not align with rollout steps")
        entropies = torch.stack([item[0] for item in calls]).cpu().tolist()
        supports = torch.stack([item[1] for item in calls]).cpu().tolist()
        live_total = 0
        nonforced = 0
        entropy_sum = 0.0
        nonforced_entropy_sum = 0.0
        sequence_sums = [0.0] * 4
        for step, entropy_rows, support_rows in zip(
            record["steps"], entropies, supports, strict=True
        ):
            for row, live in enumerate(step["active"]):
                if not live:
                    continue
                live_total += 1
                entropy_sum += entropy_rows[row]
                sequence_sums[row] += step["old_logprobs"][row]
                if support_rows[row] > 1:
                    nonforced += 1
                    nonforced_entropy_sum += entropy_rows[row]
        if live_total != sum(map(len, record["completion_ids"])):
            raise ValueError("live entropy positions differ from sampled completion inventory")
        receipt = {
            "temperature": arm["temperature"],
            "live_positions_total": live_total,
            "live_positions_nonforced": nonforced,
            "entropy_sum_nats": entropy_sum,
            "entropy_mean_nats": entropy_sum / live_total if live_total else 0.0,
            "nonforced_entropy_sum_nats": nonforced_entropy_sum,
            "nonforced_entropy_mean_nats": (
                nonforced_entropy_sum / nonforced if nonforced else 0.0
            ),
            "source": "already-computed constrained sampling logq; no extra model forward",
        }
        if not all(math.isfinite(value) for key, value in receipt.items() if key.endswith("nats")):
            raise ValueError("nonfinite rollout entropy")
        record["branching_entropy"] = receipt
        record["sampled_sequence_logprob_sums"] = sequence_sums
        record["experimental_arm"] = public
        state["update_rollouts"].append(receipt)
        destination = args[6] if len(args) > 6 else kwargs["directory"]
        annotated_write(destination / "ROLLOUT.json", record)
        return record

    def replay(*args, **kwargs):
        state["phase"] = "replay"
        try:
            result = original_replay(*args, **kwargs)
        finally:
            state["phase"] = None
        result["experimental_arm"] = public
        result["temperature_path_attested"] = True
        destination = args[5] if len(args) > 5 else kwargs["directory"]
        annotated_write(destination / "REPLAY.json", result)
        return result

    def execute(*args, **kwargs):
        optimizer = args[1] if len(args) > 1 else kwargs["optimizer"]
        observed_lrs = {group["lr"] for group in optimizer.param_groups}
        if observed_lrs != {arm["learning_rate"]}:
            raise ValueError("actual optimizer learning rate differs from sealed arm")
        state["update_rollouts"] = []
        result = original_execute(*args, **kwargs)
        directory = args[8] if len(args) > 8 else kwargs["directory"]
        collection_path = directory / "COLLECTION.json"
        if collection_path.exists():
            collection = source.core.read(collection_path)
            rows = state["update_rollouts"]
            total = sum(row["live_positions_total"] for row in rows)
            nonforced = sum(row["live_positions_nonforced"] for row in rows)
            entropy_sum = sum(row["entropy_sum_nats"] for row in rows)
            nonforced_sum = sum(row["nonforced_entropy_sum_nats"] for row in rows)
            collection["branching_entropy"] = {
                "groups": len(rows),
                "temperature": arm["temperature"],
                "live_positions_total": total,
                "live_positions_nonforced": nonforced,
                "entropy_sum_nats": entropy_sum,
                "entropy_mean_nats": entropy_sum / total if total else 0.0,
                "nonforced_entropy_sum_nats": nonforced_sum,
                "nonforced_entropy_mean_nats": nonforced_sum / nonforced if nonforced else 0.0,
                "source": "aggregated live rollout receipts; no extra model forward",
            }
            collection["poststep_extra_forward_sweep"] = False
            annotated_write(collection_path, collection)
            result["collection"] = collection
        return result

    def changed_binding(binding, child, update):
        update = copy.deepcopy(update)
        update["experimental_arm"] = public
        update["fixed_training_seeds"] = study.plan(arm["name"])["seeds"]
        return original_changed_binding(binding, child, update)

    source.core.write = annotated_write
    source.core.v1.write_json = annotated_write
    source.core.v1.constrained_logprobs = constrained
    source.core.v1.rollout_group = rollout
    source.core.v1.replay_group = replay
    source.core.v1.changed_binding = changed_binding
    source.execute_update = execute
    return state
