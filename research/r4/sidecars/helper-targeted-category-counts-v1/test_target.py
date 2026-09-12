"""Focused contracts: matched gold, reuse, context, and actual native schemas."""

import importlib
import json
from collections import Counter

import pytest


def module(name):
    return importlib.import_module(name)


def fixture():
    ids = ["a", "b", "c", "d"]
    rows = [
        {
            "call_id": arm,
            "dataset": "toy",
            "block": 0,
            "ids": ids,
            "arm": "full" if arm == "full" else "targeted",
            "target": None if arm == "full" else arm,
            "labels": ["A", "B"],
            "body": {"token_ids": [1] * 10},
        }
        for arm in ("full", "A", "B")
    ]
    predictions = {
        "full": dict(zip(ids, ["A", "B", "B", "B"], strict=True)),
        "A": dict(zip(ids, ["A", "A", "other", "other"], strict=True)),
        "B": dict(zip(ids, ["other", "other", "B", "B"], strict=True)),
    }
    calls = [
        {
            **row,
            "prediction": predictions[row["call_id"]],
            "status": "returned_valid",
            "prompt_tokens": 10,
            "completion_tokens": 2,
            "cached_prompt_tokens": 0,
            "wall_seconds": 1.0,
        }
        for row in rows
    ]
    return rows, calls, {"labels": dict(zip(ids, ["A", "A", "B", "B"], strict=True))}


def test_same_gold_matched_counts_and_reusable_cost():
    rows, calls, gold = fixture()
    value = module("metrics").summarize(calls, rows, gold)
    dataset = value["datasets"]["toy"]
    assert dataset["full"]["exact_count_tasks"] == 0
    assert dataset["full"]["sum_absolute_count_error"] == 2
    assert dataset["targeted"]["exact_count_tasks"] == 2
    assert dataset["targeted"]["sum_absolute_count_error"] == 0
    assert dataset["full"]["macro_balanced_accuracy"] == 0.75
    assert dataset["targeted"]["macro_balanced_accuracy"] == 1.0
    assert value["per_target"]["toy:A:full"]["FN"] == 1
    assert value["physical"]["toy:full"]["attempted_calls"] == 1
    assert value["cost_views"]["toy"]["single_uniform_target"]["full_total_tokens"] == 12
    assert value["cost_views"]["toy"]["single_uniform_target"]["targeted_total_tokens"] == 12
    assert value["cost_views"]["toy"]["all_targets"]["full_total_tokens"] == 12
    assert value["cost_views"]["toy"]["all_targets"]["targeted_total_tokens"] == 24


def test_missing_full_map_fans_out_without_multiplying_physical_failure():
    rows, calls, gold = fixture()
    calls[0].update(status="request_error", prediction={})
    calls[0].pop("prompt_tokens")
    calls[0].pop("completion_tokens")
    value = module("metrics").summarize(calls, rows, gold)
    assert value["datasets"]["toy"]["full"]["unavailable_count_tasks"] == 2
    assert value["datasets"]["toy"]["full"]["unavailable_decisions"] == 8
    assert value["physical"]["toy:full"]["status_counts"] == {"request_error": 1}
    assert value["physical"]["toy:full"]["usage_unknown_calls"] == 1
    assert value["per_target"]["toy:A:full"]["missing_positive"] == 2
    assert value["per_target"]["toy:A:full"]["recall_bounds"] == [0, 1]
    assert value["datasets"]["toy"]["full"]["macro_balanced_accuracy"] is None
    assert value["cost_views"]["toy"]["single_uniform_target"]["token_ratio"] is None


def test_frozen_inventory_binary_complement_and_context(monkeypatch):
    study = module("target_study")
    rows = study.make_schedule()
    assert len(rows) == 96
    assert Counter(row["arm"] for row in rows) == {"full": 16, "targeted": 80}
    assert sum(len(row["ids"]) for row in rows) == 1536
    assert len({identifier for row in rows for identifier in row["ids"]}) == 256
    for row in rows:
        schema = json.loads(row["schema_ordered_json"])
        assert list(schema["properties"]) == row["ids"]
        allowed = row["labels"] if row["arm"] == "full" else [row["target"], "other"]
        assert schema["properties"][row["ids"][0]]["enum"] == allowed
        if row["arm"] == "targeted":
            assert "not an additional semantic category" in row["request_text"]
    bound = study.context_bound(rows, 8192)
    assert bound["maximum_prompt_plus_output_tokens"] <= 8192
    with pytest.raises(ValueError, match="context"):
        study.context_bound(rows, 1024)
    # The loader requires a credential before returning, but this CPU test never starts a service.
    monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY", "cpu-fixture-not-a-provider-credential")
    assert study.dependencies().SERVE == study.SERVICE


def test_response_validates_binary_other_without_accepting_extra_ids():
    study = module("target_study")
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(study.MODEL, local_files_only=True)
    row = next(row for row in study.make_schedule() if row["arm"] == "targeted")
    prediction = dict.fromkeys(row["ids"], "other")
    token_ids = tokenizer.encode(json.dumps(prediction), add_special_tokens=False)
    raw = {
        "model": study.CHILD_ALIAS,
        "request_id": "toy-unique",
        "choices": [{"token_ids": token_ids, "finish_reason": "stop"}],
        "usage": {
            "prompt_tokens": len(row["body"]["token_ids"]),
            "completion_tokens": len(token_ids),
        },
    }
    assert study.response_record(row, raw, tokenizer)["status"] == "returned_valid"
    raw["choices"][0]["finish_reason"] = "length"
    assert study.response_record(row, raw, tokenizer)["status"] == "invalid_response"
    raw["choices"][0]["token_ids"] = tokenizer.encode(
        json.dumps(list(prediction.items())), add_special_tokens=False
    )
    raw["usage"]["completion_tokens"] = len(raw["choices"][0]["token_ids"])
    raw["choices"][0]["finish_reason"] = "stop"
    assert study.response_record(row, raw, tokenizer)["status"] == "invalid_response"
    raw["choices"][0]["finish_reason"] = "stop"
    raw["choices"][0]["token_ids"] = tokenizer.encode(
        json.dumps({**prediction, "extra": "other"}), add_special_tokens=False
    )
    raw["usage"]["completion_tokens"] = len(raw["choices"][0]["token_ids"])
    assert study.response_record(row, raw, tokenizer)["status"] == "invalid_response"
