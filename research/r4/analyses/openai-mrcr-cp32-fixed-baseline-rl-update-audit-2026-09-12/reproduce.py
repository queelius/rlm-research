"""Read-only audit of the fixed-baseline cp32 final-action RL update."""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
import math
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parents[1] / "sidecars/openai-mrcr-cp32-fixed-baseline-final-rl-v1"
OUT = SIDE / "outputs/attempt-001"
CP = OUT / "checkpoint-0001"
PARENT = (
    ROOT.parents[1]
    / "sidecars/openai-mrcr-procedural-sft-continue32-v1/outputs/attempt-001/checkpoint-0032"
)


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path: Path):
    return json.loads(path.read_text())


def tensor_norm(values) -> float:
    return math.sqrt(math.fsum(float(value.double().square().sum()) for value in values))


def build():
    import torch
    from safetensors.torch import load_file

    result = read(OUT / "RESULT.json")
    state = read(CP / "state.json")
    commit = read(CP / "STEP_COMMIT.json")
    initial = read(OUT / "INITIAL.json")
    prequal = read(OUT / "PRESTEP_QUALIFICATION.json")
    inputs = read(SIDE / "TRAIN_INPUTS.json")
    replay = read(OUT / "gradient/REPLAY.json")
    pre = read(OUT / "PRESTEP_LOGPS.json")["episodes"]
    post = read(OUT / "POSTSTEP_LOGPS.json")["episodes"]

    assert result["status"] == state["status"] == "UPDATED"
    assert result["optimizer_steps"] == state["optimizer_steps"] == commit["step"] == 1
    assert sha(CP / "state.json") == result["state_sha256"]
    assert sha(CP / "STEP_COMMIT.json") == result["step_commit_sha256"]
    for raw, expected in commit["files_sha256"].items():
        assert sha(Path(raw)) == expected
    assert sha(OUT / "PRESTEP_QUALIFICATION.json") == state["prestep_qualification_sha256"]
    assert sha(OUT / "PRESTEP_LOGPS.json") == state["prestep_logps_sha256"]
    assert sha(OUT / "POSTSTEP_LOGPS.json") == state["poststep_logps_sha256"]
    assert sha(OUT / "gradient/REPLAY.json") == state["gradient_receipt_sha256"]
    assert sha(OUT / "gradient/gradients.pt") == state["gradient_sha256"]
    assert sha(PARENT / "adapter_model.safetensors") == state["parent_adapter_sha256"]
    assert sha(CP / "adapter_model.safetensors") == state["adapter_sha256"]
    assert sha(OUT / "initial-trainable.pt") == initial["initial_tensor_file_sha256"]
    assert sha(OUT / "initial-rng.pt") == initial["initial_rng_sha256"]

    before = load_file(str(PARENT / "adapter_model.safetensors"))
    after = load_file(str(CP / "adapter_model.safetensors"))
    assert before.keys() == after.keys()
    actual_adapter_delta = tensor_norm(after[key] - before[key] for key in before)
    assert math.isclose(actual_adapter_delta, state["adapter_delta_l2"], rel_tol=2e-6)

    gradients = torch.load(OUT / "gradient/gradients.pt", map_location="cpu", weights_only=True)
    components = torch.load(
        OUT / "gradient/negative-component-gradients.pt", map_location="cpu", weights_only=True
    )
    actual_gradient_norm = tensor_norm(gradients.values())
    component_norms = {key: tensor_norm(value.values()) for key, value in components.items()}
    for key, value in component_norms.items():
        assert math.isclose(value, replay["negative_component_gradient_l2"][key], rel_tol=1e-9)
    # clip_grad_norm_ reports through a float32 reduction; the saved tensors are summed in float64.
    assert math.isclose(actual_gradient_norm, replay["gradient_norm_before_clip"], rel_tol=1e-7)

    rows = inputs["episodes"]
    assert len(rows) == len(pre) == len(post) == len(replay["episodes"]) == 32
    movement_by_reward = defaultdict(list)
    movement_by_reward_part = defaultdict(lambda: defaultdict(list))
    episode_rows = []
    for row, pre_turns, post_turns, replay_row in zip(rows, pre, post, replay["episodes"], strict=True):
        assert row["episode_id"] == replay_row["episode_id"]
        assert len(pre_turns) == len(post_turns) == 1
        before_values, after_values = pre_turns[0], post_turns[0]
        assert len(before_values) == len(after_values) == len(row["root_turns"][0]["action_ids"])
        parts = row["root_turns"][0]["diagnostic_token_parts"]
        deltas = [new - old for old, new in zip(before_values, after_values, strict=True)]
        total = math.fsum(deltas)
        movement_by_reward[row["reward"]].append(total)
        part_sums = {}
        for part in ("body", "whitespace", "eos"):
            part_sums[part] = math.fsum(delta for delta, label in zip(deltas, parts, strict=True) if label == part)
            movement_by_reward_part[row["reward"]][part].append(part_sums[part])
        episode_rows.append(
            {
                "episode_id": row["episode_id"],
                "group_id": row["group_id"],
                "reward": row["reward"],
                "tokens": len(deltas),
                "post_minus_pre_logprob_sum": total,
                "post_minus_pre_by_part": part_sums,
            }
        )

    rewards = Counter(row["reward"] for row in rows)
    negative_vectors_identical = len({
        tuple(round(value, 10) for value in vector[0])
        for vector, row in zip(pre, rows, strict=True)
        if row["reward"] == 0
    }) == 1
    group_rewards = defaultdict(list)
    for row in rows:
        group_rewards[row["group_id"]].append(row["reward"])

    return {
        "schema": "openai-mrcr-cp32-fixed-baseline-rl-update-audit-v1",
        "status": "complete_read_only",
        "source": {
            "ready_sha256": sha(SIDE / "READY.json"),
            "train_inputs_sha256": sha(SIDE / "TRAIN_INPUTS.json"),
            "result_sha256": sha(OUT / "RESULT.json"),
            "state_sha256": sha(CP / "state.json"),
            "step_commit_sha256": sha(CP / "STEP_COMMIT.json"),
            "replay_sha256": sha(OUT / "gradient/REPLAY.json"),
            "prestep_logps_sha256": sha(OUT / "PRESTEP_LOGPS.json"),
            "poststep_logps_sha256": sha(OUT / "POSTSTEP_LOGPS.json"),
        },
        "integrity": {
            "step_commit_all_files_match": True,
            "parent_and_updated_adapter_tensors_loaded": len(before),
            "adapter_delta_l2_recomputed": actual_adapter_delta,
            "gradient_norm_l2_recomputed": actual_gradient_norm,
            "optimizer_steps": 1,
            "fresh_adam": state["fresh_AdamW"],
            "optimizer_state_steps": state["optimizer_state_steps"],
        },
        "training": {
            "episodes": len(rows),
            "groups": len(group_rewards),
            "reward_counts": {str(key): value for key, value in sorted(rewards.items())},
            "group_reward_vectors": [group_rewards[key] for key in sorted(group_rewards)],
            "conditional_final_tokens": state["actual_final_tokens"],
            "zero_loss_other_root_tokens": state["zero_loss_other_root_tokens"],
            "child_loss_tokens": state["child_loss_tokens"],
            "denominator": state["denominator"],
            "gradient_component_l2_negative_only": component_norms,
            "token_TIS": {
                "cap": prequal["cap"],
                "capped_tokens": prequal["capped_tokens"],
                "weight_min": prequal["capped_min"],
                "weight_max": prequal["capped_max"],
                "weight_mean": prequal["capped_weight_mean"],
            },
        },
        "poststep_on_saved_actions": {
            "diagnostic_only": True,
            "not_new_generation_or_accuracy": True,
            "negative_pre_vectors_identical": negative_vectors_identical,
            "mean_sequence_logprob_delta_by_reward": {
                str(key): math.fsum(values) / len(values) for key, values in movement_by_reward.items()
            },
            "sum_sequence_logprob_delta_by_reward": {
                str(key): math.fsum(values) for key, values in movement_by_reward.items()
            },
            "mean_part_logprob_delta_by_reward": {
                str(reward): {
                    part: math.fsum(values) / len(values) for part, values in parts.items()
                }
                for reward, parts in movement_by_reward_part.items()
            },
        },
        "episodes": episode_rows,
        "limitations": [
            "The update conditions on the same 32 saved native final actions; it is not an accuracy evaluation.",
            "All four negative examples are repetitions of one group and one final-token sequence.",
            "Negative component norms isolate token subsets but do not decompose the total positive-plus-negative gradient.",
            "Shared parameters mean a change in whitespace likelihood can also change semantic behavior elsewhere.",
        ],
    }


def write_x(path: Path, value) -> None:
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


if __name__ == "__main__":
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise RuntimeError("CPU-only audit requires CUDA_VISIBLE_DEVICES empty")
    value = build()
    target = ROOT / "RESULTS.json"
    if target.exists():
        assert read(target) == value
    else:
        write_x(target, value)
    print(json.dumps({"status": value["status"], **value["poststep_on_saved_actions"]}, sort_keys=True))
