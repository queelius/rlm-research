"""Host-only matched binary/count endpoints; physical costs counted once."""

from collections import Counter

FIELDS = ("TP", "FP", "TN", "FN", "missing_positive", "missing_negative")


def rates(metric):
    positive = metric["TP"] + metric["FN"] + metric["missing_positive"]
    negative = metric["TN"] + metric["FP"] + metric["missing_negative"]
    metric["recall_bounds"] = (
        [metric["TP"] / positive, (metric["TP"] + metric["missing_positive"]) / positive]
        if positive
        else None
    )
    metric["specificity_bounds"] = (
        [metric["TN"] / negative, (metric["TN"] + metric["missing_negative"]) / negative]
        if negative
        else None
    )
    metric["positive_recall"] = (
        metric["TP"] / positive if positive and not metric["missing_positive"] else None
    )
    metric["specificity"] = (
        metric["TN"] / negative if negative and not metric["missing_negative"] else None
    )
    a, b = metric["positive_recall"], metric["specificity"]
    metric["balanced_accuracy"] = (a + b) / 2 if a is not None and b is not None else None
    metric["balanced_accuracy_bounds"] = (
        [(metric["recall_bounds"][i] + metric["specificity_bounds"][i]) / 2 for i in (0, 1)]
        if positive and negative
        else None
    )


def cost(call):
    if call is None or any(call.get(key) is None for key in ("prompt_tokens", "completion_tokens")):
        return None
    return call["prompt_tokens"] + call["completion_tokens"]


def components(call):
    return {
        field: call.get(field) if call is not None else None
        for field in ("prompt_tokens", "completion_tokens", "cached_prompt_tokens", "wall_seconds")
    }


def summarize(calls, schedule, gold):
    planned = {row["call_id"]: row for row in schedule}
    observed = {row["call_id"]: row for row in calls}
    if (
        len(planned) != len(schedule)
        or len(observed) != len(calls)
        or not observed.keys() <= planned.keys()
    ):
        raise ValueError("duplicate or out-of-inventory call")
    physical, blocks = {}, {}
    for row in schedule:
        call = observed.get(row["call_id"])
        if call and any(
            call[key] != row[key] for key in ("dataset", "block", "ids", "arm", "target")
        ):
            raise ValueError("call coordinate mismatch")
        block = blocks.setdefault((row["dataset"], row["block"]), {})
        coordinate = row["target"] if row["arm"] == "targeted" else None
        if coordinate in block:
            raise ValueError("duplicate task coordinate")
        block[coordinate] = row
        key = row["dataset"] + ":" + row["arm"]
        metric = physical.setdefault(
            key,
            {
                "planned_calls": 0,
                "attempted_calls": 0,
                "planned_predictions": 0,
                "status_counts": Counter(),
                "usage_unknown_calls": 0,
                "cache_usage_unknown_calls": 0,
                "prompt_tokens_observed_subtotal": 0,
                "completion_tokens_observed_subtotal": 0,
                "cached_tokens_observed_subtotal": 0,
                "planned_prompt_tokens": 0,
                "attempted_prompt_tokens": 0,
                "wall_seconds": 0.0,
            },
        )
        metric["planned_calls"] += 1
        metric["planned_predictions"] += len(row["ids"])
        metric["planned_prompt_tokens"] += len(row["body"]["token_ids"])
        status = call["status"] if call else "unattempted"
        metric["status_counts"][status] += 1
        if call:
            metric["attempted_calls"] += 1
            metric["attempted_prompt_tokens"] += len(row["body"]["token_ids"])
            metric["usage_unknown_calls"] += int(cost(call) is None)
            metric["cache_usage_unknown_calls"] += int(call.get("cached_prompt_tokens") is None)
            for field, target in (
                ("prompt_tokens", "prompt_tokens_observed_subtotal"),
                ("completion_tokens", "completion_tokens_observed_subtotal"),
                ("cached_prompt_tokens", "cached_tokens_observed_subtotal"),
            ):
                metric[target] += call.get(field) or 0
            metric["wall_seconds"] += call.get("wall_seconds", 0)
    tasks, per_target, datasets, costs, consistency = [], {}, {}, {}, {}
    for (dataset, block_index), block in blocks.items():
        full = block[None]
        labels = full["labels"]
        if set(block) != {None, *labels} or any(
            row["ids"] != full["ids"] for row in block.values()
        ):
            raise ValueError("missing target schedule or mismatched full/target records")
        full_call = observed.get(full["call_id"])
        target_calls = [observed.get(block[label]["call_id"]) for label in labels]
        block_cost = {
            "block": block_index,
            "full_call_id": full["call_id"],
            "full_total_tokens": cost(full_call),
            "target_costs": {
                label: cost(call) for label, call in zip(labels, target_calls, strict=True)
            },
            "full_components": components(full_call),
            "target_components": {
                label: components(call) for label, call in zip(labels, target_calls, strict=True)
            },
        }
        costs.setdefault(dataset, {"blocks": []})["blocks"].append(block_cost)
        c = consistency.setdefault(dataset, Counter())
        for identifier in full["ids"]:
            c["planned_records"] += 1
            if any(call is None or call["status"] != "returned_valid" for call in target_calls):
                c["unavailable_records"] += 1
            else:
                positives = sum(
                    call["prediction"][identifier] == target
                    for target, call in zip(labels, target_calls, strict=True)
                )
                c[
                    "zero_positive"
                    if positives == 0
                    else "one_positive"
                    if positives == 1
                    else "multiple_positive"
                ] += 1
        for target in labels:
            task = {
                "dataset": dataset,
                "block": block_index,
                "target": target,
                "ids": full["ids"],
                "gold_count": sum(gold["labels"][key] == target for key in full["ids"]),
                "arms": {},
            }
            for arm, row in (("full", full), ("targeted", block[target])):
                call = observed.get(row["call_id"])
                valid = call is not None and call["status"] == "returned_valid"
                confusion = dict.fromkeys(FIELDS, 0)
                predicted_count = 0
                for identifier in row["ids"]:
                    positive = gold["labels"][identifier] == target
                    if not valid:
                        confusion["missing_positive" if positive else "missing_negative"] += 1
                        continue
                    predicted = call["prediction"][identifier] == target
                    predicted_count += int(predicted)
                    confusion[
                        "TP"
                        if positive and predicted
                        else "FN"
                        if positive
                        else "FP"
                        if predicted
                        else "TN"
                    ] += 1
                entry = {
                    **confusion,
                    "call_id": row["call_id"],
                    "status": call["status"] if call else "unattempted",
                    "predicted_count": predicted_count if valid else None,
                    "signed_count_error": predicted_count - task["gold_count"] if valid else None,
                    "exact_count": predicted_count == task["gold_count"] if valid else None,
                }
                rates(entry)
                task["arms"][arm] = entry
                target_key = f"{dataset}:{target}:{arm}"
                accumulated = per_target.setdefault(target_key, dict.fromkeys(FIELDS, 0))
                for field in FIELDS:
                    accumulated[field] += confusion[field]
                metric = datasets.setdefault(dataset, {}).setdefault(
                    arm,
                    {
                        "planned_count_tasks": 0,
                        "available_count_tasks": 0,
                        "unavailable_count_tasks": 0,
                        "exact_count_tasks": 0,
                        "sum_absolute_count_error": 0,
                        "sum_signed_count_error": 0,
                        "planned_decisions": 0,
                        "unavailable_decisions": 0,
                    },
                )
                metric["planned_count_tasks"] += 1
                metric["available_count_tasks"] += int(valid)
                metric["unavailable_count_tasks"] += int(not valid)
                metric["planned_decisions"] += len(row["ids"])
                metric["unavailable_decisions"] += len(row["ids"]) * int(not valid)
                if valid:
                    metric["exact_count_tasks"] += int(entry["exact_count"])
                    metric["sum_absolute_count_error"] += abs(entry["signed_count_error"])
                    metric["sum_signed_count_error"] += entry["signed_count_error"]
            tasks.append(task)
    for metric in per_target.values():
        rates(metric)
    for dataset, arms in datasets.items():
        for arm, metric in arms.items():
            values = [
                value["balanced_accuracy"]
                for key, value in per_target.items()
                if key.startswith(dataset + ":") and key.endswith(":" + arm)
            ]
            metric["macro_balanced_accuracy"] = (
                sum(values) / len(values) if all(v is not None for v in values) else None
            )
            metric["exact_count_bounds"] = [
                metric["exact_count_tasks"],
                metric["exact_count_tasks"] + metric["unavailable_count_tasks"],
            ]
            metric["absolute_error_is_available_subtotal"] = bool(metric["unavailable_count_tasks"])
        paired = Counter()
        for task in (task for task in tasks if task["dataset"] == dataset):
            a, b = (task["arms"][arm]["exact_count"] for arm in ("full", "targeted"))
            category = (
                "both_unavailable"
                if a is None and b is None
                else "full_unavailable"
                if a is None
                else "targeted_unavailable"
                if b is None
                else "both_exact"
                if a and b
                else "both_inexact"
                if not a and not b
                else "targeted_wins"
                if b
                else "targeted_losses"
            )
            paired[category] += 1
        arms["paired_exact_count"] = dict(paired)
        values = costs[dataset]["blocks"]
        complete_usage = all(
            v["full_total_tokens"] is not None
            and all(t is not None for t in v["target_costs"].values())
            for v in values
        )
        for view in ("single_uniform_target", "all_targets"):
            full_total = sum(v["full_total_tokens"] for v in values) if complete_usage else None
            targeted_total = (
                sum(
                    sum(v["target_costs"].values())
                    / (len(v["target_costs"]) if view == "single_uniform_target" else 1)
                    for v in values
                )
                if complete_usage
                else None
            )
            costs[dataset][view] = {
                "complete_usage": complete_usage,
                "full_total_tokens": full_total,
                "targeted_total_tokens": targeted_total,
                "token_ratio": targeted_total / full_total if full_total else None,
                "full_calls": len(values),
                "targeted_calls": len(values)
                if view == "single_uniform_target"
                else sum(len(v["target_costs"]) for v in values),
            }
            for field in (
                "prompt_tokens",
                "completion_tokens",
                "cached_prompt_tokens",
                "wall_seconds",
            ):
                known = all(
                    v["full_components"][field] is not None
                    and all(t[field] is not None for t in v["target_components"].values())
                    for v in values
                )
                costs[dataset][view][field] = {
                    "full": sum(v["full_components"][field] for v in values) if known else None,
                    "targeted": sum(
                        sum(t[field] for t in v["target_components"].values())
                        / (len(v["target_components"]) if view == "single_uniform_target" else 1)
                        for v in values
                    )
                    if known
                    else None,
                    "complete_usage": known,
                }
        a, b = arms["full"], arms["targeted"]
        ratio = costs[dataset]["single_uniform_target"]["token_ratio"]
        eligible = (
            not a["unavailable_count_tasks"]
            and not b["unavailable_count_tasks"]
            and ratio is not None
        )
        arms["prospective_screen"] = {
            "eligible_complete": eligible,
            "token_budget": 1.25,
            "passes": bool(
                eligible
                and b["exact_count_tasks"] > a["exact_count_tasks"]
                and b["sum_absolute_count_error"] < a["sum_absolute_count_error"]
                and b["macro_balanced_accuracy"] is not None
                and a["macro_balanced_accuracy"] is not None
                and b["macro_balanced_accuracy"] >= a["macro_balanced_accuracy"]
                and ratio <= 1.25
            ),
            "meaning": "screen for independent root-count ablation, not a validated gain",
        }
    for metric in physical.values():
        metric["status_counts"] = dict(metric["status_counts"])
    return {
        "schema": "helper-targeted-category-counts-result-v1",
        "planned_calls": len(schedule),
        "attempted_calls": len(calls),
        "planned_physical_predictions": sum(len(r["ids"]) for r in schedule),
        "physical": physical,
        "tasks": tasks,
        "per_target": per_target,
        "datasets": datasets,
        "cost_views": costs,
        "targeted_consistency": {key: dict(value) for key, value in consistency.items()},
        "cost_boundary": "observed subtotals; unknown usage is not zero cost; full map paid once",
        "claim_boundary": "exposed exploratory panel; related tasks; no training or root claim",
    }
