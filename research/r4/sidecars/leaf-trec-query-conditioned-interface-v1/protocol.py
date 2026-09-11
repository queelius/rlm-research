"""Strict full-six and A/B/other contracts with common projected scoring."""

import json
import math


CATEGORIES = (
    "human being",
    "location",
    "abbreviation",
    "entity",
    "description and abstract concept",
    "numeric value",
)
PROJECTED = ("A", "B", "other")


def unique(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate map ID")
        value[key] = item
    return value


def project(label, pair):
    return "A" if label == pair[0] else "B" if label == pair[1] else "other"


def score(content, ids, gold, pair, interface, authenticated, tool_calls=False):
    result = {
        "available": bool(authenticated),
        "complete_map": False,
        "strict_correct": None if not authenticated else 0,
        "exact_batch": None if not authenticated else False,
        "labels": None,
        "projected": None,
        "confusion": None,
        "output_order_equal": None,
        "invalid_reason": None,
    }
    if not authenticated:
        return result
    try:
        if tool_calls:
            raise ValueError("wrong tool route; no execution")
        labels = json.loads(content, object_pairs_hook=unique)
        if not isinstance(labels, dict):
            raise ValueError("not a JSON object")
        allowed = CATEGORIES if interface == "full6" else PROJECTED if interface == "abo" else ()
        if set(labels) != set(ids) or len(ids) != len(set(ids)):
            raise ValueError("incomplete or extra map")
        if any(not isinstance(value, str) or value not in allowed for value in labels.values()):
            raise ValueError("noncanonical label")
        projected = {key: project(value, pair) if interface == "full6" else value for key, value in labels.items()}
        projected_gold = {key: project(gold[key], pair) for key in ids}
        correct = sum(projected[key] == projected_gold[key] for key in ids)
        confusion = {}
        for label in PROJECTED:
            confusion[label] = {
                "tp": sum(projected[key] == label and projected_gold[key] == label for key in ids),
                "fp": sum(projected[key] == label and projected_gold[key] != label for key in ids),
                "fn": sum(projected[key] != label and projected_gold[key] == label for key in ids),
            }
        result.update(
            complete_map=True,
            strict_correct=correct,
            exact_batch=correct == len(ids),
            labels=labels,
            projected=projected,
            confusion=confusion,
            output_order_equal=list(labels) == ids,
        )
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
    if not ids or len(ids) != len(logs) or not all(math.isfinite(item["logprob"]) for item in logs):
        raise ValueError("token/logprob identity")
    if usage["prompt_tokens"] != len(body["token_ids"]) or usage["completion_tokens"] != len(ids):
        raise ValueError("native prompt/output usage")
    if not isinstance(raw.get("request_id"), str) or not raw["request_id"]:
        raise ValueError("provider request identity")
    if choice["finish_reason"] not in ("stop", "length", "tool_calls"):
        raise ValueError("unverified finish reason")
    parsed = renderer.parse_response(ids)
    return {
        "content": parsed.content,
        "tool_calls": bool(parsed.tool_calls) or choice["finish_reason"] == "tool_calls",
        "finish_reason": choice["finish_reason"],
        "completion_ids": ids,
        "provider_request_id": raw["request_id"],
    }
