"""Host-only final answer, native trace, helper map and physical-cost audit."""

from collections import Counter
import copy
import re

import protocol
import study


def inspect(raw, coordinate, context, gold, roots, wrappers, censored=False):
    traces = raw.get("traces") or []
    trace = traces[0] if len(traces) == 1 else {}
    own_wrappers = [row for row in wrappers if row.get("coordinate_id") == coordinate["id"]]
    wrapper_ids = {row["request_id"] for row in own_wrappers}
    # Explicitly remove the non-model map-wrapper calls, not the underlying live B4 calls:
    # those have their own physical envelopes and are audited separately.
    root_trace = copy.deepcopy(trace)
    # Real native fixture showed that logical trace.model retains the caller root alias
    # even for the non-model helper wrapper. Use the exact trusted ACP request ID, not
    # a presumed response-model alias, to authenticate this explicit exclusion.
    wrapper_calls = [call for call in trace.get("calls", [])
                     if (call.get("acp") or {}).get("request_id") in wrapper_ids]
    root_trace["calls"] = [call for call in trace.get("calls", [])
                           if (call.get("acp") or {}).get("request_id") not in wrapper_ids]
    native = [row for row in roots if row.get("coordinate_id") == coordinate["id"]]
    mapping = study.sources()[4].map_trace(root_trace, native, max_actions=6)
    errors = [*raw.get("errors", []), *trace.get("errors", [])]
    stopped = trace.get("stop_condition")
    reply = trace.get("root_reply")
    match = re.fullmatch(r"Answer: ([0-9]+)", reply.strip()) if isinstance(reply, str) else None
    answer = int(match[1]) if match else None
    wrapper_bridge_complete = len(wrapper_calls) == len(own_wrappers) and len(wrapper_ids) == len(own_wrappers)
    physical_authenticated = mapping["complete"] and mapping["root_actions"] > 0 and wrapper_bridge_complete
    if censored or errors or not physical_authenticated:
        status, available, reward = "infrastructure_unavailable", False, None
    elif stopped in {"max_turns", "max_input_tokens", "max_output_tokens", "max_total_tokens"}:
        status, available, reward = "model_finite_horizon", True, 0
    elif not raw.get("ok") or len(traces) != 1:
        status, available, reward = "unqualified_terminal", False, None
    elif answer is None:
        status, available, reward = "model_malformed_final", True, 0
    else:
        status, available = "valid_final", True
        reward = int(answer == gold["answers"][coordinate["operator"]])
    valid_maps = [row for row in own_wrappers if row.get("status") == "returned"]
    helper = {"logical_invocations": len(own_wrappers), "complete_maps": len(valid_maps),
              "aggregate": None, "local_correct": None, "records": 0, "root_equals_map_aggregate": None,
              "map_aggregate_equals_gold": None, "error_separation": "no complete helper map"}
    if len(valid_maps) == 1:
        labels = valid_maps[0]["labels"]
        value = protocol.aggregate(context["records"], labels, coordinate)
        truth = gold["answers"][coordinate["operator"]]
        helper.update(aggregate=value, local_correct=sum(labels[key] == label for key, label in gold["labels"].items()),
            records=16, root_equals_map_aggregate=answer == value if answer is not None else None,
            map_aggregate_equals_gold=value == truth)
        if answer is None:
            helper["error_separation"] = "helper evidence acquired; no valid root final"
        elif answer == truth:
            helper["error_separation"] = "root correct; map aggregate correct" if value == truth else "root correct despite wrong map aggregate"
        elif value == truth:
            helper["error_separation"] = "wrong root final despite correct map aggregate"
        elif answer == value:
            helper["error_separation"] = "wrong root final agrees with wrong map aggregate"
        else:
            helper["error_separation"] = "wrong root final and wrong map aggregate disagree"
    return {"status": status, "available": available, "reward": reward, "root_reply": reply,
            "parsed_answer": answer, "gold_answer": gold["answers"][coordinate["operator"]],
            "stop_condition": stopped, "errors": errors, "root_native_mapping": mapping,
            "wrapper_bridge": {"complete": wrapper_bridge_complete, "request_ids": sorted(wrapper_ids),
                               "logical_calls": len(wrapper_calls), "model_samples": 0}, "helper": helper}


def summarize(records, root_calls, helper_calls):
    result = {"planned_episodes": 48, "context_clusters": 8, "pairs_per_comparison": 16,
              "observed_episodes": len(records), "arms": {}, "paired": {}, "physical_costs": {}}
    for arm in study.ARMS:
        rows = [row for row in records if row["coordinate"]["arm"] == arm]
        available = [row for row in rows if row["derived"]["available"]]
        result["arms"][arm] = {"planned": 16, "recorded": len(rows), "available": len(available),
            "correct": sum(row["derived"]["reward"] == 1 for row in available),
            "unavailable_including_unattempted": 16 - len(available),
            "statuses": dict(Counter(row["derived"]["status"] for row in rows)),
            "complete_helper_maps": sum(row["derived"]["helper"]["complete_maps"] for row in rows),
            "helper_label_correct_observed": sum(row["derived"]["helper"]["local_correct"] or 0 for row in rows),
            "helper_label_decisions_observed": sum(row["derived"]["helper"]["records"] for row in rows),
            "trace_consistency_not_causal_attribution": dict(Counter(row["derived"]["helper"]["error_separation"] for row in rows))}
    by_pair = {}
    for row in records:
        by_pair.setdefault(row["coordinate"]["pair_id"], {})[row["coordinate"]["arm"]] = row
    for left, right in (("c32", "rl_step8"), ("no_child_python", "c32"), ("no_child_python", "rl_step8")):
        wins, losses, ties, unknown = [], [], [], []
        for coordinate in study.plan(left):
            pair = by_pair.get(coordinate["pair_id"], {})
            a, b = pair.get(left), pair.get(right)
            if not a or not b or not a["derived"]["available"] or not b["derived"]["available"]:
                unknown.append(coordinate["pair_id"])
            elif b["derived"]["reward"] > a["derived"]["reward"]:
                wins.append(coordinate["pair_id"])
            elif b["derived"]["reward"] < a["derived"]["reward"]:
                losses.append(coordinate["pair_id"])
            else:
                ties.append(coordinate["pair_id"])
        result["paired"][left + "->" + right] = {"wins": wins, "losses": losses, "ties": ties, "unavailable": unknown}
    def cost_summary(name, calls):
        cost = {"attempts": len(calls), "returned": sum(row.get("status") in ("returned", "returned_valid") for row in calls)}
        for field in ("prompt_tokens", "completion_tokens", "cached_prompt_tokens"):
            values = []
            for row in calls:
                usage = (row.get("response") or {}).get("usage") or {}
                value = row.get(field) if name == "helper_B4" else (
                    (usage.get("prompt_tokens_details") or {}).get("cached_tokens") if field == "cached_prompt_tokens" else usage.get(field))
                values.append(value)
            cost[field + "_observed_subtotal"] = sum(value for value in values if isinstance(value, int))
            cost[field + "_unknown_calls"] = sum(not isinstance(value, int) for value in values)
        return cost
    for name, calls in (("root", root_calls), ("helper_B4", helper_calls)):
        result["physical_costs"][name] = cost_summary(name, calls)
    result["physical_costs"]["by_arm"] = {}
    for arm in study.ARMS:
        identifiers = {row["id"] for row in study.plan(arm)}
        result["physical_costs"]["by_arm"][arm] = {
            "root": cost_summary("root", [row for row in root_calls if row.get("coordinate_id") in identifiers]),
            "helper_B4": cost_summary("helper_B4", [row for row in helper_calls if row.get("coordinate_id") in identifiers])}
    provider_ids = [(row.get("response") or {}).get("id") for row in root_calls if row.get("status") == "returned"]
    provider_ids += [row.get("request_id") for row in helper_calls if row.get("status") == "returned_valid"]
    duplicate_ids = [key for key, count in Counter(provider_ids).items() if key and count > 1]
    result["native_inventory"] = {"duplicate_provider_response_ids": duplicate_ids,
        "missing_provider_response_ids": sum(not isinstance(key, str) or not key for key in provider_ids),
        "root_attempts_le288": len(root_calls) <= 288, "helper_attempts_le128": len(helper_calls) <= 128,
        "helper_calls_per_episode_max": max(Counter(row.get("coordinate_id") for row in helper_calls).values(), default=0)}
    result["complete"] = (len(records) == 48 and all(row["unavailable_including_unattempted"] == 0 for row in result["arms"].values())
        and not duplicate_ids and not result["native_inventory"]["missing_provider_response_ids"]
        and len(root_calls) <= 288 and len(helper_calls) <= 128)
    result["claim_boundary"] = "fresh AG content, familiar operators, frozen root; prescribed B4 helper acquisition; not new operator/partition learning"
    return result
