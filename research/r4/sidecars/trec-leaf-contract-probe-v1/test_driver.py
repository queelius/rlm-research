"""Focused CPU checks: pairing, no label leakage, strict scoring, cost and checkpoint safety."""

import asyncio
import importlib.util
import json
from pathlib import Path

import pytest


def driver():
    path = Path(__file__).with_name("driver.py")
    assert path.is_file(), "leaf driver implementation missing"
    spec = importlib.util.spec_from_file_location("leaf_probe_driver", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_plan_covers_each_training_record_once_per_arm_without_gold_in_requests():
    d = driver()
    design = d.make_design()
    assert len(design["batches"]) == 18
    assert len(design["plan"]) == 72
    assert design["batches"][-1]["record_indices"] == [86, 87, 88, 89]
    for arm in ["baseline", "definitions", "schema", "both"]:
        rows = [r for r in design["plan"] if r["arm"] == arm]
        covered = [i for r in rows for i in design["batches"][r["batch_id"]]["record_indices"]]
        assert covered == list(range(1, 90))
    for row in design["plan"]:
        body = d.make_request(design, row, "assigned-model")
        assert body["max_tokens"] == 256 and body["temperature"] == 0.5
        assert "gold_label" not in json.dumps(body)
        assert "answer" not in body


def test_schema_changes_decoding_not_messages_and_requires_last_batch_length_four():
    d = driver()
    design = d.make_design()
    rows = {r["arm"]: r for r in design["plan"] if r["batch_id"] == 17}
    bodies = {arm: d.make_request(design, row, "assigned-model") for arm, row in rows.items()}
    assert bodies["schema"]["messages"] == bodies["baseline"]["messages"]
    assert bodies["both"]["messages"] == bodies["definitions"]["messages"]
    assert bodies["both"]["messages"] != bodies["schema"]["messages"]
    schema = bodies["schema"].pop("structured_outputs")["json"]
    assert bodies["schema"] == bodies["baseline"]
    assert schema["minItems"] == schema["maxItems"] == 4
    assert len(schema["items"]["enum"]) == 6
    assert "tool_choice" not in bodies["baseline"]
    assert bodies["baseline"]["return_token_ids"] is True
    assert "logprobs" not in bodies["baseline"]


def test_noncanonical_label_is_not_silently_collapsed():
    d = driver()
    result = d.score_labels(
        '["description", "entity"]', ["description and abstract concept", "entity"]
    )
    assert result["strict_correct"] == 1
    assert result["schema_valid"] is False
    assert result["noncanonical_labels"] == 1
    assert result["predictions"] == ["description", "entity"]


def test_wrong_cardinality_does_not_impute_positionwise_accuracy():
    d = driver()
    result = d.score_labels('["entity"]', ["entity", "location"])
    assert result["strict_correct"] == 0
    assert result["predictions"] == [None, None]
    assert result["parse_status"] == "length_mismatch"
    malformed = d.score_labels('```json\n["entity"]\n```', ["entity"])
    assert malformed["parse_status"] == "invalid_json"


def test_vllm_prompt_usage_includes_cached_tokens():
    d = driver()
    result = d.usage_metrics(
        {
            "prompt_tokens": 20,
            "completion_tokens": 3,
            "prompt_tokens_details": {"cached_tokens": 12},
        }
    )
    assert result["logical_input_tokens"] == 20
    assert result["cached_input_tokens"] == 12
    assert result["uncached_input_tokens"] == 8
    assert result["completion_tokens"] == 3


def test_checkpoint_refuses_to_overwrite_material(tmp_path):
    d = driver()
    target = tmp_path / "record.json"
    d.write_once(target, {"first": 1})
    with pytest.raises(FileExistsError):
        d.write_once(target, {"second": 2})
    assert json.loads(target.read_text()) == {"first": 1}


def test_bound_weights_cannot_silently_switch_to_a_different_base_model():
    d = driver()
    descriptor = json.loads(
        Path(
            "/project/alex_phd/runs/rlm-research-r4/operations/2026-09-08-resume/"
            "frozen-replay-planned/endpoint.json"
        ).read_text()
    )
    descriptor["base_model"]["revision"] = "different-base-revision"
    with pytest.raises(ValueError, match="4B base"):
        d.verify_weights(descriptor)


def test_http_error_is_checkpointed_without_scoring_or_retrying(tmp_path, monkeypatch):
    d = driver()
    descriptor_path = Path(
        "/project/alex_phd/runs/rlm-research-r4/operations/2026-09-08-resume/"
        "frozen-replay-planned/endpoint.json"
    )
    spec = d.bind_spec(descriptor_path)
    descriptor = spec["endpoint_descriptor"]
    spec_path = tmp_path / "SPEC.json"
    d.write_once(spec_path, spec)
    monkeypatch.setenv(descriptor["api_key_env"], "test-only-not-an-api-key")
    requests = []

    def transport(request):
        if request.method == "GET":
            if request.url.path == "/version":
                return d.httpx.Response(200, json={"version": "0.28.0"})
            return d.httpx.Response(200, json={"data": [{"id": descriptor["model_alias"]}]})
        requests.append(json.loads(request.content))
        return d.httpx.Response(500, json={"error": {"message": "synthetic failure"}})

    original = d.httpx.AsyncClient
    monkeypatch.setattr(
        d.httpx,
        "AsyncClient",
        lambda **kw: original(**kw, transport=d.httpx.MockTransport(transport)),
    )
    output = tmp_path / "attempt"
    asyncio.run(d.run(spec_path, output))
    status = json.loads((output / "STATUS.json").read_text())
    assert status["stop_reason"] == "request_error"
    assert 1 <= len(requests) <= 4
    assert len({json.dumps(r, sort_keys=True) for r in requests}) == len(requests)
    rows = [json.loads(p.read_text()) for p in (output / "calls").glob("*.json")]
    assert len(rows) == len(requests)
    assert all(r["score"] is None and r["http_status"] == 500 for r in rows)
    assert all(
        c["model_completed_calls"] == 0
        for c in json.loads((output / "analysis.json").read_text())["cells"]
    )
