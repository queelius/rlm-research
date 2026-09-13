"""Focused frozen schedule, checkpoint binding, request, and metric contracts."""
import copy
import metrics,study
def test_actual_schedule_and_checkpoint_binding():
    ready=study.verify();assert ready["planned_calls"]==72
    calls=study.calls();assert len(calls)==72 and all(c["split"]=="held" for c in calls)
    assert {c["arm"] for c in calls}==set(study.ARMS)
    for root in study.tasks():
        rows=[c for c in calls if c["root_id"]==root["root_id"]]
        assert len(rows)==6 and len({(c["repeat"],c["seed"]) for c in rows})==2
    binding=study.binding();assert len(binding["models"])==2 and binding["base_control_adapter"] is None
    request=study.request_for(calls[0]);assert request["model"] in {str(study.BASE),study.local_alias(),study.joint_alias()}
    assert request["sampling_params"]["temperature"]==0.5
def test_all_unknown_remains_unknown():
    call=copy.deepcopy(study.calls()[0])
    row=metrics.grade(call,{},study.task(call)["public_order"],study.gold()[call["root_id"]])
    assert not row["available"] and not row["exact"]
