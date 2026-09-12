import importlib.util
import math
from pathlib import Path

import pytest
import torch


ROOT = Path(__file__).resolve().parent


def load(name):
    path = ROOT / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"token_tis_test_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_token_tis_is_detached_capped_and_not_self_normalized():
    maths = load("math_core")
    current = [[-0.5, -0.4], [-4.0]]
    native = [[-1.5, -0.4], [-3.0]]
    result = maths.token_tis(current, native, cap=2.0)

    expected = [2.0, 1.0, math.exp(-1.0)]
    assert result["weights"] == pytest.approx(expected)
    assert result["uncapped_weights"] == pytest.approx(
        [math.exp(1.0), 1.0, math.exp(-1.0)]
    )
    assert result["capped_tokens"] == 1
    assert result["tokens"] == 3
    assert result["capped_fraction"] == pytest.approx(1 / 3)
    assert result["weight_sum"] == pytest.approx(sum(expected))
    assert result["weight_mean"] != pytest.approx(1.0)
    assert result["self_normalized"] is False
    assert result["surrogate_unbiased"] is False


@pytest.mark.parametrize(
    "current,native",
    [([[float("nan")]], [[-1.0]]), ([[0.1]], [[-1.0]]), ([[-1.0]], [[float("inf")]])],
)
def test_token_tis_rejects_nonfinite_or_out_of_support_values(current, native):
    maths = load("math_core")
    with pytest.raises(ValueError, match="finite nonpositive"):
        maths.token_tis(current, native, cap=2.0)


def test_token_tis_streamed_objective_uses_sequence_sum_and_fixed_24_denominator():
    maths = load("math_core")
    values = [
        [torch.tensor([-1.0, -2.0], requires_grad=True), torch.tensor([-3.0], requires_grad=True)],
        [torch.tensor([-4.0], requires_grad=True)],
    ]
    weights = [[[2.0, 0.5], [1.0]], [[0.25]]]
    advantages = [0.5, -0.25]
    terms = list(maths.token_tis_terms(values, weights, advantages, denominator=24))
    loss = sum(terms)
    assert float(loss.detach()) == pytest.approx(
        -((0.5 * (2.0 * -1.0 + 0.5 * -2.0 + -3.0)) + (-0.25 * 0.25 * -4.0)) / 24
    )
    loss.backward()
    assert values[0][0].grad.tolist() == pytest.approx([-1.0 / 24, -0.25 / 24])
    assert values[1][0].grad.tolist() == pytest.approx([0.25 * 0.25 / 24])


def test_two_fresh_adam_branches_restore_identity_and_have_ten_x_dose():
    maths = load("math_core")
    model = torch.nn.Linear(2, 1, bias=False)
    model.weight.data.copy_(torch.tensor([[0.25, -0.5]]))
    snapshot = maths.snapshot_trainable(model)
    gradients = {"weight": torch.tensor([[0.75, -0.25]])}

    low = maths.apply_fresh_adam_branch(model, snapshot, gradients, learning_rate=1e-5)
    low_parameters = maths.snapshot_trainable(model)
    high = maths.apply_fresh_adam_branch(model, snapshot, gradients, learning_rate=1e-4)
    high_parameters = maths.snapshot_trainable(model)
    relation = maths.ten_x_dose_relation(snapshot, low_parameters, high_parameters)

    assert low["optimizer_state_empty_before_step"] is True
    assert high["optimizer_state_empty_before_step"] is True
    assert low["optimizer_state_steps"] == [1]
    assert high["optimizer_state_steps"] == [1]
    assert low["starting_identity_sha256"] == high["starting_identity_sha256"]
    assert relation["passed"] is True
    assert relation["delta_norm_ratio"] == pytest.approx(10.0, rel=5e-3)


def test_actual_frozen_input_inventory_and_source_pins_load():
    study = load("study")
    ready, data, episodes = study.load_sealed_inputs()

    assert ready["status"] == "CPU_READY_TOKEN_TIS_TWO_LR_V2"
    assert data["schema"] == "mrcr-short-shaped-root-hf-training-inputs-v1"
    assert len(episodes) == 24
    assert len({row["group_id"] for row in episodes}) == 6
    assert sum(len(row["root_turns"]) for row in episodes) == 74
    assert sum(
        len(turn["old_logprobs"]) for row in episodes for turn in row["root_turns"]
    ) == 15602
    assert sum(len(row.get("fixed_child_turns", [])) for row in episodes) == 0
    assert all(
        child["credited"] is False and child["loss_tokens"] == 0
        for row in episodes
        for child in row.get("fixed_child_turns", [])
    )


def test_owner_plan_is_fixed_two_independent_branches_without_generation():
    owner = load("owner")
    plan = owner.plan()
    assert plan["cap_seconds"] == 900
    assert plan["branches"] == ["lr1e-5", "lr1e-4"]
    assert plan["learning_rates"] == [1e-5, 1e-4]
    assert plan["optimizer_steps_per_branch"] == 1
    assert plan["new_generation_calls"] == 0
    assert plan["heldout_queries"] == 0
    assert plan["fixed_denominator"] == 24
    assert plan["token_tis_cap"] == 2.0
