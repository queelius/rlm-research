"""Compact paired/context-cluster and family-router diagnostic summaries."""

from collections import defaultdict


def compute(rows):
    pairs = defaultdict(dict)
    contexts = defaultdict(lambda: {"enabled_correct": 0, "no_child_correct": 0,
                                    "enabled_observed": 0, "no_child_observed": 0})
    costs = defaultdict(lambda: {"episodes": 0, "model_calls": 0, "action_tokens": 0,
                                "child_action_tokens": 0, "wall_seconds": 0.0})
    for row in rows:
        coordinate = row["coordinate"]
        mode = coordinate["mode"]
        reward = row.get("endpoint_reward")
        pairs[coordinate["pair_id"]][mode] = (reward, coordinate)
        context = contexts[coordinate["context_id"]]
        context[mode + "_observed"] += reward is not None
        context[mode + "_correct"] += reward == 1
        cost = costs[mode]
        cost["episodes"] += 1
        for key in ("model_calls", "action_tokens", "child_action_tokens"):
            cost[key] += row.get(key, 0) or 0
        cost["wall_seconds"] += row.get("wall_seconds", 0) or 0
    outcomes = {"enabled_win": 0, "no_child_win": 0, "tie": 0, "incomplete": 0}
    family_by_context = defaultdict(lambda: defaultdict(dict))
    for pair in pairs.values():
        if set(pair) != {"enabled", "no_child"} or any(pair[mode][0] is None for mode in pair):
            outcomes["incomplete"] += 1
            continue
        enabled, coordinate = pair["enabled"]
        direct, _ = pair["no_child"]
        if enabled > direct:
            outcomes["enabled_win"] += 1
        elif direct > enabled:
            outcomes["no_child_win"] += 1
        else:
            outcomes["tie"] += 1
        family_by_context[coordinate["context_id"]][coordinate["family"]][coordinate["repeat"]] = {
            "enabled": enabled, "no_child": direct}
    for value in contexts.values():
        value["enabled_minus_no_child"] = value["enabled_correct"] - value["no_child_correct"]
    context_ids = sorted(contexts)
    router_folds = []
    for held in context_ids:
        training = [item for item in context_ids if item != held]
        preferences = {}
        for family in ("J1", "J2", "M1", "M2", "T1", "T2"):
            deltas = []
            for context in training:
                for record in family_by_context[context][family].values():
                    deltas.append(record["enabled"] - record["no_child"])
            preferences[family] = "enabled" if sum(deltas) > 0 else "no_child"
        observed, correct, missing = 0, 0, 0
        for family, repeats in family_by_context[held].items():
            for record in repeats.values():
                observed += 1
                correct += record[preferences[family]]
        missing = sum(1 for pair in pairs.values() if any(v[1]["context_id"] == held for v in pair.values())
                      and (set(pair) != {"enabled", "no_child"} or any(v[0] is None for v in pair.values())))
        router_folds.append({"held_context": held, "training_contexts": training,
                             "family_preferences": preferences, "observed_pairs": observed,
                             "selected_correct": correct, "missing_pairs": missing})
    return {
        "paired_observed": outcomes,
        "contexts": dict(sorted(contexts.items())),
        "inference": {"naive_48_pair_p_value": None, "unit": "context cluster",
                      "context_clusters": len(contexts)},
        "family_router": {
            "kind": "cross-fit diagnostic using supplied family metadata",
            "feature_available_at_deployment": "family is supplied in benchmark coordinate metadata",
            "held_context_groups": len(contexts),
            "missing_pairs_not_dropped": outcomes["incomplete"],
            "folds": router_folds,
            "deployable_learned_planner": False,
        },
        "costs": dict(costs),
    }
