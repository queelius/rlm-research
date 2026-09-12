"""Train-only reward-credit and committed SFT-loss audit; never reads heldout512."""

import collections
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
STORE = ROOT.parents[1]
SIDE = STORE / "sidecars"
ARMS = {
    "seed1": SIDE / "helper-agnews-native-hf-onestep-v1",
    "seed2": SIDE / "helper-agnews-native-hf-onestep-seed2-v1",
}
SFT = SIDE / "helper-agnews-sft-eightstep-v1"


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_x(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def rloo(values):
    return [value - (sum(values) - value) / (len(values) - 1) for value in values]


def reward_arm(path):
    output = path / "outputs/attempt-001"
    collection_path, gold_path = output / "COLLECTION.json", path / "inputs/HOST_GOLD.json"
    rows, gold = read(collection_path)["records"], read(gold_path)
    groups = collections.defaultdict(list)
    for row in rows:
        expected = [
            row["prediction"][identifier] == gold[row["context_id"]]["labels"][identifier]
            for identifier in row["requested_ids"]
        ]
        if sum(expected) != row["correct_count"] or not math.isclose(row["reward"], sum(expected) / 4):
            raise ValueError("saved map/count reward differs from host truth")
        groups[row["context_id"]].append((row, expected))
    if len(rows) != 128 or len(groups) != 32 or any(len(values) != 4 for values in groups.values()):
        raise ValueError("expected exact 32x4 complete action inventory")
    count_types, item_variable_groups = collections.Counter(), 0
    constant_count_with_item_swaps = 0
    variable_item_positions = nonzero_item_action_cells = nonzero_sequence_actions = 0
    max_scalar_decomposition_error = 0.0
    examples = []
    for context, values in groups.items():
        records = [value[0] for value in values]
        binary = [value[1] for value in values]
        counts = [record["correct_count"] for record in records]
        if max(counts) == 0:
            kind = "all_wrong"
        elif min(counts) == 4:
            kind = "all_correct"
        elif len(set(counts)) > 1:
            kind = "mixed_count"
        else:
            kind = "constant_partial_" + str(counts[0])
        count_types[kind] += 1
        count_advantages = rloo(counts)
        nonzero_sequence_actions += sum(abs(value) > 1e-12 for value in count_advantages)
        item_advantages = []
        variable = []
        for position, identifier in enumerate(records[0]["requested_ids"]):
            outcomes = [int(row[position]) for row in binary]
            advantages = rloo(outcomes)
            item_advantages.append(advantages)
            if len(set(outcomes)) > 1:
                variable.append({"id": identifier, "outcomes": outcomes})
                variable_item_positions += 1
                nonzero_item_action_cells += sum(abs(value) > 1e-12 for value in advantages)
        reconstructed = [sum(item_advantages[position][action] for position in range(4)) for action in range(4)]
        max_scalar_decomposition_error = max(
            max_scalar_decomposition_error,
            max(abs(a - b) for a, b in zip(count_advantages, reconstructed, strict=True)),
        )
        if variable:
            item_variable_groups += 1
            if len(set(counts)) == 1:
                constant_count_with_item_swaps += 1
                examples.append({"context_id": context, "counts": counts, "variable_items": variable})
    result = read(output / "RESULT.json")
    return {
        "collection_sha256": sha(collection_path),
        "host_gold_sha256": sha(gold_path),
        "result_sha256": sha(output / "RESULT.json"),
        "actions": len(rows),
        "correct_item_decisions": sum(row[0]["correct_count"] for values in groups.values() for row in values),
        "item_decisions": 512,
        "count_group_types": dict(count_types),
        "count_informative_groups": count_types["mixed_count"],
        "item_variable_groups": item_variable_groups,
        "constant_count_groups_with_item_swaps": constant_count_with_item_swaps,
        "variable_item_positions": variable_item_positions,
        "nonzero_count_rloo_actions": nonzero_sequence_actions,
        "nonzero_item_rloo_action_cells": nonzero_item_action_cells,
        "max_sequence_count_advantage_vs_sum_item_advantages_error": max_scalar_decomposition_error,
        "constant_count_swap_examples": examples,
        "gradient_norm": result["gradient_norm_before_clip"],
        "adapter_delta_l2": result["adapter_delta_l2"],
        "hf_elapsed_seconds": result["elapsed_seconds"],
    }


def sft_signal():
    attempt = SFT / "outputs/attempt-001"
    checkpoints = sorted(attempt.glob("checkpoint-*/state.json"))
    metrics = []
    for path in checkpoints:
        state = read(path)
        metric = state["step_metrics"][-1]
        label_tokens = metric["label_tokens"]
        structure_tokens = metric["supervised_tokens"] - label_tokens
        metrics.append(
            {
                **metric,
                "label_mean_nll": metric["label_nll_sum"] / label_tokens,
                "structure_mean_nll": metric["structure_nll_sum"] / structure_tokens,
                "label_fraction_of_supervised_tokens": label_tokens / metric["supervised_tokens"],
                "label_fraction_of_loss_mass": metric["label_nll_sum"] / (metric["label_nll_sum"] + metric["structure_nll_sum"]),
                "state_sha256": sha(path),
                "commit_sha256": sha(path.with_name("STEP_COMMIT.json")),
            }
        )
    result_path, terminal_path = attempt / "RESULT.json", attempt / "OWNER_TERMINAL.json"
    return {
        "committed_steps": len(checkpoints),
        "metrics": metrics,
        "complete": result_path.exists() and terminal_path.exists() and read(terminal_path).get("complete") is True,
        "result_sha256": sha(result_path) if result_path.exists() else None,
        "terminal_sha256": sha(terminal_path) if terminal_path.exists() else None,
        "ready_v2_sha256": sha(SFT / "READY_V2.json"),
        "inner_label_overlap_definition": "tokens whose character offsets overlap label text excluding JSON quotes",
        "gradient_credit_decomposition_available": False,
        "gradient_credit_caveat": "loss mass is not parameter-gradient contribution; no separate gradient sweeps were run",
    }


def main():
    arms = {name: reward_arm(path) for name, path in ARMS.items()}
    rows = {
        name: read(path / "outputs/attempt-001/COLLECTION.json")["records"]
        for name, path in ARMS.items()
    }
    paired = list(zip(rows["seed1"], rows["seed2"], strict=True))
    mixed = {
        name: {
            context
            for context in {row["context_id"] for row in values}
            if len({row["correct_count"] for row in values if row["context_id"] == context}) > 1
        }
        for name, values in rows.items()
    }
    report = {
        "schema": "agnews-train-only-credit-and-sft-signal-v1",
        "scope": "training records only; heldout512 not read",
        "arms": arms,
        "cross_seed": {
            "paired_actions": len(paired),
            "byte_identical_decoded_maps": sum(a["decoded_text"] == b["decoded_text"] for a, b in paired),
            "identical_prediction_maps": sum(a["prediction"] == b["prediction"] for a, b in paired),
            "identical_correct_counts": sum(a["correct_count"] == b["correct_count"] for a, b in paired),
            "mixed_context_union": len(mixed["seed1"] | mixed["seed2"]),
            "mixed_context_intersection": len(mixed["seed1"] & mixed["seed2"]),
        },
        "sft": sft_signal(),
        "credit_conclusion": (
            "For these saved maps, item-level binary decomposition adds no informative group: "
            "every item-variable group is already count-variable, and sequence-level summed item RLOO "
            "is algebraically identical to correct-count RLOO. Token-local credit would change where "
            "the same advantage is applied, but not which groups are nonzero here."
        ),
    }
    write_x(ROOT / "RESULTS.json", report)
    print(json.dumps({"results_sha256": sha(ROOT / "RESULTS.json"), "sft_steps": report["sft"]["committed_steps"], "count_groups": {k: v["count_informative_groups"] for k, v in arms.items()}}, sort_keys=True))


if __name__ == "__main__":
    main()
