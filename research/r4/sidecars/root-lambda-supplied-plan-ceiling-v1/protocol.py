"""Strict child map and deterministic public J1 reducer."""
import json
import math

CATEGORIES = ("human being", "location", "abbreviation", "entity",
              "description and abstract concept", "numeric value")


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result: raise ValueError("duplicate map ID")
        result[key] = value
    return result


def score(content, ids, gold, authenticated, tool_calls=False):
    result = {"available": bool(authenticated), "complete_map": False,
              "strict_correct": None if not authenticated else 0, "labels": None,
              "canonical_id_matches": None if not authenticated else 0,
              "output_order_equal": None, "invalid_reason": None}
    if not authenticated: return result
    try:
        if tool_calls: raise ValueError("wrong tool route; no execution")
        labels = json.loads(content, object_pairs_hook=unique)
        if not isinstance(labels, dict): raise ValueError("not a JSON object")
        result["canonical_id_matches"] = sum(
            key in labels and isinstance(labels[key], str) and labels[key] in CATEGORIES
            for key in ids
        )
        if (set(labels) != set(ids) or len(ids) != len(set(ids))
                or any(not isinstance(value, str) or value not in CATEGORIES
                       for value in labels.values())):
            raise ValueError("incomplete/extra/noncanonical map")
        result.update(complete_map=True, labels=labels,
                      strict_correct=sum(labels[key] == gold[key] for key in ids),
                      output_order_equal=list(labels) == ids)
    except (ValueError, TypeError) as error:
        result["invalid_reason"] = str(error)
    return result


def native(raw, body, renderer):
    if raw["model"] != body["model"] or len(raw["choices"]) != 1:
        raise ValueError("native model/choice identity")
    choice = raw["choices"][0]; ids = choice["token_ids"]; logs = choice["logprobs"]["content"]
    usage = raw["usage"]
    if not ids or len(ids) != len(logs) or not all(math.isfinite(item["logprob"]) for item in logs):
        raise ValueError("token/logprob identity")
    if usage["prompt_tokens"] != len(body["token_ids"]) or usage["completion_tokens"] != len(ids):
        raise ValueError("native prompt/output usage")
    if not isinstance(raw.get("request_id"), str) or not raw["request_id"]:
        raise ValueError("provider request identity")
    if choice["finish_reason"] not in ("stop", "length", "tool_calls"):
        raise ValueError("unverified finish reason")
    parsed = renderer.parse_response(ids)
    return {"content": parsed.content,
            "tool_calls": bool(parsed.tool_calls) or choice["finish_reason"] == "tool_calls",
            "finish_reason": choice["finish_reason"], "completion_ids": ids,
            "provider_request_id": raw["request_id"]}


def reduce_j1(records, labels, spec):
    expected = {row["id"] for row in records}
    if set(labels) != expected: raise ValueError("reducer requires one label for every record")
    qualifying = sorted({row["user"] for row in records
                         if row["user"] in spec["users"] and labels[row["id"]] == spec["target"]})
    contributions = {row["id"]: row["weight"]
                     if row["user"] in qualifying and labels[row["id"]] == spec["target_b"] else 0
                     for row in records}
    return {"answer": sum(contributions.values()), "qualifying_users": qualifying,
            "contributions": contributions}
