import json
from pathlib import Path

import pytest

import checkpoint
import collect
import study


def test_frozen_schedules_hold_heldout_across_base_and_checkpoint():
    train = study.schedule("train")
    held = study.schedule("held")
    assert len(train) == 32 and len(held) == 32
    assert len({row["record_id"] for row in train}) == 32
    assert len({row["record_id"] for row in held}) == 16
    assert {row["repeat"] for row in train} == {0}
    assert {row["repeat"] for row in held} == {0, 1}
    assert all(row["temperature"] == 0.5 for row in train + held)
    assert not ({row["record_id"] for row in train} & {row["record_id"] for row in held})
    # Arm is deliberately absent: both held policies consume these exact coordinates/seeds.
    assert all("arm" not in row for row in held)
    prepared = study.prepare_inputs()
    assert prepared["train"]["prefixes"] == prepared["held"]["prefixes"] == 32
    prefixes = study.read(study.input_dir("train") / "PREFIXES.json")
    corpus = study.read(study.TRAINING / "TEACHER_CORPUS_V2.json")
    first = corpus["episodes"][0]
    coordinate = next(row for row in train if row["record_id"] == first["episode_id"])
    turn = first["turns"][0]
    assert prefixes[coordinate["id"]]["token_ids"] == turn["input_ids"][: turn["prompt_length"]]


def test_train_gate_uses_raw_exact_and_distinct_contexts():
    rows = []
    for index in range(32):
        answer = f"gold-{index}"
        reply = answer if index < 8 else "wrong"
        rows.append(
            {
                "coordinate": {"record_id": f"r{index}", "context_sha256": f"c{index}"},
                "derived": {
                    "scientifically_available": True,
                    "root_reply": reply,
                    "answer": answer,
                    "raw_exact": reply == answer,
                    "normalized_exact": reply.strip() == answer.strip(),
                    "reward": float(reply == answer),
                    "root_actions_returned": 1,
                    "child_actions_returned": 0,
                    "prompt_tokens": 10,
                    "completion_tokens": 2,
                    "usage_unknown_calls": 0,
                    "native_mapping_complete": True,
                    "initial_root_prefix_verified": True,
                    "six_total_root_child_cap_respected": True,
                },
            }
        )
    gate = collect.manipulation_gate(rows)
    assert gate["eligible"] and gate["raw_exact"] == 8
    rows[0]["derived"]["root_reply"] = " " + rows[0]["derived"]["answer"]
    rows[0]["derived"]["raw_exact"] = False
    rows[0]["derived"]["normalized_exact"] = True
    rows[0]["derived"]["reward"] = 0.0
    gate = collect.manipulation_gate(rows)
    assert not gate["eligible"] and gate["raw_exact"] == 7
    assert gate["normalized_exact"] == 8
    result = collect.summarize(rows, "train", "checkpoint4")
    assert result["manipulation_gate"] == gate
    assert result["raw_exact"] == 7 and result["normalized_exact"] == 8


def test_checkpoint_header_and_step_chain_reject_intermediate_or_missing_parent(tmp_path):
    output = tmp_path / "attempt"
    output.mkdir()
    result = {
        "status": "COMPLETED_FOUR_UPDATES",
        "optimizer_steps": 4,
        "primary_checkpoint": str(output / "checkpoint-0003"),
        "evaluation_binding": str(output / "checkpoint-0003/EVAL_BINDING.json"),
        "step_commits": [],
    }
    with pytest.raises(ValueError, match="checkpoint-0004"):
        checkpoint.validate_result_header(result, output)
    state = {"step": 2, "optimizer_steps": 2, "previous_step_commit_sha256": None}
    with pytest.raises(ValueError, match="previous"):
        checkpoint.validate_state_link(state, 2, "abc")


def test_zero_adapter_requires_only_lora_tensors_and_exact_zeros(tmp_path):
    import torch
    from safetensors.torch import save_file

    source = tmp_path / "source"
    zero = tmp_path / "zero"
    source.mkdir()
    (source / "adapter_config.json").write_text(
        json.dumps({"bias": "none", "lora_dropout": 0.0, "r": 8, "lora_alpha": 16})
    )
    save_file(
        {
            "base_model.a.lora_A.weight": torch.ones(2, 3),
            "base_model.a.lora_B.weight": torch.ones(4, 2),
        },
        source / "adapter_model.safetensors",
    )
    receipt = checkpoint.materialize_zero_adapter(source, zero)
    assert receipt["all_tensors_zero"] and receipt["tensors"] == 2
    checkpoint.validate_zero_adapter(zero, receipt)


def test_actual_role_router_changes_only_model_for_depth():
    role = collect.role_hooks()
    role_map = {"root": study.ADAPTED_ALIAS, "children": [study.BASE_ALIAS]}
    headers = {
        "x-rlm-role-depth": "1",
        "x-rlm-role-invocation": "invocation-1",
        "x-rlm-role-request-id": "a" * 32,
        "x-rlm-role-kind": "ordinary",
    }
    body = {"model": study.ADAPTED_ALIAS, "token_ids": [1, 2], "sampling_params": {"seed": 3}}
    before = {key: value for key, value in body.items() if key != "model"}
    evidence = role.route_native(body, headers, role_map, study.BASE_ALIAS)
    assert body["model"] == study.BASE_ALIAS and evidence["depth"] == 1
    assert {key: value for key, value in body.items() if key != "model"} == before
