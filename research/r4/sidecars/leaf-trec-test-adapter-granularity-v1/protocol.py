"""Strict native map contract, independent of host gold exposure."""
import json
import math

CATEGORIES = ("human being", "location", "abbreviation", "entity", "description and abstract concept", "numeric value")


def unique(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate map ID")
        value[key] = item
    return value


def score(content, ids, gold, authenticated, tool_calls=False):
    result = {"available": bool(authenticated), "complete_map": False, "strict_correct": None if not authenticated else 0, "labels": None, "canonical_id_matches": None if not authenticated else 0, "output_order_equal": None, "invalid_reason": None}
    if not authenticated:
        return result
    try:
        if tool_calls:
            raise ValueError("wrong tool route; no execution")
        labels = json.loads(content, object_pairs_hook=unique)
        if not isinstance(labels, dict):
            raise ValueError("not a JSON object")
        result["canonical_id_matches"] = sum(key in labels and isinstance(labels[key], str) and labels[key] in CATEGORIES for key in ids)
        if set(labels) != set(ids) or len(ids) != len(set(ids)) or any(not isinstance(value, str) or value not in CATEGORIES for value in labels.values()):
            raise ValueError("incomplete/extra/noncanonical map")
        result.update(complete_map=True, labels=labels, strict_correct=sum(labels[key] == gold[key] for key in ids), output_order_equal=list(labels) == ids)
    except (ValueError, TypeError) as error:
        result["invalid_reason"] = str(error)
    return result


def native(raw, body, renderer):
    if raw["model"] != body["model"] or len(raw["choices"]) != 1:
        raise ValueError("native model/choice identity")
    choice = raw["choices"][0]
    ids = choice["token_ids"]
    logs = choice["logprobs"]["content"]
    usage = raw["usage"]
    if not ids or len(ids) != len(logs) or not all(math.isfinite(value["logprob"]) for value in logs):
        raise ValueError("token/logprob identity")
    if usage["prompt_tokens"] != len(body["token_ids"]) or usage["completion_tokens"] != len(ids):
        raise ValueError("native prompt/output usage")
    if not isinstance(raw.get("request_id"), str) or not raw["request_id"]:
        raise ValueError("provider request identity")
    if choice["finish_reason"] not in ("stop", "length", "tool_calls"):
        raise ValueError("unverified finish reason")
    parsed = renderer.parse_response(ids)
    return {"content": parsed.content, "tool_calls": bool(parsed.tool_calls) or choice["finish_reason"] == "tool_calls", "finish_reason": choice["finish_reason"], "completion_ids": ids, "provider_request_id": raw["request_id"]}
