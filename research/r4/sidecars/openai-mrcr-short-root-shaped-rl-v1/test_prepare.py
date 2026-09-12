import json


def test_saved_batch_maps_exact_complete_groups_and_shaped_reward():
    import build_inputs

    data = build_inputs.build()
    assert len(data["episodes"]) == 24
    assert len({row["group_id"] for row in data["episodes"]}) == 6
    assert len(data["excluded_groups"]) == 2
    assert sum(len(row["root_turns"]) for row in data["episodes"]) == 74
    assert sum(
        len(turn["action_ids"]) for row in data["episodes"] for turn in row["root_turns"]
    ) == 15602
    assert all(not row["fixed_child_turns"] for row in data["episodes"])
    groups = {}
    for row in data["episodes"]:
        groups.setdefault(row["group_id"], []).append(row)
        expected = 0.5 * (row["raw_official_similarity"] >= 0.90) + 0.5 * row["raw_exact"]
        assert row["reward"] == expected
    assert sum(len({row["reward"] for row in group}) > 1 for group in groups.values()) == 2
    assert all(len(group) == 4 for group in groups.values())


def test_thin_trainer_uses_fixed24_denominator_and_validates_real_inputs(tmp_path):
    import build_inputs
    import trainer

    data = build_inputs.build()
    module = trainer.module()
    episodes = module.validate_inputs(data)
    assert len(episodes) == 24
    text = trainer.source_text()
    assert " / 24" in text
    assert "all24_passed" in text
    assert '"episodes": 24' in text and '"groups": 6' in text


def test_reward_keeps_wrong_turn_overlap_at_zero():
    import build_inputs

    assert build_inputs.shaped_reward(0.3865546218487395, False) == 0.0
    assert build_inputs.shaped_reward(0.9876772843524761, False) == 0.5
    assert build_inputs.shaped_reward(1.0, True) == 1.0


def test_streamed_gradient_equals_fixed24_sequence_sum_objective():
    import torch

    import math_core
    import trainer

    advantages = torch.tensor(([0.5, -1 / 6, -1 / 6, -1 / 6] * 6), dtype=torch.float64)
    ratios = torch.linspace(0.8, 1.2, 24, dtype=torch.float64)
    left = torch.tensor(0.3, dtype=torch.float64, requires_grad=True)
    left_turns = [[left * (index + 1), left * torch.tensor([0.5, 1.5])] for index in range(24)]
    expected = math_core.trajectory_loss(left_turns, advantages, ratios)
    expected.backward()
    expected_gradient = left.grad.detach().clone()

    right = torch.tensor(0.3, dtype=torch.float64, requires_grad=True)
    right_turns = [
        [right * (index + 1), right * torch.tensor([0.5, 1.5])] for index in range(24)
    ]
    actual = trainer.streamed_objective(right_turns, advantages, ratios)
    actual.backward()
    assert torch.allclose(actual, expected, atol=1e-12, rtol=0)
    assert torch.allclose(right.grad, expected_gradient, atol=1e-12, rtol=0)
