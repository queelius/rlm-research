"""Focused response-joint input, gradient, owner, and checkpoint-interface tests."""

from pathlib import Path

import study


def test_actual_shared64_inputs_and_cpu_entry_guard():
    import train
    ready, rows = train.preflight()
    assert ready["credit_mode"] == "joint" and len(rows) == 64
    try: train.trainer.run(study, study.OUTPUT, study.SCIENCE_SECONDS)
    except RuntimeError as error: assert str(error) == "CPU_ENTRY_VERIFIED: MAIN must assign one GPU before training"
    else: raise AssertionError("CPU training guard absent")
    assert not study.OUTPUT.exists()


def test_joint_credit_is_broadcast_before_equal_candidate_scaling():
    import torch
    import train
    _, credit = train.trainer.dependencies(study)
    values = torch.tensor([-2.0, -3.0], requires_grad=True)
    loss = credit.credit_loss(values, [1.0, 1.0], [0.5, 0.5],
        [[1.0,0.0],[0.0,1.0]], candidates=2, denominator=64)
    loss.backward(); assert torch.equal(values.grad, torch.tensor([-1/256,-1/256]))
    import checkpoint
    assert callable(checkpoint.endpoint) and Path(study.CONFIG_SOURCE).exists()

