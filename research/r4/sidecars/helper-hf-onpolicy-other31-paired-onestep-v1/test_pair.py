"""Focused paired-baseline, restore, replay, and evaluator-interface checks."""

import copy
import hashlib
import json
import shutil

import numpy as np
import pytest
import torch


def test_other31_excludes_all_four_current_actions_and_preserves_failures():
    from pair_math import paired_advantages

    rewards = [[0.0] * 4, [1.0] * 4] + [[0.0, 1.0, 0.0, 1.0] for _ in range(30)]
    result = paired_advantages(rewards)
    assert result[0]["other31_baseline"] == pytest.approx(64 / 124)
    assert result[0]["other31"] == pytest.approx([-64 / 124] * 4)
    assert result[0]["rloo"] == [0.0] * 4
    assert result[0]["all_failure"] is True
    assert result[1]["other31_baseline"] == pytest.approx(60 / 124)
    assert len(result) == 32 and sum(len(row["other31"]) for row in result) == 128


def test_restore_is_bit_identical_and_new_adam_has_no_carried_state():
    from pair_math import assert_snapshot, restore_snapshot, snapshot_trainable

    model = torch.nn.Sequential(torch.nn.Linear(3, 4), torch.nn.Linear(4, 2))
    snapshot = snapshot_trainable(model)
    first = torch.optim.AdamW(model.parameters(), lr=1e-5)
    model(torch.ones(1, 3)).sum().backward()
    first.step()
    assert first.state
    restore_snapshot(model, snapshot)
    assert_snapshot(model, snapshot)
    fresh = torch.optim.AdamW(model.parameters(), lr=1e-5)
    assert not fresh.state
    assert first is not fresh


class TinyGrammar:
    def init(self, schema):
        self.offset = 0
        self.terminated = [False] * 4
        return {"schema_sha256": hashlib.sha256(schema.encode()).hexdigest(), "versions": {}}

    def masks(self):
        words = np.array(
            [[(1 << 2) | (1 << 3)] if self.offset == 0 else [1 << 1]] * 4,
            dtype=np.int32,
        )
        return words, {
            "terminated": self.terminated,
            "sha256": hashlib.sha256(words.tobytes()).hexdigest(),
        }

    def accept(self, tokens):
        self.offset += 1
        self.terminated = [token == 1 for token in tokens]
        return {"terminated": self.terminated}


class TinyTokenizer:
    def decode(self, tokens, **_kwargs):
        return json.dumps({"q": "entity" if tokens[0] == 2 else "location"})


def tiny_model():
    from peft import LoraConfig, get_peft_model
    from transformers import Qwen3Config, Qwen3ForCausalLM

    torch.manual_seed(9)
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
    config._attn_implementation = "eager"
    model = get_peft_model(
        Qwen3ForCausalLM(config),
        LoraConfig(r=2, lora_alpha=4, lora_dropout=0, target_modules=["q_proj", "v_proj"]),
    ).eval()
    with torch.no_grad():
        for name, value in model.named_parameters():
            if "lora_B" in name:
                value.normal_(0, 0.01)
    return model


def test_actual_replay_is_onpolicy_and_gradient_scales_with_fixed_128_denominator(
    monkeypatch, tmp_path
):
    import source

    implementation = source.load()
    monkeypatch.setattr(implementation.core.v1, "VOCAB", 16)
    monkeypatch.setattr(implementation.core.v1, "STOP_IDS", [1])
    monkeypatch.setattr(implementation.core.v1, "MAX_NEW", 2)
    model = tiny_model()
    group = {
        "group_id": "g",
        "public_record": {"id": "q", "text": "toy"},
        "prompt_ids": [4, 5, 6],
        "schema_ordered_json": "{}",
        "schema_ordered_sha256": hashlib.sha256(b"{}").hexdigest(),
    }
    source_dir = tmp_path / "source"
    record = implementation.core.v1.rollout_group(
        model,
        TinyGrammar(),
        TinyTokenizer(),
        group,
        0,
        torch.Generator().manual_seed(18),
        source_dir,
    )
    norms = []
    for scale in (1.0, 2.0):
        destination = tmp_path / f"branch-{scale}"
        destination.mkdir()
        shutil.copyfile(source_dir / "MASKS.npz", destination / "MASKS.npz")
        model.zero_grad(set_to_none=True)
        replay = implementation.core.v1.replay_group(
            model,
            TinyGrammar(),
            group,
            copy.deepcopy(record),
            [scale, -scale, scale, -scale],
            destination,
        )
        assert replay["passed"] and replay["batch_denominator"] == 128
        assert replay["maximum_token_logprob_error"] == 0
        assert replay["maximum_sequence_logprob_error"] == 0
        norms.append(
            torch.sqrt(
                sum(
                    parameter.grad.detach().float().square().sum()
                    for parameter in model.parameters()
                    if parameter.grad is not None
                )
            ).item()
        )
    assert norms[0] > 0 and norms[1] == pytest.approx(2 * norms[0], rel=2e-5)


def test_evaluator_handoff_requires_exact_branch_and_step1_binding(tmp_path):
    from eligibility import validate_handoff

    checkpoint = tmp_path / "checkpoint-0001"
    checkpoint.mkdir()
    (checkpoint / "adapter_model.safetensors").write_bytes(b"adapter")
    (checkpoint / "adapter_config.json").write_text("{}")
    binding = {
        "role_map": {"root": "root", "children": ["child"]},
        "fixed_child": "child",
        "models": {
            "root": {"path": "root", "adapter_sha256": "root"},
            "child": {
                "path": str(checkpoint),
                "adapter_sha256": hashlib.sha256(b"adapter").hexdigest(),
                "config_sha256": hashlib.sha256(b"{}").hexdigest(),
            },
        },
        "child_only_update": {
            "experiment": "helper-hf-onpolicy-other31-paired-onestep-v1",
            "branch": "other31",
            "step": 1,
            "baseline": "detached leave-current-question-out other31x4 mean",
            "shared_collection_sha256": "shared",
            "root_unchanged": True,
        },
    }
    state = {
        "schema": "helper-hf-onpolicy-other31-paired-state-v1",
        "branch": "other31",
        "step": 1,
        "optimizer_state_steps": [1],
        "shared_collection_sha256": "shared",
        "baseline": "detached leave-current-question-out other31x4 mean",
    }
    assert validate_handoff(checkpoint, state, binding)["branch"] == "other31"
    binding["child_only_update"]["branch"] = "rloo"
    with pytest.raises(ValueError, match="branch"):
        validate_handoff(checkpoint, state, binding)
