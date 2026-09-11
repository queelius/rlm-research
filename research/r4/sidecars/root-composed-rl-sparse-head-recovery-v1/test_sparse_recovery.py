import json
from pathlib import Path
import subprocess

import pytest

import sparse_math as math
import sparse_owner as owner
import sparse_study as study


def test_selected_positions_are_exact_action_predecessors():
    turn = {"prompt_length": 7, "input_ids": list(range(12)), "old_logprobs": [0.0] * 5}
    assert math.position_list(turn) == [6, 7, 8, 9, 10]
    with pytest.raises(ValueError):
        math.position_list({**turn, "prompt_length": 0})


def test_selected_loss_rebuilds_masked_local_capture_contract():
    class Shape:
        shape = (1, 2, 9)

    class Strict:
        @staticmethod
        def tis_action_loss(logits, turn, **kwargs):
            assert turn["input_ids"] == [12, 13, 14]
            assert turn["prompt_length"] == 1
            assert turn["labels"] == [-100, 13, 14]
            assert turn["loss_mask"] == [0, 1, 1]
            return "loss", "capture"

    turn = {"input_ids": [10, 11, 12, 13, 14], "prompt_length": 3,
            "old_logprobs": [-1.0, -2.0], "labels": [-100, -100, -100, 13, 14],
            "loss_mask": [0, 0, 0, 1, 1]}
    assert math.selected_tis_loss(Shape(), turn, advantage=1, temperature=.5, tis=Strict) == ("loss", "capture")


def test_cpu_tiny_qwen_equivalence_fixture():
    result = subprocess.run(
        [str(study.TRAIN), str(study.ROOT / "cpu_equivalence.py")],
        check=True,
        text=True,
        capture_output=True,
        env={"CUDA_VISIBLE_DEVICES": "", "PATH": "/usr/bin:/bin"},
        timeout=180,
    )
    receipt = json.loads(result.stdout)
    assert receipt["device"] == "cpu"
    assert receipt["loss_close"] and receipt["logprobs_close"] and receipt["gradients_close"]
    assert receipt["full_positions"] > receipt["selected_positions"] > 0


def test_frozen_failed_group_and_checkpoint_are_authenticated():
    receipt = study.verify_inputs()
    assert receipt["previous_optimizer_step"] == 1
    assert receipt["target_optimizer_step"] == 2
    assert receipt["episodes"] == 11
    assert receipt["turns"] == 154
    assert receipt["causal_tokens"] == 647114
    assert receipt["action_tokens"] == 18517
    assert receipt["max_sequence_tokens"] == 8192
    assert receipt["max_action_tokens"] == 219


def test_owner_has_inclusive_two_stage_budget_and_exact_attempt(tmp_path):
    budget = owner.budget(1000.0)
    assert budget == {
        "started": 1000.0,
        "qualification_end": 1900.0,
        "work_end": 3700.0,
        "owned_end": 3970.0,
        "outer_end": 4000.0,
    }
    assert owner.stage_deadline("qualification", 1000.0, budget) == 1900.0
    assert owner.stage_deadline("training", 1900.0, budget) == 3700.0
    with pytest.raises(ValueError):
        owner.check_output(tmp_path)


def test_training_cannot_start_without_passed_qualification(tmp_path):
    with pytest.raises(ValueError):
        owner.require_qualification(tmp_path)
    q = {
        "schema": "root-composed-rl-sparse-head-qualification-v1",
        "passed": True,
        "optimizer_steps": 0,
        "short_equivalence": {"passed": True},
        "longest_sparse": {"passed": True},
        "checkpoint1_state_sha256": study.PINS[study.CHECKPOINT / "state.json"],
        "group_sha256": study.PINS[study.GROUP],
    }
    path = tmp_path / "QUALIFICATION_RESULT.json"
    path.write_text(json.dumps(q))
    assert owner.require_qualification(tmp_path) == q


def test_stage_commands_bind_exact_inputs_and_caps():
    q = owner.qualification_argv(Path("/tmp/x"), 1234.0)
    t = owner.training_argv(Path("/tmp/x"), 2345.0)
    assert q[-2:] == ["--deadline", "1234.0"]
    assert t[-2:] == ["--deadline", "2345.0"]
    assert str(study.GROUP) in q and str(study.GROUP) in t
    assert str(study.GENERATION) in q and str(study.GENERATION) in t
    assert str(study.CHECKPOINT) in q and str(study.CHECKPOINT) in t
    assert "qualification" in q[q.index("--output") + 1]
    assert "training" in t[t.index("--output") + 1]


def test_prepared_identity_reauthenticates_every_owned_source():
    ready = study.verify_prepared()
    assert ready["identity"] == study.read(study.ROOT / "READY.json")["identity"]
    assert ready["frozen_inventory"] == study.verify_inputs()
