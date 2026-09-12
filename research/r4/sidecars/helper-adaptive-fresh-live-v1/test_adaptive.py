"""Two bounded fixtures: catch routing leakage/cost duplication and request mispartitioning."""

import importlib
import json
from collections import Counter

import pytest


def test_live_commit_precedes_future_outputs_and_costs_count_physical_calls_once():
    m = importlib.import_module("adaptive_metrics")
    public = [{"id": i, "dataset": "toy"} for i in ("x", "y", "z")]
    rows = [
        {
            "call_id": arm,
            "arm": arm,
            "dataset": "toy",
            "ids": ["x", "y", "z"],
            "body": {"token_ids": [1] * 10},
        }
        for arm in ("original", "neighbor_A", "neighbor_B")
    ] + [
        {
            "call_id": i,
            "arm": "singleton",
            "dataset": "toy",
            "ids": [i],
            "body": {"token_ids": [1] * 3},
        }
        for i in ("x", "y", "z")
    ]
    answers = {
        "original": {"x": "A", "y": "A", "z": "A"},
        "neighbor_A": {"x": "A", "y": "B", "z": "B"},
        "neighbor_B": {"x": "A", "y": "B", "z": "C"},
        "x": {"x": "A"},
        "y": {"y": "B"},
        "z": {"z": "C"},
    }
    events = []

    def send(row):
        events.append(row["call_id"])
        return {
            **row,
            "status": "returned_valid",
            "prediction": answers[row["call_id"]],
            "prompt_tokens": len(row["body"]["token_ids"]),
            "completion_tokens": 2,
            "cached_prompt_tokens": 0,
            "wall_seconds": 1,
        }

    def commit(routing, calls):
        assert events == ["original", "neighbor_A"]
        assert routing["selected_ids"] == ["y", "z"]
        assert len(calls) == 2
        events.append("COMMIT")

    calls, routing = m.collect(rows, public, send, commit)
    assert events == ["original", "neighbor_A", "COMMIT", "y", "z", "neighbor_B", "x"]
    result = m.summarize(calls, rows, public, {"x": "A", "y": "B", "z": "C"}, routing)
    policy = result["datasets"]["toy"]["policies"]
    assert [policy[key]["correct"] for key in m.POLICIES] == [1, 2, 3, 3]
    assert policy["three_vote"]["prediction_by_id"]["z"] == "A"
    assert result["physical_cost"]["observed_total_tokens"] == 51
    assert [policy[key]["cost"]["observed_total_tokens"] for key in m.POLICIES] == [12, 36, 34, 15]
    assert result["datasets"]["toy"]["screen"]["metric_passes"]
    # A missing full map fans out to all its records, not singleton rescue or free cost.
    broken = [
        {**call, "status": "request_error", "prediction": {}}
        if call["call_id"] == "neighbor_A"
        else call
        for call in calls
    ]
    broken[1].pop("prompt_tokens")
    broken[1].pop("completion_tokens")
    missing_route = m.route(broken[:2], public)
    assert missing_route["selected_ids"] == [] and len(missing_route["unavailable_ids"]) == 3
    missing = m.summarize(broken, rows, public, {"x": "A", "y": "B", "z": "C"}, missing_route)
    assert missing["datasets"]["toy"]["policies"]["selective_singleton"]["unavailable"] == 3
    assert missing["physical_cost"]["usage_unknown_calls"] == 1
    assert not missing["datasets"]["toy"]["screen"]["metric_passes"]


def test_frozen_partitions_schema_context_and_actual_native_token_decoder(monkeypatch):
    s = importlib.import_module("adaptive_study")
    rows = s.make_schedule()
    assert len(rows) == 152 and sum(len(r["ids"]) for r in rows) == 512
    visits = Counter((r["arm"], i) for r in rows for i in r["ids"])
    assert len(visits) == 512 and set(visits.values()) == {1}
    original_slots = {i: j for r in rows if r["arm"] == "original" for j, i in enumerate(r["ids"])}
    for row in rows:
        assert row["body"]["sampling_params"]["temperature"] == 0
        assert row["body"]["sampling_params"]["max_tokens"] == 1024
        assert row["body"]["sampling_params"]["seed"] == 202609121210 + (
            row["dataset"] == "ag_news"
        )
        if row["arm"].startswith("neighbor"):
            assert all(original_slots[i] == j for j, i in enumerate(row["ids"]))
        schema = json.loads(row["schema_ordered_json"])
        assert list(schema["properties"]) == schema["required"] == row["ids"]
        assert all(value["enum"] == row["labels"] for value in schema["properties"].values())
    assert s.context_bound(rows, 8192)["all_requests_fit"]
    with pytest.raises(ValueError, match="context"):
        s.context_bound(rows, 1024)
    monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY", "cpu-fixture-not-a-provider-credential")
    assert s.dependencies().SERVE == s.SERVICE and callable(s.wire_send())
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained(s.MODEL, local_files_only=True)
    row = rows[0]
    pred = dict.fromkeys(row["ids"], row["labels"][0])
    ids = tok.encode(json.dumps(pred), add_special_tokens=False)
    raw = {
        "request_id": "fixture",
        "model": s.CHILD_ALIAS,
        "choices": [{"token_ids": ids, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": len(row["body"]["token_ids"]), "completion_tokens": len(ids)},
    }
    assert s.response_record(row, raw, tok)["prediction"] == pred
    raw["choices"][0]["finish_reason"] = "length"
    assert s.response_record(row, raw, tok)["status"] == "invalid_response"
