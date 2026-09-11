"""Bounded CPU tests for clean-group replication; never contacts a service."""

import asyncio
import importlib.util
import json
from copy import deepcopy
from pathlib import Path

import pytest


def driver():
    path = Path(__file__).with_name("driver.py")
    assert path.exists(), "validation replication implementation missing"
    spec = importlib.util.spec_from_file_location("leaf_validation_driver", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_plan_pairs_clean_source_groups_across_three_seeds_and_four_arms():
    d = driver()
    design = d.make_design()
    assert len(design["records"]) == 300
    groups = [r["question_group_sha256"] for r in design["records"]]
    assert groups == sorted(set(groups))
    assert len(design["batches"]) == 60
    assert len(design["plan"]) == len({r["id"] for r in design["plan"]}) == 720
    assert design["seeds"] == [980260100, 980260101, 980260102]
    assert design["provenance"]["source_test_file_read"] is False
    assert design["provenance"]["validation_intersects_prior_pool"] == 0
    for seed in (980260100, 980260101, 980260102):
        for arm in ("baseline", "definitions", "schema", "both"):
            rows = [r for r in design["plan"] if r["seed"] == seed and r["arm"] == arm]
            assert len(rows) == 60
            indices = [i for r in rows for i in design["batches"][r["batch_id"]]["record_indices"]]
            assert indices == list(range(1, 301))


def test_new_design_retains_exact_old_request_contract():
    d = driver()
    design = d.make_design()
    old = json.loads((d.OLD / "FROZEN_REPLAY_SPEC.json").read_text())
    probe = deepcopy(design)
    probe["batches"] = old["design"]["batches"]
    for row in old["design"]["plan"][:8]:
        body = d.make_request(probe, row, old["endpoint_descriptor"]["model_alias"])
        assert d.digest(body) == old["request_sha256"][row["id"]]
    for row in design["plan"][:4]:
        body = d.make_request(design, row, "assigned")
        assert "gold_label" not in json.dumps(body)
        assert body["temperature"] == 0.5 and body["max_tokens"] == 256


def test_dynamic_denominators_and_alias_sensitivity_preserve_observation_boundary():
    d = driver()
    design = {
        "seeds": [9],
        "records": [{"record_index": i} for i in range(1, 8)],
        "batches": [{"record_indices": [1, 2]}, {"record_indices": [3, 4, 5, 6, 7]}],
        "plan": [{"arm": a, "seed": 9, "batch_id": b} for b in range(2) for a in d.ARMS],
    }
    record = {
        "coordinate": {"arm": "baseline", "seed": 9, "batch_id": 0},
        "score": {"records": 2, "strict_correct": 1, "schema_valid": False},
        "record_results": [
            {
                "record_index": 1,
                "question_group_sha256": "g1",
                "gold_label": "entity",
                "prediction": "entity",
            },
            {
                "record_index": 2,
                "question_group_sha256": "g2",
                "gold_label": "description and abstract concept",
                "prediction": "description",
            },
        ],
        "usage": {"logical_input_tokens": 11, "completion_tokens": 3},
        "finish_reason": "stop",
    }
    cell = d.summarize(design, [record])["cells"][0]
    assert cell["planned_calls"] == 2 and cell["planned_record_labels"] == 7
    assert cell["observed_record_labels"] == 2
    assert cell["accuracy_per_model_completed_record"] == 0.5
    assert cell["correct_over_planned_record_labels"] == 1 / 7
    assert cell["alias_sensitivity_correct"] == 2
    assert cell["execution_errors"] == 0 and cell["unrecorded_calls"] == 1


def test_changed_partition_bytes_are_rejected(tmp_path, monkeypatch):
    d = driver()
    changed = tmp_path / "split.json"
    changed.write_text("{}")
    monkeypatch.setattr(d, "SPLIT", changed)
    with pytest.raises(ValueError, match="source hash"):
        d.make_design()


def test_non_original_adapter_is_rejected():
    d = driver()
    descriptor = json.loads(d.DEFAULT_ENDPOINT.read_text())
    descriptor["adapter"]["model_sha256"] = "different-adapter"
    with pytest.raises(ValueError, match="original step0"):
        d.verify_original_weights(descriptor)


def test_http_error_checkpoints_and_stops_without_retry(tmp_path, monkeypatch):
    d = driver()
    spec = d.bind_spec(d.DEFAULT_ENDPOINT)
    spec_path = tmp_path / "SPEC.json"
    d.write_once(spec_path, spec)
    descriptor = spec["endpoint_descriptor"]
    monkeypatch.setenv(descriptor["api_key_env"], "synthetic-test-key")
    original = d.httpx.AsyncClient

    def transport(request):
        if request.url.path == "/version":
            return d.httpx.Response(200, json={"version": "0.28.0"})
        if request.url.path == "/v1/models":
            return d.httpx.Response(200, json={"data": [{"id": descriptor["model_alias"]}]})
        return d.httpx.Response(500, json={"error": {"message": "bounded synthetic failure"}})

    monkeypatch.setattr(
        d.httpx,
        "AsyncClient",
        lambda **kw: original(**kw, transport=d.httpx.MockTransport(transport)),
    )
    output = tmp_path / "attempt"
    asyncio.run(d.run(spec_path, output))
    status = json.loads((output / "STATUS.json").read_text())
    assert status["planned"] == 720 and 1 <= status["recorded"] <= 4
    assert status["stop_reason"] == "request_error"
    rows = [json.loads(p.read_text()) for p in (output / "calls").glob("*.json")]
    assert len(rows) == status["recorded"]
    assert len({r["coordinate"]["id"] for r in rows}) == len(rows)
    assert all(r["score"] is None and r["http_status"] == 500 for r in rows)
    assert all(len(r["source_groups"]) == 5 for r in rows)
    assert all(r["model_identity"]["adapter_sha256"] == d.STEP0_SHA for r in rows)
