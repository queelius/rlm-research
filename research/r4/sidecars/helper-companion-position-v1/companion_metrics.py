"""Four related full-label treatments, paired by immutable ID with explicit missing branches."""

from collections import Counter


def summarize(calls, schedule, gold):
    planned = {row["call_id"]: row for row in schedule}
    observed = {call["call_id"]: call for call in calls}
    if (
        len(planned) != len(schedule)
        or len(observed) != len(calls)
        or not observed.keys() <= planned.keys()
    ):
        raise ValueError("duplicate or out-of-inventory calls")
    metrics, predictions, outcomes = {}, {}, {}
    for row in schedule:
        key = f"{row['dataset']}:{row['arm']}"
        metric = metrics.setdefault(
            key,
            {
                "planned_calls": 0,
                "attempted_calls": 0,
                "planned_predictions": 0,
                "correct": 0,
                "wrong": 0,
                "unavailable": 0,
                "status_counts": Counter(),
                "confusion": {},
                "prompt_tokens_observed_subtotal": 0,
                "completion_tokens_observed_subtotal": 0,
                "cached_tokens_observed_subtotal": 0,
                "usage_unknown_calls": 0,
                "cache_usage_unknown_calls": 0,
                "planned_prompt_tokens": 0,
                "attempted_prompt_tokens": 0,
                "wall_seconds": 0.0,
            },
        )
        call = observed.get(row["call_id"])
        if call and any(call[key] != row[key] for key in ("dataset", "arm", "ids")):
            raise ValueError("call coordinates differ")
        status = call["status"] if call else "unattempted"
        metric["status_counts"][status] += 1
        metric["planned_calls"] += 1
        metric["attempted_calls"] += int(call is not None)
        metric["planned_predictions"] += len(row["ids"])
        metric["planned_prompt_tokens"] += len(row["body"]["token_ids"])
        valid = call is not None and status == "returned_valid"
        for identifier in row["ids"]:
            coordinate = (row["dataset"], row["arm"], identifier)
            if coordinate in predictions:
                raise ValueError("duplicate record within treatment")
            prediction = call["prediction"][identifier] if valid else None
            predictions[coordinate] = prediction
            correct = prediction == gold["labels"][identifier] if valid else None
            outcomes[coordinate] = correct
            metric["correct"] += int(correct is True)
            metric["wrong"] += int(correct is False)
            metric["unavailable"] += int(correct is None)
            if valid:
                confusion = metric["confusion"].setdefault(gold["labels"][identifier], Counter())
                confusion[prediction] += 1
        if call:
            metric["attempted_prompt_tokens"] += len(row["body"]["token_ids"])
            metric["usage_unknown_calls"] += int(
                any(call.get(k) is None for k in ("prompt_tokens", "completion_tokens"))
            )
            metric["cache_usage_unknown_calls"] += int(call.get("cached_prompt_tokens") is None)
            for field, target in (
                ("prompt_tokens", "prompt_tokens_observed_subtotal"),
                ("completion_tokens", "completion_tokens_observed_subtotal"),
                ("cached_prompt_tokens", "cached_tokens_observed_subtotal"),
            ):
                metric[target] += call.get(field) or 0
            metric["wall_seconds"] += call.get("wall_seconds", 0)
    paired = {}
    for dataset in sorted({row["dataset"] for row in schedule}):
        identifiers = {
            identifier for row in schedule if row["dataset"] == dataset for identifier in row["ids"]
        }
        for baseline, challenger in (
            ("original", "reverse"),
            ("original", "neighbor_A"),
            ("original", "neighbor_B"),
            ("neighbor_A", "neighbor_B"),
        ):
            counts = Counter()
            details = []
            for identifier in sorted(identifiers):
                left, right = (dataset, baseline, identifier), (dataset, challenger, identifier)
                a, b = outcomes.get(left), outcomes.get(right)
                if a is None or b is None:
                    branch = (
                        "both_unavailable"
                        if a is None and b is None
                        else "baseline_unavailable"
                        if a is None
                        else "challenger_unavailable"
                    )
                else:
                    branch = (
                        "both_correct"
                        if a and b
                        else "both_wrong"
                        if not a and not b
                        else "challenger_wins"
                        if b
                        else "challenger_losses"
                    )
                    changed = predictions[left] != predictions[right]
                    counts["paired_available"] += 1
                    counts["prediction_disagreements"] += int(changed)
                    if changed:
                        details.append(
                            {
                                "id": identifier,
                                "gold": gold["labels"][identifier],
                                "baseline": predictions[left],
                                "challenger": predictions[right],
                            }
                        )
                counts[branch] += 1
            paired[f"{dataset}:{baseline}_vs_{challenger}"] = {
                **dict(counts),
                "planned_records": len(identifiers),
                "changed_predictions": details,
                "record_slot_preserved": baseline != "reverse" and challenger != "reverse",
                "absolute_token_offsets_preserved": False,
            }
    for metric in metrics.values():
        metric["status_counts"] = dict(metric["status_counts"])
        metric["confusion"] = {key: dict(value) for key, value in metric["confusion"].items()}
        metric["correct_bounds"] = [metric["correct"], metric["correct"] + metric["unavailable"]]
        metric["total_tokens_observed_subtotal"] = (
            metric["prompt_tokens_observed_subtotal"]
            + metric["completion_tokens_observed_subtotal"]
        )
    return {
        "schema": "helper-companion-position-result-v1",
        "planned_calls": len(schedule),
        "attempted_calls": len(calls),
        "planned_predictions": sum(len(row["ids"]) for row in schedule),
        "complete_available": len(calls) == len(schedule)
        and all(call["status"] == "returned_valid" for call in calls),
        "by_dataset_arm": metrics,
        "paired": paired,
        "cost_boundary": (
            "reported subtotals only; unknown attempted usage and unattempted calls separate"
        ),
        "claim_boundary": (
            "256 exposed records with4 related outputs; "
            "no adaptive-policy or attention-mechanism claim"
        ),
    }
