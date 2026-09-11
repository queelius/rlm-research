import json
from pathlib import Path

import id_owner_v3 as owner
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
    monkeypatch.setattr(owner, "verify_v2", lambda: {"identity": "cpu"})
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
    assert ledger["free"]["slot_taxonomy"] == {
        "native_final": 1,
        "attempted_no_native_final": 0,
        "attempted_failure_no_result": 1,
        "prepared_attempt_unknown": 0,
        "unstarted": 0,
    }
    assert ledger["free"]["physical_requests"] == 1


def test_cleanup_is_never_more_than_thirty_seconds():
    assert owner.cleanup_deadline(now=100, stage_end=900, owned=2000) == 130
    assert owner.cleanup_deadline(now=100, stage_end=120, owned=2000) == 120
    assert owner.cleanup_deadline(now=100, stage_end=900, owned=125) == 125


def test_cost_ledger_includes_probe_attempts_and_usage(tmp_path):
    probe = tmp_path / "sft6/probes/p"
    probe.mkdir(parents=True)
    study.write(probe / "RESULT.json", {
        "available": True, "physical_request_attempt": True, "response_returned": True,
        "usage": {"prompt_tokens": 7, "completion_tokens": 3,
                  "prompt_tokens_details": {"cached_tokens": 2}},
    })
    value = owner.ledger(tmp_path)
    assert value["probe"]["physical_requests"] == 1
    assert value["probe"]["native_final_endpoints"] == 1
    assert value["probe"]["usage"]["known"] == {"input": 7, "output": 3, "cached": 2}
    free = tmp_path / "sft12/free/f/physical"
    free.mkdir(parents=True)
    study.write(free / "000.json", {"physical_request_attempt": True,
                "response": {"choices": [{}], "usage": {"prompt_tokens": 11,
                             "completion_tokens": 5,
                             "prompt_tokens_details": {"cached_tokens": 9}}}})
    value = owner.ledger(tmp_path)
    assert value["free"]["returned_completions"] == 1
    assert value["free"]["usage"]["known"] == {"input": 11, "output": 5, "cached": 9}


def test_probe_orphan_response_proves_attempt_but_request_only_does_not(tmp_path):
    response_only = tmp_path / "sft18/probes/response"
    response_only.mkdir(parents=True)
    study.write(response_only / "REQUEST.json", {"body": {}})
    study.write(response_only / "RESPONSE.json", {"status": 200, "body": json.dumps({
        "choices": [{"token_ids": [1]}],
        "usage": {"prompt_tokens": 13, "completion_tokens": 2,
                  "prompt_tokens_details": {"cached_tokens": 10}},
    })})
    request_only = tmp_path / "sft18/probes/prepared"
    request_only.mkdir(parents=True)
    study.write(request_only / "REQUEST.json", {"body": {}})
    value = owner.ledger(tmp_path)["probe"]
    assert value["response_proven_attempts"] == 1
    assert value["http_responses"] == 1
    assert value["returned_choice_payloads"] == 1
    assert value["native_final_endpoints"] == 0
    assert value["prepared_attempt_unknown"] == 1
    assert value["usage"]["known"] == {"input": 13, "output": 2, "cached": 10}
