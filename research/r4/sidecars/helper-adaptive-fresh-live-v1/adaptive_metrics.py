"""Gold-free live routing, staged execution, and physical versus logical accounting."""

from collections import Counter

POLICIES = ("original16", "three_vote", "selective_singleton", "always_singleton")


def maps(calls):
    result = {}
    for call in calls:
        if call["status"] == "returned_valid":
            result.setdefault(call["arm"], {}).update(call["prediction"])
    return result


def route(calls, public):
    predictions = maps(calls)
    original, other = predictions.get("original", {}), predictions.get("neighbor_A", {})
    selected, unavailable, agreed = [], [], {}
    for row in public:
        identifier = row["id"]
        if identifier not in original or identifier not in other:
            unavailable.append(identifier)
        elif original[identifier] != other[identifier]:
            selected.append(identifier)
        else:
            agreed[identifier] = original[identifier]
    return {
        "schema": "adaptive-gold-free-routing-v1",
        "selected_ids": selected,
        "unavailable_ids": unavailable,
        "agreed_predictions": agreed,
        "source_call_ids": [c["call_id"] for c in calls if c["arm"] in ("original", "neighbor_A")],
        "used_gold": False,
        "used_neighbor_B": False,
        "used_singletons": False,
    }


def collect(rows, public, call_one, commit):
    calls = [call_one(r) for r in rows if r["arm"] in ("original", "neighbor_A")]
    routing = route(calls, public)
    commit(routing, calls)
    chosen = set(routing["selected_ids"])
    calls.extend(call_one(r) for r in rows if r["arm"] == "singleton" and r["ids"][0] in chosen)
    calls.extend(call_one(r) for r in rows if r["arm"] == "neighbor_B")
    calls.extend(call_one(r) for r in rows if r["arm"] == "singleton" and r["ids"][0] not in chosen)
    return calls, routing


def cost(rows, by_call):
    calls = [by_call[r["call_id"]] for r in rows if r["call_id"] in by_call]

    def valid_count(value):
        return type(value) is int and value >= 0

    input_sum = sum(c.get("prompt_tokens", 0) for c in calls if valid_count(c.get("prompt_tokens")))
    output_sum = sum(
        c.get("completion_tokens", 0) for c in calls if valid_count(c.get("completion_tokens"))
    )
    unknown = sum(
        not all(valid_count(c.get(k)) for k in ("prompt_tokens", "completion_tokens"))
        for c in calls
    )
    return {
        "planned_calls": len(rows),
        "attempted_calls": len(calls),
        "unattempted_calls": len(rows) - len(calls),
        "requested_record_slots": sum(len(r["ids"]) for r in rows),
        "status_counts": dict(
            Counter([c["status"] for c in calls] + ["unattempted"] * (len(rows) - len(calls)))
        ),
        "observed_input_tokens": input_sum,
        "observed_output_tokens": output_sum,
        "observed_total_tokens": input_sum + output_sum,
        "usage_unknown_calls": unknown,
        "usage_complete": not unknown and len(calls) == len(rows),
        "observed_cached_tokens": sum(
            c.get("cached_prompt_tokens", 0)
            for c in calls
            if valid_count(c.get("cached_prompt_tokens"))
        ),
        "cache_unknown_calls": sum(not valid_count(c.get("cached_prompt_tokens")) for c in calls),
        "planned_input_tokens": sum(len(r["body"]["token_ids"]) for r in rows),
        "planned_output_upper_bound": 1024 * len(rows),
        "observed_request_seconds": sum(c.get("wall_seconds", 0) for c in calls),
        "cost_scope": (
            "Observed physical-token subtotal; missing usage and unattempted calls are not free. "
            "Shared-cache latency is not an independent policy estimate."
        ),
        "call_ids": [r["call_id"] for r in rows],
    }


def paired(candidate, baseline, ids, gold):
    counts = Counter()
    for identifier in ids:
        a, b = baseline.get(identifier), candidate.get(identifier)
        if a is None or b is None:
            counts["baseline_unavailable"] += a is None
            counts["candidate_unavailable"] += b is None
            counts["either_unavailable"] += 1
            continue
        counts["valid_pairs"] += 1
        counts["label_disagreements"] += a != b
        correct_a, correct_b = a == gold[identifier], b == gold[identifier]
        key = (
            "both_correct"
            if correct_a and correct_b
            else "both_wrong"
            if not correct_a and not correct_b
            else "wins"
            if correct_b
            else "losses"
        )
        counts[key] += 1
    return {"denominator": len(ids), **dict(counts)}


def summarize(calls, rows, public, gold, routing):
    by_call = {c["call_id"]: c for c in calls}
    if len(by_call) != len(calls):
        raise ValueError("duplicate physical call")
    predictions = maps(calls)
    original = predictions.get("original", {})
    vote, ties = {}, []
    for row in public:
        identifier = row["id"]
        values = [
            predictions.get(a, {}).get(identifier) for a in ("original", "neighbor_A", "neighbor_B")
        ]
        if None not in values:
            if len(set(values)) == 3:
                vote[identifier] = values[0]
                ties.append(identifier)
            else:
                vote[identifier] = Counter(values).most_common(1)[0][0]
    selected = set(routing["selected_ids"]) if routing is not None else set()
    selective = dict(routing["agreed_predictions"]) if routing is not None else {}
    singleton = predictions.get("singleton", {})
    selective.update({i: singleton[i] for i in selected if i in singleton})
    policy_maps = dict(zip(POLICIES, (original, vote, selective, singleton), strict=True))
    datasets = {}
    for dataset in dict.fromkeys(r["dataset"] for r in public):
        ids = [r["id"] for r in public if r["dataset"] == dataset]
        dataset_rows = [r for r in rows if r["dataset"] == dataset]
        policy_rows = {
            "original16": [r for r in dataset_rows if r["arm"] == "original"],
            "three_vote": [r for r in dataset_rows if r["arm"] != "singleton"],
            "selective_singleton": [
                r
                for r in dataset_rows
                if r["arm"] in ("original", "neighbor_A")
                or r["arm"] == "singleton"
                and r["ids"][0] in selected
            ],
            "always_singleton": [r for r in dataset_rows if r["arm"] == "singleton"],
        }
        policies = {}
        for name, pred in policy_maps.items():
            available = {i: pred[i] for i in ids if i in pred}
            per_class = {}
            for label in sorted({gold[i] for i in ids}):
                members = [i for i in ids if gold[i] == label]
                per_class[label] = {
                    "records": len(members),
                    "correct": sum(pred.get(i) == label for i in members),
                    "unavailable": sum(i not in pred for i in members),
                    "predictions": dict(Counter(pred.get(i, "UNAVAILABLE") for i in members)),
                }
            policies[name] = {
                "records": len(ids),
                "correct": sum(pred.get(i) == gold[i] for i in ids),
                "unavailable": len(ids) - len(available),
                "prediction_by_id": available,
                "per_class": per_class,
                "cost": cost(policy_rows[name], by_call),
            }
        comparisons = {
            f"{name}_vs_{baseline}": paired(policy_maps[name], policy_maps[baseline], ids, gold)
            for name in POLICIES
            for baseline in ("original16", "three_vote")
            if name != baseline
        }
        comparisons["selective_singleton_vs_always_singleton"] = paired(
            selective, singleton, ids, gold
        )
        complete = all(
            not p["unavailable"] and p["cost"]["usage_complete"] for p in policies.values()
        )
        adaptive, ensemble = policies["selective_singleton"], policies["three_vote"]
        metric_passes = (
            complete
            and adaptive["correct"] >= ensemble["correct"]
            and adaptive["cost"]["observed_total_tokens"]
            < ensemble["cost"]["observed_total_tokens"]
        )
        datasets[dataset] = {
            "records": len(ids),
            "policies": policies,
            "paired": comparisons,
            "escalated_ids": [i for i in ids if i in selected],
            "routing_unavailable_ids": [
                i for i in ids if routing is None or i in routing["unavailable_ids"]
            ],
            "common_wrong_consensus_ids": [
                i
                for i in ids
                if routing is not None
                and i in routing["agreed_predictions"]
                and routing["agreed_predictions"][i] != gold[i]
            ],
            "three_distinct_tie_original_ids": [i for i in ids if i in ties],
            "complete_available_with_usage": complete,
            "screen": {
                "metric_passes": metric_passes,
                "passes": False,
                "requires_runtime_and_complete_panel": True,
            },
        }
    return {
        "schema": "fresh-adaptive-helper-result-v1",
        "datasets": datasets,
        "physical_cost": cost(rows, by_call),
        "unique_records": len(public),
        "routing_committed": routing is not None,
        "complete_available": all(d["complete_available_with_usage"] for d in datasets.values()),
        "limitations": [
            "Exploratory five-observed-class TREC; six-label schema remains.",
            "Matched shared components, not independent cold-service policy trials.",
            "Known-style ensemble baseline; no new algorithm or general recursion claim.",
        ],
    }
