"""Focused behavioral tests for permutations, paired metrics and native boundaries."""

import importlib
import json
from collections import Counter

import pytest


def test_inventory_preserves_neighbor_slots_and_reverses_only_original_companions():
    study = importlib.import_module("companion_study")
    rows = study.make_schedule()
    assert len(rows) == 64
    assert sum(len(row["ids"]) for row in rows) == 1024
    visits = Counter((row["arm"], identifier) for row in rows for identifier in row["ids"])
    assert len(visits) == 1024 and set(visits.values()) == {1}
    originals = {(row["dataset"], row["block"]): row for row in rows if row["arm"] == "original"}
    original_slots = {
        identifier: slot for row in originals.values() for slot, identifier in enumerate(row["ids"])
    }
    for row in rows:
        original = originals[(row["dataset"], row["block"])]
        if row["arm"] == "reverse":
            assert row["ids"] == original["ids"][::-1]
        if row["arm"].startswith("neighbor"):
            assert all(
                original_slots[identifier] == slot for slot, identifier in enumerate(row["ids"])
            )
        schema = json.loads(row["schema_ordered_json"])
        assert list(schema["properties"]) == row["ids"]
    for arm in ("neighbor_A", "neighbor_B"):
        selected = [row for row in rows if row["arm"] == arm]
        assert any(
            set(row["ids"]) != set(originals[(row["dataset"], row["block"])]["ids"])
            for row in selected
        )
    assert study.context_bound(rows, 8192)["all_requests_fit"]
    with pytest.raises(ValueError, match="context"):
        study.context_bound(rows, 1024)


def test_paired_predictions_and_missing_calls_use_same_id_not_group_index():
    metrics = importlib.import_module("companion_metrics")
    rows = [
        {
            "call_id": "a",
            "dataset": "toy",
            "arm": "original",
            "ids": ["x", "y"],
            "body": {"token_ids": [1]},
        },
        {
            "call_id": "b",
            "dataset": "toy",
            "arm": "reverse",
            "ids": ["y", "x"],
            "body": {"token_ids": [1]},
        },
        {
            "call_id": "c",
            "dataset": "toy",
            "arm": "neighbor_A",
            "ids": ["x", "y"],
            "body": {"token_ids": [1]},
        },
        {
            "call_id": "d",
            "dataset": "toy",
            "arm": "neighbor_B",
            "ids": ["x", "y"],
            "body": {"token_ids": [1]},
        },
    ]
    calls = [
        {
            **row,
            "status": "returned_valid",
            "prediction": prediction,
            "prompt_tokens": 1,
            "completion_tokens": 2,
            "wall_seconds": 1,
        }
        for row, prediction in zip(
            rows[:2], [{"x": "A", "y": "A"}, {"y": "B", "x": "A"}], strict=True
        )
    ]
    value = metrics.summarize(calls, rows, {"labels": {"x": "A", "y": "B"}})
    assert value["by_dataset_arm"]["toy:original"]["correct"] == 1
    assert value["by_dataset_arm"]["toy:reverse"]["correct"] == 2
    assert value["paired"]["toy:original_vs_reverse"]["challenger_wins"] == 1
    assert value["paired"]["toy:original_vs_reverse"]["prediction_disagreements"] == 1
    assert value["by_dataset_arm"]["toy:neighbor_A"]["unavailable"] == 2
    assert value["by_dataset_arm"]["toy:neighbor_A"]["status_counts"] == {"unattempted": 1}
    assert value["paired"]["toy:original_vs_neighbor_A"]["challenger_unavailable"] == 2
    assert not value["complete_available"]


def test_native_seam_and_real_full_label_decoder(monkeypatch):
    study = importlib.import_module("companion_study")
    from transformers import AutoTokenizer

    monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY", "cpu-fixture-not-a-provider-credential")
    assert study.dependencies().SERVE == study.SERVICE
    assert callable(study.wire_send())
    row = next(row for row in study.make_schedule() if row["arm"] == "neighbor_A")
    tokenizer = AutoTokenizer.from_pretrained(study.MODEL, local_files_only=True)
    prediction = dict.fromkeys(row["ids"], row["labels"][0])
    ids = tokenizer.encode(json.dumps(prediction), add_special_tokens=False)
    raw = {
        "request_id": "fixture",
        "model": study.CHILD_ALIAS,
        "choices": [{"token_ids": ids, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": len(row["body"]["token_ids"]), "completion_tokens": len(ids)},
    }
    assert study.response_record(row, raw, tokenizer)["prediction"] == prediction
    raw["choices"][0]["finish_reason"] = "length"
    assert study.response_record(row, raw, tokenizer)["status"] == "invalid_response"
