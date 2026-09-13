import torch

import credit


def test_local_and_joint_rloo_differ_but_keep_equal_fixed_scale():
    correct = [[1, 0], [1, 1], [0, 1], [0, 0]]
    result = credit.advantages(correct, [True] * 4)
    assert result["candidate_rewards"] == correct
    assert result["response_rewards"] == [0.5, 1.0, 0.5, 0.0]
    assert torch.allclose(torch.tensor(result["local"]), torch.tensor(
        [[2/3, -2/3], [2/3, 2/3], [-2/3, 2/3], [-2/3, -2/3]]))
    assert torch.allclose(torch.tensor(result["joint"]), torch.tensor(
        [[0.0, 0.0], [2/3, 2/3], [0.0, 0.0], [-2/3, -2/3]]))
    assert all(abs(sum(row[i] for row in result["local"])) < 1e-12 for i in range(2))
    assert all(abs(sum(row[i] for row in result["joint"])) < 1e-12 for i in range(2))


def test_invalid_vector_is_zero_reward_zero_mask_and_retained_in_rloo():
    correct = [[1, 1], [1, 0], [0, 1], [1, 1]]
    result = credit.advantages(correct, [True, True, True, False])
    assert result["candidate_rewards"][3] == [0, 0]
    assert result["response_rewards"][3] == 0.0
    assert result["invalid_reward_policy"] == "all candidate rewards and response reward are zero"
    assert result["invalid_samples_enter_peer_RLOO_baselines"]
    assert not result["sample_valid"][3]


def test_whole_single_decision_tokens_and_cross_decision_tokens_are_explicit():
    spans = {"qualified": True, "native_token_character_offsets": [[0, 5], [5, 9], [9, 15], [15, 16]],
        "decisions": [
            {"position": 0, "character_span": [1, 5], "token_indices": [0]},
            {"position": 1, "character_span": [5, 10], "token_indices": [1, 2]},
        ]}
    result = credit.token_credit(spans, action_tokens=5, candidates=2, valid=True)
    assert result["coefficients"] == [[1.0, 0.0], [0.0, 1.0], [0.0, 1.0], [0.0, 0.0], [0.0, 0.0]]
    assert result["boundary_overlap_token_indices"] == [0, 2]
    assert result["whole_single_decision_token_weight"] == 1.0
    assert not result["cross_decision_token_indices"]
    invalid = credit.token_credit(spans, action_tokens=5, candidates=2, valid=False)
    assert invalid["coefficients"] == [[0.0, 0.0]] * 5
    assert invalid["invalid_vector_zero_mask"] and invalid["boundary_overlap_token_indices"] == []
    crossing = {**spans, "decisions": [
        {"position": 0, "character_span": [1, 6], "token_indices": [0, 1]},
        {"position": 1, "character_span": [5, 10], "token_indices": [1, 2]}]}
    crossed = credit.token_credit(crossing, action_tokens=5, candidates=2, valid=True)
    assert crossed["coefficients"][1] == [0.0, 0.0]
    assert crossed["cross_decision_token_indices"] == [1]


def test_credit_loss_uses_candidate_average_and_fixed_64_denominator():
    values = torch.tensor([-2.0, -3.0, -4.0], requires_grad=True)
    tis = [1.0, 0.5, 2.0]
    coefficients = [[1.0, 0.0], [0.0, 0.5], [0.0, 0.0]]
    loss = credit.credit_loss(values, tis, [1.0, -1.0], coefficients,
                              candidates=2, denominator=64)
    loss.backward()
    assert torch.equal(values.grad, torch.tensor([-1/128, 1/512, 0.0]))
