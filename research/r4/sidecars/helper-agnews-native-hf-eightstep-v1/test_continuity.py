"""Catch fresh-Adam resets, constructor RNG leakage and optimizer-state misbinding."""

import copy
import random

import numpy as np
import torch
import train_step


def test_two_actual_updates_equal_after_adapter_adam_rng_save_reload(tmp_path):
    from peft import LoraConfig, get_peft_model
    from transformers import Qwen3Config, Qwen3ForCausalLM

    torch.set_num_threads(2)
    torch.manual_seed(19)
    config = Qwen3Config(
        vocab_size=16,
        hidden_size=16,
        intermediate_size=32,
        num_hidden_layers=2,
        num_attention_heads=2,
        num_key_value_heads=1,
        head_dim=8,
        attention_dropout=0,
    )
    config._attn_implementation = "sdpa"

    def create():
        return get_peft_model(
            Qwen3ForCausalLM(config),
            LoraConfig(r=2, lora_alpha=4, lora_dropout=0, target_modules=["q_proj", "v_proj"]),
        ).eval()

    model = create()
    model.config.use_cache = False
    base_state = copy.deepcopy(model.state_dict())
    optimizer = train_step.make_optimizer(model)
    masks = {
        str(i): np.array([[(1 << 2) | (1 << 3)], [1 << 1]], dtype=np.int32) for i in range(128)
    }

    def actions(policy, step):
        records = []
        for i in range(128):
            row = {
                "episode_id": f"{step}:{i}",
                "group_id": str(i // 4),
                "input_ids": [4, 5, 6, 2 + i % 2, 1],
                "prompt_length": 3,
                "selected_positions": [3, 4],
                "action_ids": [2 + i % 2, 1],
                "temperature": 0.5,
                "mask_key": str(i),
                "reward": [0, 0.25, 0.75, 1][i % 4],
            }
            row["old_logprobs"] = (
                train_step.modules()
                .train._selected_logprobs(policy, row, masks[str(i)], require_grad=False)
                .tolist()
            )
            records.append(row)
        return records

    random.seed(29)
    np.random.seed(29)
    torch.manual_seed(29)
    result1 = train_step.update_once(
        model, optimizer, actions(model, 1), masks, tmp_path / "step1", 0
    )
    assert result1["status"] == "UPDATED" and result1["optimizer_state_steps"] == [1]
    train_step.save_training_state(model, optimizer, tmp_path / "saved", 1)
    records2 = actions(model, 2)
    rng_draws = (random.random(), float(np.random.random()), torch.rand(3))
    result2 = train_step.update_once(model, optimizer, records2, masks, tmp_path / "direct", 1)
    expected_model = copy.deepcopy(model.state_dict())
    expected_optimizer = copy.deepcopy(optimizer.state_dict())
    expected_gradients = {
        name: p.grad.detach().clone() for name, p in model.named_parameters() if p.requires_grad
    }
    resumed = create()  # Constructor consumes Torch RNG before the restore.
    resumed.load_state_dict(base_state)
    resumed_optimizer = train_step.make_optimizer(resumed)
    train_step.restore_training_state(resumed, resumed_optimizer, tmp_path / "saved", 1)
    assert (random.random(), float(np.random.random())) == rng_draws[:2]
    assert torch.equal(torch.rand(3), rng_draws[2])
    replay_result = train_step.update_once(
        resumed, resumed_optimizer, records2, masks, tmp_path / "resumed", 1
    )
    assert result2["optimizer_state_steps"] == replay_result["optimizer_state_steps"] == [2]
    assert all(
        torch.equal(value, resumed.state_dict()[key]) for key, value in expected_model.items()
    )
    for name, parameter in resumed.named_parameters():
        if parameter.requires_grad:
            assert torch.equal(parameter.grad, expected_gradients[name])
    actual_optimizer = resumed_optimizer.state_dict()
    assert expected_optimizer["param_groups"] == actual_optimizer["param_groups"]
    for index, values in expected_optimizer["state"].items():
        for key, value in values.items():
            assert torch.equal(value, actual_optimizer["state"][index][key])
    before = copy.deepcopy(resumed.state_dict())
    bad = copy.deepcopy(records2)
    bad[0]["old_logprobs"][0] -= 20
    rejected = train_step.update_once(resumed, resumed_optimizer, bad, masks, tmp_path / "bad", 2)
    assert rejected["status"] == "NO_UPDATE_LIKELIHOOD_GATE_FAILED"
    assert rejected["optimizer_steps"] == 2
    assert all(torch.equal(value, resumed.state_dict()[key]) for key, value in before.items())
    assert train_step.optimizer_steps(resumed_optimizer) == [2]
