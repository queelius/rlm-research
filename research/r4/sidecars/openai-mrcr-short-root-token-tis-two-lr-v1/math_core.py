"""Pure math and deterministic branch-state helpers for the token-TIS dose probe."""

from __future__ import annotations

import hashlib
import math
from collections.abc import Iterable, Sequence

import torch


def _flatten(rows: Sequence[Sequence[float]]) -> list[float]:
    return [float(value) for row in rows for value in row]


def token_tis(
    current_turns: Sequence[Sequence[float]],
    native_turns: Sequence[Sequence[float]],
    *,
    cap: float,
) -> dict:
    """Compute unnormalized capped token-level IS weights.

    This is deliberately a biased surrogate: clipping occurs independently at each token,
    and the result is neither sequence-correct nor self-normalized.
    """
    if cap <= 0 or len(current_turns) != len(native_turns) or not current_turns:
        raise ValueError("token inventories or cap differ")
    current = _flatten(current_turns)
    native = _flatten(native_turns)
    if not current or len(current) != len(native):
        raise ValueError("token inventories differ")
    if any(not math.isfinite(value) or value > 0 for value in current + native):
        raise ValueError("token log probabilities must be finite nonpositive")
    uncapped = [math.exp(now - old) for now, old in zip(current, native, strict=True)]
    if any(not math.isfinite(value) or value <= 0 for value in uncapped):
        raise ValueError("token importance weights must be finite positive")
    weights = [min(value, cap) for value in uncapped]
    total = math.fsum(weights)
    squares = math.fsum(value * value for value in weights)
    capped = sum(value > cap for value in uncapped)
    return {
        "tokens": len(weights),
        "log_ratios": [now - old for now, old in zip(current, native, strict=True)],
        "uncapped_weights": uncapped,
        "weights": weights,
        "cap": cap,
        "capped_tokens": capped,
        "capped_fraction": capped / len(weights),
        "weight_sum": total,
        "weight_mean": total / len(weights),
        "token_ess": total * total / squares,
        "token_ess_fraction": total * total / squares / len(weights),
        "self_normalized": False,
        "surrogate_unbiased": False,
    }


def token_tis_terms(
    root_turn_logprobs: Sequence[Sequence[torch.Tensor]],
    token_weights: Sequence[Sequence[Sequence[float]]],
    advantages: Sequence[float],
    *,
    denominator: int,
) -> Iterable[torch.Tensor]:
    """Yield streamed token-TIS sequence-SUM terms divided by a fixed denominator."""
    if denominator <= 0 or not root_turn_logprobs:
        raise ValueError("positive fixed denominator and episodes required")
    if not (
        len(root_turn_logprobs) == len(token_weights) == len(advantages)
    ):
        raise ValueError("episode inventories differ")
    for turns, weights, advantage in zip(
        root_turn_logprobs, token_weights, advantages, strict=True
    ):
        if not turns or len(turns) != len(weights):
            raise ValueError("turn inventories differ")
        for values, turn_weights in zip(turns, weights, strict=True):
            if values.numel() != len(turn_weights) or values.numel() == 0:
                raise ValueError("token weight inventory differs")
            detached = torch.tensor(
                turn_weights, dtype=values.dtype, device=values.device
            ).detach()
            yield -(float(advantage) * (detached * values).sum()) / denominator


def snapshot_trainable(model) -> dict[str, torch.Tensor]:
    snapshot = {
        name: parameter.detach().cpu().clone()
        for name, parameter in model.named_parameters()
        if parameter.requires_grad
    }
    if not snapshot:
        raise ValueError("no trainable parameters")
    return snapshot


def snapshot_digest(snapshot: dict[str, torch.Tensor]) -> str:
    digest = hashlib.sha256()
    for name in sorted(snapshot):
        value = snapshot[name].detach().cpu().contiguous()
        digest.update(name.encode())
        digest.update(str(value.dtype).encode())
        digest.update(str(tuple(value.shape)).encode())
        digest.update(value.numpy().tobytes(order="C"))
    return digest.hexdigest()


def restore_snapshot(model, snapshot: dict[str, torch.Tensor]) -> str:
    current = {
        name: parameter for name, parameter in model.named_parameters() if parameter.requires_grad
    }
    if set(current) != set(snapshot):
        raise ValueError("trainable parameter inventory changed")
    model.zero_grad(set_to_none=True)
    with torch.no_grad():
        for name, parameter in current.items():
            parameter.copy_(snapshot[name].to(device=parameter.device, dtype=parameter.dtype))
    actual = snapshot_trainable(model)
    if any(not torch.equal(actual[name], snapshot[name]) for name in snapshot):
        raise ValueError("trainable snapshot restoration was not exact")
    return snapshot_digest(actual)


def apply_fresh_adam_branch(
    model,
    snapshot: dict[str, torch.Tensor],
    gradients: dict[str, torch.Tensor],
    *,
    learning_rate: float,
) -> dict:
    """Restore one initial state and apply exactly one fresh-AdamW step."""
    initial_identity = restore_snapshot(model, snapshot)
    parameters = {
        name: parameter for name, parameter in model.named_parameters() if parameter.requires_grad
    }
    if set(parameters) != set(gradients):
        raise ValueError("gradient inventory differs")
    optimizer = torch.optim.AdamW(
        list(parameters.values()), lr=learning_rate, weight_decay=0.0
    )
    was_empty = not optimizer.state
    if not was_empty:
        raise ValueError("fresh branch optimizer has state")
    for name, parameter in parameters.items():
        gradient = gradients[name]
        if not torch.isfinite(gradient).all():
            raise ValueError("nonfinite saved gradient")
        parameter.grad = gradient.to(device=parameter.device, dtype=parameter.dtype).clone()
    optimizer.step()
    states = optimizer.state_dict()
    steps = sorted({int(value["step"]) for value in states["state"].values()})
    if steps != [1]:
        raise ValueError("branch Adam state is not exactly step1")
    return {
        "optimizer": optimizer,
        "optimizer_state_empty_before_step": was_empty,
        "optimizer_state_steps": steps,
        "starting_identity_sha256": initial_identity,
        "learning_rate": learning_rate,
        "weight_decay": 0.0,
    }


def _delta_vector(initial, updated):
    if set(initial) != set(updated):
        raise ValueError("branch parameter inventories differ")
    return torch.cat(
        [(updated[name].double() - initial[name].double()).reshape(-1) for name in sorted(initial)]
    )


def ten_x_dose_relation(initial, low, high) -> dict:
    low_delta = _delta_vector(initial, low)
    high_delta = _delta_vector(initial, high)
    low_norm = float(torch.linalg.vector_norm(low_delta))
    high_norm = float(torch.linalg.vector_norm(high_delta))
    if not math.isfinite(low_norm + high_norm) or low_norm <= 0:
        raise ValueError("branch deltas are nonfinite or zero")
    ratio = high_norm / low_norm
    residual = float(torch.linalg.vector_norm(high_delta - 10.0 * low_delta))
    cosine = float(torch.nn.functional.cosine_similarity(low_delta, high_delta, dim=0))
    passed = math.isclose(ratio, 10.0, rel_tol=5e-3) and cosine >= 0.99999
    return {
        "expected_ratio": 10.0,
        "delta_norm_ratio": ratio,
        "low_delta_l2": low_norm,
        "high_delta_l2": high_norm,
        "ten_x_residual_l2": residual,
        "delta_cosine": cosine,
        "relative_tolerance": 0.005,
        "passed": passed,
    }
