import copy
import math
from pathlib import Path

import pytest

import fourstep_panel_study as study


def test_schedule_is_exact_frozen_c32_unseen_policy():
    rows=study.schedule();assert rows==study.source().schedule();assert len(rows)==64
    assert len({identifier for row in rows for identifier in row["ids"]})==256
    for row in rows:
        schema=row["body"]["sampling_params"]["structured_outputs"]["json"]
        assert row["body"]["sampling_params"]["temperature"]==0
        assert list(schema["properties"])==row["ids"]==schema["required"]


def test_final_header_rejects_wrong_primary_step(tmp_path):
    result={"status":"COMPLETED_FOUR_UPDATES","completed_optimizer_steps":4,
        "primary_checkpoint_available":True,"primary_checkpoint_step":3,
        "primary_checkpoint":str(tmp_path/"checkpoint-0003"),
        "checkpoints":[{"step":i,"checkpoint":str(tmp_path/f"checkpoint-{i:04d}")} for i in range(1,5)]}
    with pytest.raises(ValueError,match="primary step4"):
        study.validate_final_result(result,tmp_path)


def test_lineage_header_rejects_missing_previous_commit():
    parent={"path":"checkpoint-0001/STEP_COMMIT.json","sha256":"abc"}
    state={"step":2,"cumulative_optimizer_steps":2,"optimizer_state_steps":[2],
        "ready_identity":"ready","parent_identity":"state1","parent_step_commit":None}
    commit={"step":2,"cumulative_optimizer_steps":2,"ready_identity":"ready",
        "parent_identity":"state1","parent_step_commit":parent,"status":"UPDATED"}
    with pytest.raises(ValueError,match="lineage"):
        study.validate_lineage_header(2,state,commit,"state1",parent,"ready")


def test_probability_gate_recomputes_token_sequence_and_support_errors():
    group={"passed":True,"finite":True,"batch_denominator":128,"sequence_reduction":"sum",
        "current_logprobs":[[-0.2,-0.3],[-0.1],[-0.4],[-0.5]],
        "old_logprobs":[[-0.2,-0.3],[-0.1],[-0.4],[-0.5]],
        "maximum_token_logprob_error":0.0,"maximum_sequence_logprob_error":0.0,
        "support_maximum_logprob_error":0.0,"full_support_audited":True}
    study.verify_probability_group(group,0,copy.deepcopy(group))
    broken=copy.deepcopy(group);broken["current_logprobs"][0][0]+=2e-5
    broken["maximum_token_logprob_error"]=2e-5;broken["maximum_sequence_logprob_error"]=2e-5
    with pytest.raises(ValueError,match="probability gate"):
        study.verify_probability_group(broken,0,copy.deepcopy(broken))
