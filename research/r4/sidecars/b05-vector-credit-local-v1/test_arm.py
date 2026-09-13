"""Focused candidate-local input, gradient, owner, and checkpoint-interface tests."""

from pathlib import Path

import study


def test_actual_shared64_inputs_and_cpu_entry_guard():
    import train
    ready, rows = train.preflight()
    assert ready["credit_mode"] == "local" and len(rows) == 64
    assert all(row["episode_id"] for row in rows)
    try: train.trainer.run(study, study.OUTPUT, study.SCIENCE_SECONDS)
    except RuntimeError as error: assert str(error) == "CPU_ENTRY_VERIFIED: MAIN must assign one GPU before training"
    else: raise AssertionError("CPU training guard absent")
    assert not study.OUTPUT.exists()


def test_actual_tiny_zero_B_gradient_and_fresh_adam():
    import torch
    from transformers import Qwen3Config, Qwen3ForCausalLM
    import train
    model_core, credit = train.trainer.dependencies(study)
    torch.set_num_threads(1); torch.manual_seed(31)
    base = Qwen3ForCausalLM(Qwen3Config(vocab_size=32, hidden_size=16, intermediate_size=32,
        num_hidden_layers=1, num_attention_heads=2, num_key_value_heads=1, head_dim=8,
        attention_dropout=0.0)); base.config._name_or_path = str(study.BASE)
    model = model_core.initialize(base); initial = model_core.math.snapshot_trainable(model)
    turn = {"prompt_ids": [1,2,3], "action_ids": [4,5,6], "input_ids": [1,2,3,4,5,6],
        "labels": [-100,-100,-100,4,5,6], "loss_mask": [0,0,0,1,1,1],
        "old_logprobs": [-3.0] * 3}
    values = model_core.selected_logprobs(model, turn, require_grad=True); values.retain_grad()
    loss = credit.credit_loss(values, [1.0] * 3, [1.0, -1.0],
        [[1.0,0.0],[0.0,1.0],[0.0,0.0]], candidates=2, denominator=64)
    loss.backward(); assert torch.equal(values.grad, torch.tensor([-1/128,1/128,0.0]))
    gradients = {name: parameter.grad.clone() if parameter.grad is not None else torch.zeros_like(parameter)
                 for name, parameter in model.named_parameters() if parameter.requires_grad}
    branch = model_core.math.apply_fresh_adam_branch(model, initial, gradients, learning_rate=1e-4)
    assert branch["optimizer_state_empty_before_step"] and branch["optimizer_state_steps"] == [1]
    import checkpoint
    assert callable(checkpoint.endpoint) and Path(study.CONFIG_SOURCE).exists()

