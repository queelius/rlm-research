"""Exact fixed56-call/224-record accounting and paired B4-cluster readouts."""

import math
import random
from collections import Counter

import study


def summarize(calls, gold, schedule):
    labels = gold["labels"]
    expected_ids = [key for row in schedule for key in row["ids"]]
    if len(schedule) != 56 or len(expected_ids) != 224 or set(expected_ids) != set(labels):
        raise ValueError("fixed56-call/224-gold inventory required")
    expected_calls = {row["call_id"]: row for row in schedule}
    predictions, duplicate_ids, attempted = {}, [], []
    per_class = {
        label: {
            "planned": sum(value == label for value in labels.values()),
            "available": 0,
            "correct": 0,
            "confusion": {other: 0 for other in study.LABELS},
        }
        for label in study.LABELS
    }
    fields = ("prompt_tokens", "completion_tokens", "cached_prompt_tokens")
    costs = {field + "_observed_subtotal": 0 for field in fields}
    unknown = {field: 0 for field in fields}
    for call in calls:
        identifier = call["call_id"]
        if identifier not in expected_calls or call["ids"] != expected_calls[identifier]["ids"]:
            raise ValueError("call schedule/record identity differs")
        attempted.append(identifier)
        for field in fields:
            value = call.get(field)
            if value is None:
                unknown[field] += 1
            elif isinstance(value, int) and value >= 0:
                costs[field + "_observed_subtotal"] += value
            else:
                raise ValueError("invalid returned usage count")
        if call["status"] == "returned_valid":
            if list(call["prediction"]) != call["ids"]:
                raise ValueError("valid-call ordered mapping differs")
            for key, prediction in call["prediction"].items():
                if prediction not in study.LABELS:
                    raise ValueError("invalid DBpedia category")
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
        len(calls) == 56
        and len(predictions) == 224
        and not duplicate_ids
        and not duplicate_calls
        and all(call["status"] == "returned_valid" for call in calls)
    )
    correct = sum(predictions[key] == labels[key] for key in predictions)
    for row in per_class.values():
        row["unavailable"] = row["planned"] - row["available"]
        row["accuracy_available"] = row["correct"] / row["available"] if row["available"] else None
    return {
        "schema": "helper-dbpedia224-transfer-result-v1",
        "complete": complete,
        "inventory": {
            "expected_calls": 56,
            "expected_ids": 224,
            "attempted_calls": len(calls),
            "unattempted_calls": 56 - len(set(attempted)),
            "valid_calls": sum(call["status"] == "returned_valid" for call in calls),
            "invalid_calls": sum(call["status"] == "invalid_response" for call in calls),
            "request_errors": sum(call["status"] == "request_error" for call in calls),
            "duplicate_call_ids": duplicate_calls,
            "duplicate_record_ids": duplicate_ids,
            "missing_ids": sorted(set(expected_ids) - set(predictions)),
        },
        "metrics": {
            "correct": correct,
            "available_predictions": len(predictions),
            "unavailable_predictions": 224 - len(predictions),
            "accuracy_available": correct / len(predictions) if predictions else None,
            "primary_accuracy": correct / 224 if complete else None,
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
        "claim_boundary": (
            "new locally evaluated DBpedia official-test records and label space; base pretraining unknown"
        ),
    }


def paired(baseline, updated, gold, schedule):
    left, right, labels = baseline["predictions"], updated["predictions"], gold["labels"]
    available = set(left) & set(right)
    wins = sorted(key for key in available if left[key] != labels[key] and right[key] == labels[key])
    losses = sorted(key for key in available if left[key] == labels[key] and right[key] != labels[key])
    differences = [
        sum(int(right[key] == labels[key]) - int(left[key] == labels[key]) for key in row["ids"])
        for row in schedule
        if all(key in available for key in row["ids"])
    ]
    complete = baseline["complete"] and updated["complete"] and len(differences) == 56
    interval = None
    if complete:
        rng = random.Random(202609123999)
        samples = sorted(sum(rng.choice(differences) for _ in range(56)) / 224 for _ in range(2000))
        interval = [samples[math.ceil(0.025 * 2000) - 1], samples[math.ceil(0.975 * 2000) - 1]]
    return {
        "paired_available": len(available),
        "paired_unavailable": 224 - len(available),
        "wins": len(wins),
        "losses": len(losses),
        "win_ids": wins,
        "loss_ids": losses,
        "net_correct_change": len(wins) - len(losses),
        "category_disagreements": sum(left[key] != right[key] for key in available),
        "clusters": len(differences),
        "planned_clusters": 56,
        "complete_primary_comparison": complete,
        "paired_accuracy_change": (len(wins) - len(losses)) / 224 if complete else None,
        "descriptive_cluster_bootstrap_95_interval": interval,
        "bootstrap_replicates": 2000,
        "bootstrap_seed": 202609123999,
        "uncertainty_unit": "shared four-record native request; not224 independent items",
    }

