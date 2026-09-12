import pytest

import arm_eval_study as study


def test_exact_frozen_unseen_schedule_is_reused():
 assert study.schedule()==study.source().schedule() and len(study.schedule())==64
 assert len({identifier for row in study.schedule() for identifier in row["ids"]})==256


@pytest.mark.parametrize("name",tuple(study.ARMS))
def test_arm_state_requires_exact_temperature_lr_and_step4_schema(name):
 public=study.experimental_arm(name);state={"schema":"helper-hf-onpolicy-fourstep-arm-state-v1","experimental_arm":public,"temperature":public["temperature"],"learning_rate":public["learning_rate"],"poststep_extra_forward_sweep":False}
 study.validate_arm_state(name,state)
 broken=dict(state);broken["learning_rate"]*=10
 with pytest.raises(ValueError,match="arm-specific"):study.validate_arm_state(name,broken)
