"""Focused preservation, explicit scoring, missing-map and native-label contracts."""

import importlib
import json
from collections import Counter

import pytest


def test_frozen56_preserves_full_bodies_definitions_and_records():
    study = importlib.import_module("yesno_study")
    old = {row["call_id"]: row for row in study.target.schedule()}
    rows = study.make_schedule()
    assert len(rows) == 56
    assert Counter(row["arm"] for row in rows) == {"full": 8, "targeted": 48}
    assert sum(len(row["ids"]) for row in rows) == 896
    for row in rows:
        source = old[row["source_call_id"]]
        assert row["ids"] == source["ids"]
        if row["arm"] == "full":
            assert row["body"] == source["body"]
            assert row["request_text"] == source["request_text"]
        else:
            assert (
                row["request_text"].split("\nTarget category:")[0]
                == source["request_text"].split("\nTarget category:")[0]
            )
            assert (
                row["request_text"].split("\nQuestions: ")[1]
                == source["request_text"].split("\nQuestions: ")[1]
            )
            schema = json.loads(row["schema_ordered_json"])
            assert list(schema["properties"]) == row["ids"]
            assert all(value["enum"] == ["yes", "no"] for value in schema["properties"].values())
    assert study.context_bound(rows, 8192)["all_requests_fit"]
    with pytest.raises(ValueError, match="context"):
        study.context_bound(rows, 1024)


def test_yesno_mapping_scores_same_gold_and_retains_collapse_missing_and_reuse():
    metrics = importlib.import_module("yesno_metrics")
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
            "body": {"token_ids": [1]},
        }
        for arm in ("full", "A", "B")
    ]
    predictions = [
        {"a": "A", "b": "B", "c": "B", "d": "B"},
        {"a": "yes", "b": "yes", "c": "no", "d": "no"},
        dict.fromkeys(ids, "yes"),
    ]
    calls = [
        {
            **row,
            "prediction": prediction,
            "status": "returned_valid",
            "prompt_tokens": 10,
            "completion_tokens": 2,
            "wall_seconds": 1,
        }
        for row, prediction in zip(rows, predictions, strict=True)
    ]
    gold = {"labels": {"a": "A", "b": "A", "c": "B", "d": "B"}}
    value = metrics.summarize(calls, rows, gold)
    assert value["per_target"]["toy:A:targeted"]["TP"] == 2
    assert value["per_target"]["toy:A:targeted"]["FP"] == 0
    assert value["binary_behavior"]["toy:B"]["all_yes_maps"] == 1
    assert value["binary_behavior"]["toy:B"]["predicted_positive"] == 4
    assert value["cost_views"]["toy"]["all_targets"]["full_total_tokens"] == 12
    assert calls[1]["prediction"]["a"] == "yes"
    calls[0].update(status="request_error", prediction={})
    value = metrics.summarize(calls, rows, gold)
    assert value["datasets"]["toy"]["full"]["unavailable_count_tasks"] == 2
    assert not value["datasets"]["toy"]["prospective_screen"]["passes"]


def test_real_decoder_accepts_yes_no_but_not_literal_or_other(monkeypatch):
    study = importlib.import_module("yesno_study")
    from transformers import AutoTokenizer

    monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY", "cpu-fixture-not-a-provider-credential")
    assert study.dependencies().SERVE == study.SERVICE
    assert callable(study.wire_send())
    row = next(row for row in study.make_schedule() if row["arm"] == "targeted")
    tokenizer = AutoTokenizer.from_pretrained(study.MODEL, local_files_only=True)

    def response(label):
        ids = tokenizer.encode(
            json.dumps(dict.fromkeys(row["ids"], label)), add_special_tokens=False
        )
        return {
            "request_id": "fixture",
            "model": study.CHILD_ALIAS,
            "choices": [{"token_ids": ids, "finish_reason": "stop"}],
            "usage": {
                "prompt_tokens": len(row["body"]["token_ids"]),
                "completion_tokens": len(ids),
            },
        }

    assert study.response_record(row, response("yes"), tokenizer)["status"] == "returned_valid"
    assert study.response_record(row, response("no"), tokenizer)["status"] == "returned_valid"
    assert study.response_record(row, response("other"), tokenizer)["status"] == "invalid_response"
    assert (
        study.response_record(row, response(row["target"]), tokenizer)["status"]
        == "invalid_response"
    )
