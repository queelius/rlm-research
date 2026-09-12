"""Catches replay-gate bypass through a real tiny HF/PEFT optimizer path."""

import copy
import importlib.util
from pathlib import Path

import numpy as np
import torch


def test_actual_tiny_hf_update_and_mismatch_no_step(tmp_path):
    path = Path(__file__).with_name("train_ag.py")
    assert path.exists(), "single-load numeric update is not implemented"
    spec = importlib.util.spec_from_file_location("ag_train_fixture", path)
    train = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(train)
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
    model = get_peft_model(
        Qwen3ForCausalLM(config),
        LoraConfig(r=2, lora_alpha=4, lora_dropout=0, target_modules=["q_proj", "v_proj"]),
    ).eval()
    model.config.use_cache = False
    initial = copy.deepcopy(model.state_dict())
    modules = train.study.numeric_modules()
    records, masks = [], {}
    for index in range(128):
        record = {
            "episode_id": str(index),
            "group_id": str(index // 4),
            "input_ids": [4, 5, 6, 2 + index % 2, 1],
            "prompt_length": 3,
            "selected_positions": [3, 4],
            "action_ids": [2 + index % 2, 1],
            "temperature": 0.5,
            "mask_key": str(index),
            "reward": [0, 0.25, 0.75, 1][index % 4],
        }
        masks[str(index)] = np.array([[(1 << 2) | (1 << 3)], [1 << 1]], dtype=np.int32)
        record["old_logprobs"] = modules.train._selected_logprobs(
            model, record, masks[str(index)], require_grad=False
        ).tolist()
        records.append(record)
    rejected = copy.deepcopy(records)
    # Same model/masks and all supported, but impossible behavior likelihoods fail ESS.
    rejected[0]["old_logprobs"][0] -= 20
    no_update = train.numeric_update(model, rejected, masks, tmp_path / "bad")
    assert no_update["status"] == "NO_UPDATE_LIKELIHOOD_GATE_FAILED"
    assert no_update["optimizer_steps"] == 0
    assert all(torch.equal(initial[key], value) for key, value in model.state_dict().items())
    qualification = train.qualify_model(model, records, masks)
    qualification["current_token_logprobs"][0][0] += 0.0002
    failed_replay = train.gradient_update(
        model, records, masks, qualification, tmp_path / "bad-replay"
    )
    assert failed_replay["status"] == "NO_UPDATE_GRADIENT_REPLAY_FAILED"
    assert failed_replay["optimizer_steps"] == 0
    assert not (tmp_path / "bad-replay/optimizer.pt").exists()
    assert all(torch.equal(initial[key], value) for key, value in model.state_dict().items())
    result = train.numeric_update(model, records, masks, tmp_path / "good")
    assert result["status"] == "UPDATED" and result["optimizer_steps"] == 1
    assert result["optimizer_state_steps"] == [1]
    assert result["gradient_norm_before_clip"] > 0 and result["adapter_delta_l2"] > 0
    assert result["gradient_replay"]["all128_passed"]
    assert result["batch_denominator"] == 128
