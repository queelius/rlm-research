"""Exercise the actual branch initializer with a real optimizer update and all RNG domains."""

import importlib.util
import random
from pathlib import Path

import numpy as np
import torch


def test_branch_start_restores_rng_and_model_after_real_adam_step(tmp_path):
    path = Path(__file__).with_name("repair.py")
    assert path.exists(), "additive branch repair absent"
    spec = importlib.util.spec_from_file_location("paired_repair_fixture", path)
    repair = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(repair)
    implementation = repair.implementation()
    assert implementation.restore_rng is implementation.save_rng.__globals__["restore_rng"]
    fixture = repair.load("paired_v1_fixture_reuse", repair.V1 / "test_pair.py")
    model = fixture.tiny_model()
    initial = repair.maths.snapshot_trainable(model)
    generator = torch.Generator().manual_seed(17)
    rng = tmp_path / "shared_rng.pt"
    implementation.save_rng(rng, generator)
    first, receipt = repair.initialize_branch(implementation, model, initial, rng, generator)
    assert receipt["rng_identical"] and receipt["optimizer_state_empty"]
    random_values = (
        random.random(),
        float(np.random.rand()),
        torch.rand(3),
        torch.rand(3, generator=generator),
    )
    inputs = torch.tensor([[4, 5, 6]] * 4)
    before = model(input_ids=inputs, use_cache=False).logits.detach().clone()
    model(input_ids=inputs, use_cache=False).logits.square().mean().backward()
    first.step()
    assert first.state and implementation.adapter_delta(model, initial) > 0
    second, second_receipt = repair.initialize_branch(
        implementation, model, initial, rng, generator
    )
    assert not second.state and second is not first and second_receipt == receipt
    repeated = (
        random.random(),
        float(np.random.rand()),
        torch.rand(3),
        torch.rand(3, generator=generator),
    )
    assert random_values[:2] == repeated[:2]
    assert all(torch.equal(a, b) for a, b in zip(random_values[2:], repeated[2:], strict=True))
    assert torch.equal(model(input_ids=inputs, use_cache=False).logits, before)
    model(input_ids=inputs, use_cache=False).logits.square().mean().backward()
    second.step()
    assert sorted({int(value["step"]) for value in second.state.values()}) == [1]
    assert repair.build()._branch.__globals__["initialize_branch"] is repair.initialize_branch
