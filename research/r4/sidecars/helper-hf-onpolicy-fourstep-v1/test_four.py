"""Focused behavioral checks of fresh multi-step policy, AdamW carry, and receipts."""

import copy
import hashlib
import json
import random
import time

import numpy as np
import pytest
import torch


def test_full_rng_snapshot_restores_next_global_and_categorical_draws(tmp_path):
    from rng_receipts import restore_rng, save_rng

    random.seed(4)
    np.random.seed(5)
    torch.manual_seed(6)
    generator = torch.Generator().manual_seed(7)
    save_rng(tmp_path / "rng.pt", generator)

    def draw():
        return (
            random.random(),
            np.random.rand(),
            torch.rand(4),
            torch.multinomial(
                torch.tensor([0.1, 0.2, 0.7]), 20, replacement=True, generator=generator
            ),
        )

    first = draw()
    restore_rng(tmp_path / "rng.pt", generator)
    second = draw()
    assert first[:2] == second[:2]
    assert torch.equal(first[2], second[2]) and torch.equal(first[3], second[3])


def test_group_commit_rejects_changed_files_and_wrong_frozen_parent(tmp_path):
    from rng_receipts import commit_files, verify_commit

    path = tmp_path / "actions.json"
    path.write_text("[]")
    commit_files(tmp_path / "GROUP_COMMIT.json", [path], {"parent_identity": "parent-a"})
    assert (
        verify_commit(tmp_path / "GROUP_COMMIT.json", "parent-a")["parent_identity"] == "parent-a"
    )
    with pytest.raises(ValueError, match="parent"):
        verify_commit(tmp_path / "GROUP_COMMIT.json", "parent-b")
    path.write_text("[1]")
    with pytest.raises(ValueError, match="changed"):
        verify_commit(tmp_path / "GROUP_COMMIT.json", "parent-a")


class TinyGrammar:
    """A real categorical support followed by EOS, without loading a second environment."""

    def init(self, schema):
        self.offset = 0
        self.terminated = [False] * 4
        return {
            "schema_sha256": hashlib.sha256(schema.encode()).hexdigest(),
            "versions": {"toy": 1},
        }

    def masks(self):
        words = np.array(
            [[(1 << 2) | (1 << 3)] if self.offset == 0 else [1 << 1]] * 4, dtype=np.int32
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


def tiny_setup(monkeypatch):
    import core
    import train_four
    from peft import LoraConfig, get_peft_model
    from transformers import Qwen3Config, Qwen3ForCausalLM

    torch.set_num_threads(2)
    torch.manual_seed(103)
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
    core.install_eval_checkpoints(model)
    monkeypatch.setattr(core.v1, "VOCAB", 16)
    monkeypatch.setattr(core.v1, "STOP_IDS", [1])
    monkeypatch.setattr(core.v1, "MAX_NEW", 2)
    # Production denominator stays128 even in this smaller CPU fixture.
    monkeypatch.setattr(train_four, "GROUPS", 4)
    groups = [
        {
            "group_id": f"g-{index}",
            "public_record": {"id": "q", "text": "toy"},
            "prompt_ids": [4, 5, 6],
            "schema_ordered_json": "{}",
            "schema_ordered_sha256": hashlib.sha256(b"{}").hexdigest(),
        }
        for index in range(4)
    ]
    optimizer = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad], lr=1e-5, weight_decay=0
    )
    return model, optimizer, groups, {group["group_id"]: "entity" for group in groups}


def test_four_actual_hf_updates_refresh_actions_and_carry_one_adamw(monkeypatch, tmp_path):
    import core
    import train_four

    model, optimizer, groups, gold = tiny_setup(monkeypatch)
    generator = torch.Generator().manual_seed(904)
    model.config.save_pretrained(tmp_path / "tiny_base")
    model.peft_config["default"].base_model_name_or_path = str(tmp_path / "tiny_base")
    initial = copy.deepcopy(model.state_dict())
    initial_adapter = train_four.parameter_snapshot(model)
    output = tmp_path / "attempt"
    output.mkdir()
    parent_identity, parent_commit = "c32", None
    original_rollout = core.v1.rollout_group
    sampled_step_counts = []

    def observed_rollout(*args, **kwargs):
        sampled_step_counts.append({int(value["step"]) for value in optimizer.state.values()})
        return original_rollout(*args, **kwargs)

    monkeypatch.setattr(core.v1, "rollout_group", observed_rollout)
    for step in range(1, 5):
        result = train_four.execute_update(
            model,
            optimizer,
            TinyGrammar(),
            TinyTokenizer(),
            groups,
            gold,
            generator,
            step,
            output / "updates" / f"update-{step:04d}",
            parent_identity,
            "cpu-ready",
        )
        assert result["status"] == "UPDATED"
        assert result["qualification"]["all_passed"]
        assert all(q["batch_denominator"] == 128 for q in result["qualification"]["groups"])
        assert {int(value["step"]) for value in optimizer.state.values()} == {step}
        assert result["adapter_delta_l2"] > 0
        checkpoint, receipt = train_four.save_checkpoint(
            model,
            optimizer,
            generator,
            output,
            step,
            result,
            parent_identity,
            parent_commit,
            "cpu-ready",
            initial_adapter,
            time.monotonic(),
        )
        from rng_receipts import verify_commit

        assert verify_commit(checkpoint / "STEP_COMMIT.json", parent_identity) == receipt
        assert receipt["cumulative_optimizer_steps"] == step
        state = core.read(checkpoint / "state.json")
        assert state["step"] == step and state["optimizer_state_steps"] == [step]
        assert state["parent_step_commit"] == parent_commit
        assert all("lora_" in name for name in state["optimizer_parameter_names"])
        assert (
            len(
                list((output / "updates" / f"update-{step:04d}").glob("groups/*/GROUP_COMMIT.json"))
            )
            == 4
        )
        parent_identity = core.sha(checkpoint / "state.json")
        parent_commit = {
            "path": str(checkpoint / "STEP_COMMIT.json"),
            "sha256": core.sha(checkpoint / "STEP_COMMIT.json"),
        }
    assert sampled_step_counts == [set()] * 4 + [{1}] * 4 + [{2}] * 4 + [{3}] * 4
    assert any(not torch.equal(value, initial[key]) for key, value in model.state_dict().items())
    assert not model.training and not model.is_gradient_checkpointing


def test_probability_failure_never_applies_current_optimizer_step(monkeypatch, tmp_path):
    import core
    import train_four

    model, optimizer, groups, gold = tiny_setup(monkeypatch)
    before = copy.deepcopy(model.state_dict())
    original = core.v1.rollout_group

    def changed(*args, **kwargs):
        record = original(*args, **kwargs)
        record["steps"][0]["old_logprobs"][0] -= 0.1
        return record

    monkeypatch.setattr(core.v1, "rollout_group", changed)
    result = train_four.execute_update(
        model,
        optimizer,
        TinyGrammar(),
        TinyTokenizer(),
        groups,
        gold,
        torch.Generator().manual_seed(904),
        1,
        tmp_path / "update",
        "c32",
        "cpu-ready",
    )
    assert result["status"] == "STOP_PROBABILITY_GATE"
    assert not optimizer.state
    assert all(torch.equal(value, before[key]) for key, value in model.state_dict().items())


def test_uniform_rewards_preserve_parameters_and_do_not_create_adamw_state(monkeypatch, tmp_path):
    import core
    import train_four

    model, optimizer, groups, gold = tiny_setup(monkeypatch)
    before = copy.deepcopy(model.state_dict())
    monkeypatch.setattr(core.v1, "local_reward", lambda *_args: 1.0)
    result = train_four.execute_update(
        model,
        optimizer,
        TinyGrammar(),
        TinyTokenizer(),
        groups,
        gold,
        torch.Generator().manual_seed(904),
        1,
        tmp_path / "update",
        "c32",
        "cpu-ready",
    )
    assert result["status"] == "STOP_ZERO_ADVANTAGE"
    assert all(row["passed"] for row in result["qualification"]["groups"])
    assert not optimizer.state
    assert all(torch.equal(value, before[key]) for key, value in model.state_dict().items())
