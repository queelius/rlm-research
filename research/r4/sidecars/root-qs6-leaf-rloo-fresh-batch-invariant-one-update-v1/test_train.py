import json
from pathlib import Path

import pytest
import torch

import train


def test_exact_formula_uses_sequence_sum_denominator48_and_detaches_ratio():
 values=torch.tensor([-0.2,-0.3],requires_grad=True);ratio=torch.tensor(1.5,requires_grad=True)
 loss=train.objective_term(values,ratio,2.0,48);loss.backward()
 assert loss.item()==pytest.approx(1.5*2*.5/48)
 assert values.grad.tolist()==pytest.approx([-3/48,-3/48])
 assert ratio.grad is None


def test_gradient_replay_failure_is_prospective():
 assert train.replay_difference([0.0,-0.1],[0.0,-0.1])["passed"] is True
 failed=train.replay_difference([0.0,-0.10002],[0.0,-0.1])
 assert failed["passed"] is False and failed["max_token_error"]>train.TOKEN_TOL
 result=train.replay_failure_result("replay-sha")
 assert result["status"]=="NO_UPDATE_GRADIENT_REPLAY_FAILED"
 assert result["optimizer_steps"]==0 and result["gradient_replay_check_sha256"]=="replay-sha"


def test_output_and_frozen_inventory_contracts():
 assert train.expected_output(train.ROOT/"outputs/attempt-001").name=="attempt-001"
 with pytest.raises(ValueError,match="exact sealed output"):train.expected_output(Path("/tmp/not-the-output"))
 source=train.load_source();dataset,records,_masks,qualification=train.load_inputs(source)
 assert len(records)==48 and len(qualification["ratios"])==48
 assert sum(len(row["action_ids"]) for row in records)==11901
