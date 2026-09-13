"""Candidate-local and response-joint credit math for one fixed G4 batch."""


def _rloo(values):
    if len(values) != 4:
        raise ValueError("credit comparison requires G4")
    return [value - sum(values[j] for j in range(4) if j != i) / 3
            for i, value in enumerate(values)]


def advantages(correct, valid):
    if len(correct) != 4 or len(valid) != 4 or not correct:
        raise ValueError("credit comparison requires four samples")
    candidates = len(correct[0])
    if candidates <= 0 or any(len(row) != candidates for row in correct):
        raise ValueError("candidate inventories differ")
    if any(type(value) is not bool for value in valid):
        raise ValueError("sample validity must be boolean")
    rewards = [[int(value) for value in row] if keep else [0] * candidates
               for row, keep in zip(correct, valid, strict=True)]
    if any(value not in (0, 1) for row in rewards for value in row):
        raise ValueError("candidate correctness must be binary")
    local_columns = [_rloo([row[j] for row in rewards]) for j in range(candidates)]
    local = [[local_columns[j][i] for j in range(candidates)] for i in range(4)]
    response = [sum(row) / candidates for row in rewards]
    joint_values = _rloo(response)
    joint = [[joint_values[i]] * candidates for i in range(4)]
    return {"sample_valid": valid, "candidate_rewards": rewards, "response_rewards": response,
        "local": local, "joint": joint,
        "invalid_reward_policy": "all candidate rewards and response reward are zero",
        "invalid_samples_enter_peer_RLOO_baselines": True, "G": 4,
        "candidates": candidates}


def token_credit(spans, *, action_tokens, candidates, valid):
    if action_tokens <= 0 or candidates <= 0:
        raise ValueError("positive token and candidate inventories required")
    zero = [[0.0] * candidates for _ in range(action_tokens)]
    if not valid:
        return {"coefficients": zero, "invalid_vector_zero_mask": True,
            "boundary_overlap_token_indices": [], "cross_decision_token_indices": [],
            "selection_tokens": 0, "boundary_overlap_present": False,
            "whole_single_decision_token_weight": 1.0}
    if not spans.get("qualified"):
        raise ValueError("valid vector lacks qualified native boolean spans")
    offsets = spans["native_token_character_offsets"]
    decisions = spans["decisions"]
    if len(decisions) != candidates or len(offsets) > action_tokens:
        raise ValueError("native span inventory differs")
    touched = {}
    boundary = set()
    for decision in decisions:
        position = decision["position"]
        if type(position) is not int or not 0 <= position < candidates:
            raise ValueError("candidate position invalid")
        lo, hi = decision["character_span"]
        if not 0 <= lo < hi:
            raise ValueError("boolean character span invalid")
        for token in decision["token_indices"]:
            if not 0 <= token < len(offsets):
                raise ValueError("token span index invalid")
            start, end = offsets[token]
            overlap = max(0, min(end, hi) - max(start, lo))
            if overlap <= 0 or end <= start:
                raise ValueError("declared token does not overlap boolean")
            touched.setdefault(token, set()).add(position)
            if overlap < end - start: boundary.add(token)
    coefficients = [row[:] for row in zero]
    crossing = []
    for token, positions in touched.items():
        if len(positions) != 1:
            crossing.append(token)
            continue
        position = next(iter(positions)); coefficients[token][position] = 1.0
    return {"coefficients": coefficients, "invalid_vector_zero_mask": False,
        "boundary_overlap_token_indices": sorted(boundary),
        "cross_decision_token_indices": sorted(crossing),
        "selection_tokens": sum(any(value > 0 for value in row) for row in coefficients),
        "boundary_overlap_present": bool(boundary), "whole_single_decision_token_weight": 1.0,
        "rule": "whole native token intersecting exactly one boolean; cross-decision, standalone punctuation, and EOS get zero"}


def credit_loss(values, token_weights, advantages, coefficients, *, candidates, denominator):
    import torch
    if denominator != 64 or candidates <= 0:
        raise ValueError("fixed /64 denominator and positive candidate inventory required")
    if values.numel() != len(token_weights) or len(coefficients) != values.numel():
        raise ValueError("token inventories differ")
    if len(advantages) != candidates or any(len(row) != candidates for row in coefficients):
        raise ValueError("candidate inventories differ")
    multipliers = [sum(value * advantages[j] for j, value in enumerate(row)) / candidates
                   for row in coefficients]
    detached = torch.tensor([weight * multiplier for weight, multiplier in
        zip(token_weights, multipliers, strict=True)], dtype=values.dtype,
        device=values.device).detach()
    return -(detached * values).sum() / denominator
