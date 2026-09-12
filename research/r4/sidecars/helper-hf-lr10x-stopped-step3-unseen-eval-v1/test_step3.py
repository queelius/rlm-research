import copy
import json

import pytest

import study


def test_exact_stopped_step3_terminal_fixture(tmp_path, monkeypatch):
    output = tmp_path / "attempt"; output.mkdir(); (output / "checkpoint-0003").mkdir()
    monkeypatch.setattr(study, "OUTPUT", output)
    result = {"status": "STOP_ZERO_ADVANTAGE", "completed_optimizer_steps": 3,
        "current_step_applied": False, "primary_checkpoint_available": False,
        "checkpoints": [{"step": 1}, {"step": 2},
            {"step": 3, "checkpoint": str(output / "checkpoint-0003")}],
        "primary_checkpoint": None, "primary_checkpoint_step": None}
    assert len(study._terminal_entries(result)) == 3
    applied = copy.deepcopy(result); applied["completed_optimizer_steps"] = 4
    with pytest.raises(ValueError, match="exact zero-advantage"): study._terminal_entries(applied)
    (output / "checkpoint-0004").mkdir()
    with pytest.raises(ValueError, match="checkpoint-0004 exists"): study._terminal_entries(result)


def test_actual_eligibility_and_collector_build():
    receipt = study.qualify()
    assert receipt["checkpoint"].endswith("checkpoint-0003")
    assert receipt["fixed_fourstep_primary"] is False
    action = receipt["update4_action_eligibility"]
    assert (action["all_correct_groups"], action["all_wrong_groups"], action["mixed_groups"]) == (30, 2, 0)
    assert action["hypothetical_other31_nonzero_actions"] == 128
    import owner
    collector = owner.build()
    assert callable(collector.execute)
