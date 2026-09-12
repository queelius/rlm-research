"""Catch stale64/256 denominators and negative/missing-dominated accounting."""

import copy
import json

import metrics


def test_actual_frozen512_schema_native_decode_and_fixed_denominators():
    import study

    schedule = study.schedule()
    gold = study.gold()
    assert len(schedule) == 128 and len(gold["labels"]) == 512
    calls = []
    for row in schedule:
        calls.append(
            {
                "call_id": row["call_id"],
                "ids": row["ids"],
                "status": "returned_valid",
                "prediction": {key: gold["labels"][key] for key in row["ids"]},
                "prompt_tokens": 100,
                "completion_tokens": 20,
                "cached_prompt_tokens": 0,
                "wall_seconds": 1.0,
                "request_id": row["call_id"],
            }
        )
    baseline = metrics.summarize(calls, gold, schedule)
    assert baseline["complete"] and baseline["metrics"]["correct"] == 512
    assert baseline["inventory"]["expected_calls"] == 128
    assert {row["correct"] for row in baseline["per_class"].values()} == {128}
    changed = copy.deepcopy(calls)
    identifier = changed[0]["ids"][0]
    old_label = gold["labels"][identifier]
    changed[0]["prediction"][identifier] = next(
        label for label in metrics.LABELS if label != old_label
    )
    updated = metrics.summarize(changed, gold, schedule)
    assert (
        updated["metrics"]["correct"] == 511 and updated["metrics"]["primary_accuracy"] == 511 / 512
    )
    assert updated["per_class"][old_label]["correct"] == 127
    paired = metrics.paired(baseline, updated, gold, schedule)
    assert paired["wins"] == 0 and paired["losses"] == 1 and paired["paired_available"] == 512
    assert paired["clusters"] == 128 and paired["net_correct_change"] == -1
    incomplete = metrics.summarize(changed[:-1], gold, schedule)
    assert not incomplete["complete"] and incomplete["metrics"]["primary_accuracy"] is None
    assert incomplete["inventory"]["unattempted_calls"] == 1
    assert incomplete["metrics"]["unavailable_predictions"] == 4
    assert incomplete["metrics"]["correct"] == 507
    error = {
        "call_id": schedule[-1]["call_id"],
        "ids": schedule[-1]["ids"],
        "status": "request_error",
    }
    failed = metrics.summarize(changed[:-1] + [error], gold, schedule)
    assert failed["cost"]["unknown_usage_calls"]["prompt_tokens"] == 1
    assert failed["cost"]["prompt_tokens_observed_subtotal"] == 12700
    assert failed["inventory"]["unattempted_calls"] == 0
    from transformers import AutoTokenizer

    import collect

    tokenizer = AutoTokenizer.from_pretrained(study.MODEL, local_files_only=True)
    row = schedule[0]
    prediction = changed[0]["prediction"]
    tokens = tokenizer.encode(
        json.dumps(prediction, separators=(",", ":")), add_special_tokens=False
    ) + [151645]
    response = {
        "model": study.CHILD_ALIAS,
        "request_id": "fresh512-fixture",
        "choices": [{"token_ids": tokens, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": len(row["body"]["token_ids"]), "completion_tokens": len(tokens)},
    }
    decoded = collect.decode(row, response, tokenizer, 1, 2)
    assert decoded["status"] == "returned_valid" and decoded["prediction"] == prediction
    assert decoded["completion_ids"] == tokens
    assert list(json.loads(row["schema_ordered_json"])["properties"]) == row["ids"]
