"""Focused tests for arm isolation, temperature flow, entropy, and LR receipts."""

import hashlib
import json

import numpy as np
import pytest
import torch


class FakeModel:
    training = False
    is_gradient_checkpointing = False
    device = torch.device("cpu")

    def modules(self):
        return []


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


def test_t2_reaches_actual_rollout_and_replay_and_records_live_entropy(monkeypatch, tmp_path):
    import arm_runtime
    import study

    source = arm_runtime.load_source()
    monkeypatch.setattr(source.core.v1, "VOCAB", 16)
    monkeypatch.setattr(source.core.v1, "STOP_IDS", [1])
    monkeypatch.setattr(source.core.v1, "MAX_NEW", 2)

    def logits(_model, ids):
        values = torch.full((4, 16), -4.0)
        values[:, 2] = 2.0
        values[:, 3] = 0.0
        values[:, 1] = 1.0
        return values

    monkeypatch.setattr(source.core.v1, "prefix_logits", logits)
    receipt = arm_runtime.install(source, study.ARMS["t2_lr1e5"])
    directory = tmp_path / "group"
    group = {
        "group_id": "g",
        "public_record": {"id": "q", "text": "toy"},
        "prompt_ids": [4, 5, 6],
        "schema_ordered_json": "{}",
        "schema_ordered_sha256": hashlib.sha256(b"{}").hexdigest(),
    }
    record = source.core.v1.rollout_group(
        FakeModel(),
        TinyGrammar(),
        TinyTokenizer(),
        group,
        0,
        torch.Generator().manual_seed(3),
        directory,
    )
    replay = source.core.v1.replay_group(
        FakeModel(), TinyGrammar(), group, record, [0.0] * 4, directory
    )
    assert replay["passed"]
    assert receipt["temperature_paths"] == {"rollout", "replay"}
    assert record["branching_entropy"]["live_positions_total"] == 8
    assert record["branching_entropy"]["live_positions_nonforced"] == 4
    assert record["branching_entropy"]["temperature"] == 2.0
    assert record["sampled_sequence_logprob_sums"] == pytest.approx(
        [sum(row) for row in replay["old_logprobs"]]
    )


@pytest.mark.parametrize(
    ("arm_name", "temperature", "learning_rate"),
    [("t2_lr1e5", 2.0, 1e-5), ("t1_lr1e4", 1.0, 1e-4)],
)
def test_arm_configures_optimizer_gate_and_truthful_state(
    monkeypatch, tmp_path, arm_name, temperature, learning_rate
):
    import arm_runtime
    import study

    source = arm_runtime.load_source()
    monkeypatch.setattr(source, "execute_update", lambda *_args, **_kwargs: {
        "status": "STOP_ZERO_ADVANTAGE",
        "collection": {},
        "optimizer_step_applied": False,
    })
    arm_runtime.install(source, study.ARMS[arm_name])
    optimizer = torch.optim.AdamW([torch.nn.Parameter(torch.ones(1))], lr=learning_rate)
    result = source.execute_update(
        None, optimizer, None, None, [], {}, None, 1, tmp_path / "update", "c32", "ready"
    )
    assert result["status"] == "STOP_ZERO_ADVANTAGE"
    assert source.LR == learning_rate
    assert source.core.v1.TEMPERATURE == temperature
    state_path = tmp_path / "state.json"
    source.core.write(state_path, {"temperature": 999, "learning_rate": 999})
    state = json.loads(state_path.read_text())
    assert state["temperature"] == temperature
    assert state["learning_rate"] == learning_rate
    assert state["experimental_arm"]["name"] == arm_name
