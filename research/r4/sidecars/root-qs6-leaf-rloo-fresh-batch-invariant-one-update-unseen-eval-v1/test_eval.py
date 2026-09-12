import copy
import inspect
from pathlib import Path

import pytest

import one_update_panel_study as study
import owner


def fixture_binding(checkpoint=Path("/tmp/checkpoint-0001")):
    value=copy.deepcopy(study.read(study.SOURCE_BINDING));alias=study.CHILD_ALIAS
    value["models"][alias]={"path":str(checkpoint),"adapter_sha256":"a","config_sha256":"c"}
    value["child_only_update"]={"step":1,"root_unchanged":True}
    return value


def test_exact_frozen_schedule_and_zero_argument_interfaces():
    rows=study.schedule();assert rows==study.source().schedule();assert len(rows)==64
    assert len({identifier for row in rows for identifier in row["ids"]})==256
    for row in rows:
        schema=row["body"]["sampling_params"]["structured_outputs"]["json"]
        assert row["body"]["sampling_params"]["temperature"]==0
        assert list(schema["properties"])==row["ids"]==schema["required"]
    assert len(inspect.signature(study.binding).parameters)==0
    assert len(inspect.signature(study.verify).parameters)==0
    assert len(inspect.signature(study.dependencies).parameters)==0


def test_actual_collector_build_uses_facade_and_binding(monkeypatch,tmp_path):
    expected=fixture_binding(tmp_path/"checkpoint-0001")
    monkeypatch.setattr(study,"qualify_one_update",lambda:{"binding":expected})
    monkeypatch.setattr(study,"ATTEMPT",tmp_path/"not-created")
    assert study.binding()==expected
    collector=owner.build_collector()
    assert collector.study is study and collector.study.binding()==expected
    assert collector.study.dependencies is study.dependencies
    pin=tmp_path/"pin";pin.write_text("fixed")
    ready={"status":"CPU_READY_CONDITIONAL_ON_UPDATED_STEP1",
        "closure_sha256":{str(pin):study.sha(pin)},"schedule_sha256":study.digest(study.schedule()),
        "identity":"fixture"}
    (tmp_path/"READY.json").write_text(__import__("json").dumps(ready))
    monkeypatch.setattr(study,"ROOT",tmp_path)
    assert study.verify()["identity"]=="fixture"


def test_qualifier_rejects_no_update_and_incomplete_replay(monkeypatch,tmp_path):
    checkpoint=tmp_path/"checkpoint-0001";checkpoint.mkdir(parents=True)
    result={"status":"NO_UPDATE_GRADIENT_REPLAY_FAILED","optimizer_steps":0,"checkpoint":str(checkpoint)}
    (tmp_path/"RESULT.json").write_text(__import__("json").dumps(result))
    monkeypatch.setattr(study,"TRAIN_OUTPUT",tmp_path)
    # Training READY is verified before RESULT, so provide the actual sealed READY unchanged.
    with pytest.raises(ValueError,match="UPDATED checkpoint-0001"):
        study.qualify_one_update(tmp_path)
