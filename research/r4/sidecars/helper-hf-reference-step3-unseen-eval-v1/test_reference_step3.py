import copy

import pytest

import study


def test_actual_eligibility_collector_and_final_lineage_fixture():
    receipt = study.qualify()
    p3 = study.TRAIN_OUTPUT / "checkpoint-0003"; p4 = study.TRAIN_OUTPUT / "checkpoint-0004"
    state3 = study.read(p3 / "state.json"); commit3 = study.read(p3 / "STEP_COMMIT.json")
    state4 = study.read(p4 / "state.json"); commit4 = study.read(p4 / "STEP_COMMIT.json")
    study._validate_step3_with_final_lineage(receipt, state3, commit3, state4, commit4)
    broken = copy.deepcopy(state4); broken["parent_identity"] = "0" * 64
    with pytest.raises(ValueError, match="does not descend"):
        study._validate_step3_with_final_lineage(receipt, state3, commit3, broken, commit4)
    assert receipt["evaluated_checkpoint_step"] == 3
    assert receipt["completed_reference_optimizer_steps"] == 4
    assert receipt["checkpoint"].endswith("checkpoint-0003")
    import owner
    assert callable(owner.build().execute)
