"""Explicit yes/no interpretation for frozen matched metrics; raw labels remain unchanged."""

import copy
from collections import Counter

import yesno_study as study

matched = study.prior.load("yesno_existing_matched_metrics", study.TARGET / "metrics.py")


def summarize(calls, schedule, gold):
    normalized = copy.deepcopy(calls)
    behavior = {}
    for row in schedule:
        if row["arm"] == "targeted":
            behavior.setdefault(f"{row['dataset']}:{row['target']}", Counter())["planned_maps"] += 1
    for call in normalized:
        if call["arm"] != "targeted":
            continue
        key = f"{call['dataset']}:{call['target']}"
        metric = behavior.setdefault(key, Counter())
        metric["attempted_maps"] += 1
        if call["status"] != "returned_valid":
            metric["unavailable_maps"] += 1
            continue
        values = list(call["prediction"].values())
        if any(value not in ("yes", "no") for value in values):
            raise ValueError("binary interpretation only accepts literal yes/no")
        positive = values.count("yes")
        metric["available_maps"] += 1
        metric["available_records"] += len(values)
        metric["predicted_positive"] += positive
        metric["all_yes_maps"] += int(positive == len(values))
        metric["all_no_maps"] += int(positive == 0)
        call["prediction"] = {
            identifier: call["target"] if value == "yes" else "other"
            for identifier, value in call["prediction"].items()
        }
    value = matched.summarize(normalized, schedule, gold)
    value["schema"] = "helper-trec-yesno-counts-result-v1"
    for metric in behavior.values():
        metric["unattempted_maps"] = metric["planned_maps"] - metric["attempted_maps"]
        metric["unavailable_maps"] = metric["planned_maps"] - metric["available_maps"]
    value["binary_behavior"] = {key: dict(item) for key, item in behavior.items()}
    value["scoring_mapping"] = {
        "yes": "positive membership in request target",
        "no": "complement of target",
    }
    value["raw_predictions_preserved"] = True
    return value


def secondary(current, old, blocks):
    selected = {"old_literal_other": old, "new_yesno": current}
    output = {
        "frozen_original_complete_blocks": blocks,
        "planned_paired_tasks": len(blocks) * 6,
        "boundary": "cross-service/cache-history diagnostic only; not primary48-task result",
    }
    for name, result in selected.items():
        tasks = [
            task
            for task in result["tasks"]
            if task["dataset"] == "trec" and task["block"] in blocks
        ]
        output[name] = {}
        for arm in ("full", "targeted"):
            available = [task for task in tasks if task["arms"][arm]["predicted_count"] is not None]
            counts = {
                "available_tasks": len(available),
                "unavailable_tasks": len(tasks) - len(available),
                "exact_count_tasks": sum(task["arms"][arm]["exact_count"] for task in available),
                "sum_absolute_count_error": sum(
                    abs(task["arms"][arm]["signed_count_error"]) for task in available
                ),
            }
            confusion = {}
            for target in sorted({task["target"] for task in tasks}):
                confusion[target] = {
                    field: sum(
                        task["arms"][arm][field] for task in tasks if task["target"] == target
                    )
                    for field in ("TP", "FP", "TN", "FN", "missing_positive", "missing_negative")
                }
            counts["per_target"] = confusion
            output[name][arm] = counts
    old_control, new_control = output["old_literal_other"]["full"], output["new_yesno"]["full"]
    output["fresh_full_control_drift"] = {
        "comparable_available": not new_control["unavailable_tasks"],
        "new_minus_old_exact_counts": (
            new_control["exact_count_tasks"] - old_control["exact_count_tasks"]
            if not new_control["unavailable_tasks"]
            else None
        ),
        "new_minus_old_absolute_error": (
            new_control["sum_absolute_count_error"] - old_control["sum_absolute_count_error"]
            if not new_control["unavailable_tasks"]
            else None
        ),
    }
    return output
