import json
from pathlib import Path

import warm_owner as owner
import warm_prepare as prepare
import warm_study as study


def test_shared_clock_and_cleanup_are_hard_bounded():
    value = owner.budget(100)
    assert value == {"started": 100, "training_end": 5500, "work": 10600,
                     "owned": 10780, "outer": 10900, "final_total": 5100}
    assert owner.cleanup_deadline(200, 900, 2000) == 230
    assert owner.cleanup_deadline(200, 215, 2000) == 215
    assert not owner.learning_window_allowed(1000, now=0)
    assert owner.learning_window_allowed(1320, now=0)


def test_planned_inventory_keeps_all_192_and_96_nulls(tmp_path, monkeypatch):
    plans = prepare.build_inputs()["PLANS.json"]
    monkeypatch.setattr(study, "read", lambda path: plans if Path(path).name == "PLANS.json" else None)
    rows = owner.planned_inventory(tmp_path)
    assert len(rows) == 288
    assert sum(row["phase"] == "training" for row in rows) == 192
    assert sum(row["phase"] == "readout" for row in rows) == 96
    assert all(row["available"] is False and row["reward"] is None for row in rows)


def test_disk_union_separates_response_final_and_prepared_unknown(tmp_path):
    response = tmp_path / "readout-trained/rollout/rows/a"
    response.mkdir(parents=True)
    study.write(response / "REQUEST.json", {"body": {}})
    study.write(response / "RESPONSE.json", {"status": 400, "body": "bad"})
    prepared = tmp_path / "readout-trained/rollout/rows/b"
    prepared.mkdir(parents=True)
    study.write(prepared / "REQUEST.json", {"body": {}})
    physical = tmp_path / "window-01/collection/rollout/episodes/c/physical"
    physical.mkdir(parents=True)
    study.write(physical / "0001.json", {"physical_request_attempt": True, "status": 200,
                "response": {"choices": [{}], "usage": {"prompt_tokens": 4,
                             "completion_tokens": 2}}})
    value = owner.cost_ledger(tmp_path)
    assert value["raw_http_responses"] == 1
    assert value["prepared_attempt_unknown"] == 1
    assert value["physical_records"] == 1
    assert value["raw_success_choice_payloads"] == 1
    assert value["billing"] == "not measured"


def test_recovered_commit_consumes_window_once(tmp_path, monkeypatch):
    old = {"step": 2, "adapter_sha256": "old"}
    new = {"step": 3, "adapter_sha256": "new"}
    state = {"policy": old, "completed_windows": 2}
    generation = {"candidate_window": 3, "round": 3, "previous_policy": old}
    checkpoint = tmp_path / "training/checkpoint-3/state.json"
    checkpoint.parent.mkdir(parents=True)
    checkpoint.write_text("{}")
    monkeypatch.setattr(owner.common.c, "checkpoint_policy", lambda *_: new)
    owner.recover_commit_on_stop(tmp_path, generation, state)
    assert state == {"policy": new, "completed_windows": 3}
    receipt = study.read(tmp_path / "COMMIT_RECOVERED_ON_STOP.json")
    assert receipt["no_second_update"] is True
    assert receipt["completed_windows"] == 3
