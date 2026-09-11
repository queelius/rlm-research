import json
from pathlib import Path

import id_owner as owner
import id_study as study


def test_execute_attempts_all_four_fixed_stages_after_ordinary_failure(tmp_path, monkeypatch):
    calls = []

    class Suite:
        def start_service(self, stage, binding, deadline):
            calls.append(("start", stage.name, binding["operator_dose_intermediate"]["policy"]))
            (stage / "service").mkdir()
            study.write(stage / "BINDING.json", binding)
            study.write(stage / "service/endpoint-original.json", {"cpu": True})
            if stage.name == "service-sft18":
                raise RuntimeError("ordinary startup failure")

        def command(self, stage, label, argv, cap, deadline):
            calls.append((label, stage.name, cap))

        def release_service(self, stage):
            calls.append(("release", stage.name))

    monkeypatch.setattr(study, "ATTEMPT", tmp_path / "attempt")
    monkeypatch.setattr(study, "verify", lambda: {"identity": "cpu"})
    monkeypatch.setattr(study, "runtime", lambda: None)
    monkeypatch.setattr(owner, "dependencies", lambda: Suite())
    monkeypatch.setattr(owner, "training_receipt", lambda: {"cpu": True})
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "CPU_INTERCEPT_ONLY")
    result = owner.execute(study.ATTEMPT)
    assert [entry[1] for entry in calls if entry[0] == "start"] == [
        "service-sft18", "service-sft24", "service-sft12", "service-sft6"
    ]
    assert result["released"] and len(result["stages"]) == 4
    assert len(result["readout_inventory"]) == 64
    assert len(result["first_action_inventory"]) == 48
    assert all(item["taxonomy"] == "unstarted" for item in result["readout_inventory"])


def test_ledger_counts_attempted_failures_separately_from_unstarted(tmp_path):
    attempted = tmp_path / "sft6/free/a"
    attempted.mkdir(parents=True)
    study.write(attempted / "FAILURE.json", {"error": "HTTP400"})
    physical = attempted / "physical"
    physical.mkdir()
    study.write(physical / "000.json", {"physical_request_attempt": True, "usage": None})
    native = tmp_path / "sft6/free/b"
    native.mkdir(parents=True)
    study.write(native / "RESULT.json", {"available": True})
    ledger = owner.ledger(tmp_path)
    assert ledger["slot_taxonomy"] == {
        "native_final": 1,
        "attempted_no_native_final": 0,
        "attempted_failure_no_result": 1,
        "unstarted": 0,
    }
    assert ledger["physical_requests"] == 1
