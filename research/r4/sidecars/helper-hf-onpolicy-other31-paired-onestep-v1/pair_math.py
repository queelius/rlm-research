"""Exact paired baselines and bit-identical trainable-state restoration."""

import math
import hashlib

import torch


def paired_advantages(reward_groups):
    if len(reward_groups) != 32 or any(len(row) != 4 for row in reward_groups):
        raise ValueError("exact 32x4 reward inventory required")
    if any(value not in (0.0, 1.0) for row in reward_groups for value in row):
        raise ValueError("binary verifier rewards required")
    total = math.fsum(value for row in reward_groups for value in row)
    result = []
    for index, rewards in enumerate(reward_groups):
        own = math.fsum(rewards)
        baseline = (total - own) / 124
        rloo = [reward - (own - reward) / 3 for reward in rewards]
        other31 = [reward - baseline for reward in rewards]
        if not all(math.isfinite(value) for value in rloo + other31):
            raise ValueError("nonfinite advantage")
        result.append(
            {
                "group_index": index,
                "rewards": list(rewards),
                "rloo": rloo,
                "other31": other31,
                "other31_baseline": baseline,
                "other31_reward_sum": total - own,
                "other31_action_count": 124,
                "current_question_actions_excluded": 4,
                "baseline_detached": True,
                "all_failure": rewards == [0.0] * 4,
                "all_success": rewards == [1.0] * 4,
            }
        )
    return result


def snapshot_trainable(model):
    snapshot = {
        name: parameter.detach().cpu().clone()
        for name, parameter in model.named_parameters()
        if parameter.requires_grad
    }
    if not snapshot:
        raise ValueError("no trainable parameters")
    return snapshot


def assert_snapshot(model, snapshot):
    current = {
        name: parameter.detach().cpu()
        for name, parameter in model.named_parameters()
        if parameter.requires_grad
    }
    if set(current) != set(snapshot):
        raise ValueError("trainable parameter inventory changed")
    changed = [name for name in snapshot if not torch.equal(current[name], snapshot[name])]
    if changed:
        raise ValueError("trainable snapshot differs: " + changed[0])
    return True


def restore_snapshot(model, snapshot):
    current = {
        name: parameter for name, parameter in model.named_parameters() if parameter.requires_grad
    }
    if set(current) != set(snapshot):
        raise ValueError("trainable parameter inventory changed before restore")
    model.zero_grad(set_to_none=True)
    with torch.no_grad():
        for name, parameter in current.items():
            parameter.copy_(snapshot[name].to(device=parameter.device, dtype=parameter.dtype))
    return assert_snapshot(model, snapshot)


def snapshot_digest(snapshot):
    digest = hashlib.sha256()
    for name in sorted(snapshot):
        value = snapshot[name].detach().cpu().contiguous()
        digest.update(name.encode())
        digest.update(str(value.dtype).encode())
        digest.update(str(tuple(value.shape)).encode())
        digest.update(value.numpy().tobytes(order="C"))
    return digest.hexdigest()
