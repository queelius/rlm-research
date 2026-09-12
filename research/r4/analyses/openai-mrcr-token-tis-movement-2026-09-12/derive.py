"""Call-free likelihood movement on the fixed training trajectories, not new answers."""

import hashlib
import json
import math
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = HERE.parents[1] / "sidecars/openai-mrcr-short-root-token-tis-two-lr-v1/outputs/attempt-001"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def inventory(condition, expected):
    path = RUN / "likelihood" / condition / "INVENTORY.json"
    assert sha(path) == expected, condition
    items = {}
    for entry in read(path)["files"]:
        episode = Path(entry["path"])
        assert sha(episode) == entry["sha256"], episode
        value = read(episode)
        assert value["episode_id"] not in items
        items[value["episode_id"]] = value
    assert len(items) == 24
    return items


def execute():
    result = read(RUN / "RESULT.json")
    assert result["status"] == "UPDATED_TWO_INDEPENDENT_BRANCHES"
    baseline = inventory("baseline", result["baseline_likelihood_inventory_sha256"])
    branches = {}
    for name, branch in result["branches"].items():
        after = inventory(name, branch["postupdate_likelihood_inventory_sha256"])
        assert set(after) == set(baseline)
        rows = []
        for episode_id, before in baseline.items():
            post = after[episode_id]
            for key in ("group_id", "reward", "advantage", "root_action_tokens"):
                assert before[key] == post[key]
            assert len(before["root_turns"]) == len(post["root_turns"])
            turns = []
            for left, right in zip(before["root_turns"], post["root_turns"], strict=True):
                for key in ("turn_index", "input_ids_sha256", "action_ids_sha256", "action_tokens"):
                    assert left[key] == right[key]
                assert len(left["logprobs"]) == len(right["logprobs"]) == left["action_tokens"]
                deltas = [b - a for a, b in zip(left["logprobs"], right["logprobs"], strict=True)]
                assert all(math.isfinite(x) for x in deltas)
                turns.append({"turn_index": left["turn_index"], "tokens": len(deltas),
                              "sequence_delta": sum(deltas), "per_token_delta": statistics.mean(deltas)})
            delta = sum(turn["sequence_delta"] for turn in turns)
            rows.append({"episode_id": episode_id, "group_id": before["group_id"],
                         "reward": before["reward"], "advantage": before["advantage"],
                         "tokens": before["root_action_tokens"], "sequence_delta": delta,
                         "per_token_delta": delta / before["root_action_tokens"], "turns": turns})
        by_advantage = {}
        for label, predicate in (("positive", lambda x: x > 0), ("negative", lambda x: x < 0),
                                 ("zero", lambda x: x == 0)):
            selected = [row for row in rows if predicate(row["advantage"])]
            by_advantage[label] = {
                "episodes": len(selected),
                "sequence_increased": sum(row["sequence_delta"] > 0 for row in selected),
                "mean_sequence_delta": statistics.mean(row["sequence_delta"] for row in selected),
                "mean_episode_per_token_delta": statistics.mean(row["per_token_delta"] for row in selected),
                "first_turn_mean_per_token_delta": statistics.mean(row["turns"][0]["per_token_delta"] for row in selected),
                "last_turn_mean_per_token_delta": statistics.mean(row["turns"][-1]["per_token_delta"] for row in selected),
            }
        branches[name] = {
            "adapter_delta_l2": branch["adapter_delta_l2"], "by_advantage": by_advantage,
            "advantage_weighted_sequence_delta_over24": sum(row["advantage"] * row["sequence_delta"] for row in rows) / 24,
            "rows": rows,
        }
    relation = RUN / "BRANCH_RELATION.json"
    assert sha(relation) == result["branch_relation_sha256"]
    return {
        "schema": "mrcr-token-tis-fixed-trajectory-movement-v1",
        "source_result_sha256": sha(RUN / "RESULT.json"), "derivation_sha256": sha(Path(__file__)),
        "training_only": True, "new_model_calls": 0, "branch_relation": read(relation),
        "branches": branches,
        "limitations": [
            "Likelihoods are recomputed by the training backend on already sampled trajectories.",
            "Increased likelihood is not increased accuracy or a newly generated answer.",
            "Only two groups have nonzero advantages; positive trajectories used broad context dumps.",
            "First and last root turns are positional diagnostics, not verified semantic action classes.",
            "Token-TIS is an explicitly biased surrogate; parameter movement does not establish estimator validity.",
        ],
    }


if __name__ == "__main__":
    value = execute()
    with (HERE / "FINDINGS.json").open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({name: {key: val for key, val in branch.items() if key != "rows"}
                      for name, branch in value["branches"].items()}, indent=2))
