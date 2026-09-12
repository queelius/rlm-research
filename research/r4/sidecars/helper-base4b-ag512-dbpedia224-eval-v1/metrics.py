"""Per-panel exact inventory and paired comparison utilities for the base control."""

from collections import Counter

import study


EXPECTED = {"ag_news": (128, 512), "dbpedia14": (56, 224)}


def summarize_panel(panel, calls, labels, schedule):
    expected_calls_count, expected_ids_count = EXPECTED[panel]
    expected_ids = [key for row in schedule for key in row["ids"]]
    if (
        len(schedule) != expected_calls_count
        or len(expected_ids) != expected_ids_count
        or set(expected_ids) != set(labels)
    ):
        raise ValueError("fixed panel/gold inventory differs")
    expected_calls = {row["call_id"]: row for row in schedule}
    attempted, duplicate_ids, predictions = [], [], {}
    fields = ("prompt_tokens", "completion_tokens", "cached_prompt_tokens")
    costs = {field + "_observed_subtotal": 0 for field in fields}
    unknown = {field: 0 for field in fields}
    per_class = {
        label: {
            "planned": sum(value == label for value in labels.values()),
            "available": 0,
            "correct": 0,
            "confusion": {other: 0 for other in study.LABELS[panel]},
        }
        for label in study.LABELS[panel]
    }
    for call in calls:
        call_id = call["call_id"]
        if call_id not in expected_calls or call["ids"] != expected_calls[call_id]["ids"]:
            raise ValueError("call schedule differs")
        attempted.append(call_id)
        for field in fields:
            value = call.get(field)
            if value is None:
                unknown[field] += 1
            elif isinstance(value, int) and value >= 0:
                costs[field + "_observed_subtotal"] += value
            else:
                raise ValueError("invalid usage")
        if call["status"] == "returned_valid":
            for key, prediction in call["prediction"].items():
                if key in predictions:
                    duplicate_ids.append(key)
                    continue
                predictions[key] = prediction
                label = labels[key]
                per_class[label]["available"] += 1
                per_class[label]["correct"] += prediction == label
                per_class[label]["confusion"][prediction] += 1
    duplicate_calls = [key for key, count in Counter(attempted).items() if count > 1]
    complete = (
        len(calls) == expected_calls_count
        and len(predictions) == expected_ids_count
        and not duplicate_ids
        and not duplicate_calls
        and all(call["status"] == "returned_valid" for call in calls)
    )
    correct = sum(predictions[key] == labels[key] for key in predictions)
    for row in per_class.values():
        row["unavailable"] = row["planned"] - row["available"]
        row["accuracy_available"] = row["correct"] / row["available"] if row["available"] else None
    return {
        "complete": complete,
        "inventory": {
            "expected_calls": expected_calls_count,
            "expected_ids": expected_ids_count,
            "attempted_calls": len(calls),
            "valid_calls": sum(call["status"] == "returned_valid" for call in calls),
            "invalid_calls": sum(call["status"] == "invalid_response" for call in calls),
            "request_errors": sum(call["status"] == "request_error" for call in calls),
            "unattempted_calls": expected_calls_count - len(set(attempted)),
            "duplicate_call_ids": duplicate_calls,
            "duplicate_record_ids": duplicate_ids,
            "missing_ids": sorted(set(expected_ids) - set(predictions)),
        },
        "metrics": {
            "correct": correct,
            "available_predictions": len(predictions),
            "unavailable_predictions": expected_ids_count - len(predictions),
            "accuracy_available": correct / len(predictions) if predictions else None,
            "primary_accuracy": correct / expected_ids_count if complete else None,
        },
        "per_class": per_class,
        "predictions": predictions,
        "calls": calls,
        "cost": {
            **costs,
            "unknown_usage_calls": unknown,
            "wall_seconds_sum_observed": sum(call.get("wall_seconds", 0) for call in calls),
            "missing_usage_is_not_zero": True,
        },
    }

