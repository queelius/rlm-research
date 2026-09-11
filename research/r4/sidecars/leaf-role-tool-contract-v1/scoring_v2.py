"""Authenticate native completion envelopes before admitting policy scores."""

import json
import re
from copy import deepcopy

import study as s


def verified_response(raw, expected_prompt_ids, tokenizer):
    if raw.get("model") != s.MODEL["alias"] or len(raw.get("choices", [])) != 1:
        raise ValueError("actual model or unique assistant choice differs")
    choice = raw["choices"][0]
    if choice.get("index") not in (None, 0):
        raise ValueError("assistant choice index differs")
    message = choice.get("message") or {}
    incoming = raw.get("prompt_token_ids")
    outgoing = choice.get("token_ids")
    usage = raw.get("usage") or {}
    if incoming != expected_prompt_ids:
        raise ValueError("actual native prompt token identity unavailable or different")
    if not isinstance(outgoing, list) or any(type(token) is not int for token in outgoing):
        raise ValueError("actual native completion token identity unavailable")
    if type(usage.get("prompt_tokens")) is not int or usage["prompt_tokens"] != len(incoming):
        raise ValueError("native prompt usage disagrees")
    if type(usage.get("completion_tokens")) is not int or usage["completion_tokens"] != len(outgoing):
        raise ValueError("native completion usage disagrees")
    total = usage.get("total_tokens")
    if total is not None and (type(total) is not int or total != len(incoming) + len(outgoing)):
        raise ValueError("native total usage disagrees")
    finish = choice.get("finish_reason")
    if message.get("role") != "assistant" or finish not in ("stop", "length", "tool_calls"):
        raise ValueError("unverified returned assistant finish branch")
    if message.get("reasoning") or message.get("reasoning_content") or message.get("function_call"):
        raise ValueError("unverified auxiliary assistant branch")

    tools = message.get("tool_calls") or []
    if tools:
        if finish != "tool_calls":
            raise ValueError("parsed tools disagree with finish branch")
        terminal_ids = {value for value in (getattr(tokenizer, "eos_token_id", None), 151645, 151643)
                        if value is not None}
        content_ids = outgoing[:-1] if outgoing and outgoing[-1] in terminal_ids else outgoing
        decoded = tokenizer.decode(content_ids, skip_special_tokens=False,
                                   clean_up_tokenization_spaces=False)
        spans = list(re.finditer(r"<tool_call>\s*(.*?)\s*</tool_call>", decoded, re.S))
        if len(spans) != len(tools):
            raise ValueError("native tool-envelope count differs")
        remaining = []
        cursor = 0
        for match, tool in zip(spans, tools, strict=True):
            envelope = json.loads(match[1])
            function = tool.get("function") or {}
            arguments = function.get("arguments")
            arguments = json.loads(arguments) if isinstance(arguments, str) else arguments
            if envelope != {"name": function.get("name"), "arguments": arguments}:
                raise ValueError("native tool-envelope function or arguments differ")
            remaining.append(decoded[cursor:match.start()])
            cursor = match.end()
        remaining.append(decoded[cursor:])
        if "".join(remaining).strip() != (message.get("content") or "").strip():
            raise ValueError("native tool-envelope surrounding text differs")
        return deepcopy(message), finish, usage

    if finish == "tool_calls":
        raise ValueError("tool finish branch has no authenticated parsed tool")
    decoded = tokenizer.decode(outgoing, skip_special_tokens=True,
                               clean_up_tokenization_spaces=False)
    if not isinstance(message.get("content"), str) or decoded != message["content"]:
        raise ValueError("native completion text differs")
    if message.get("tool_calls"):
        raise ValueError("unexpected tool branch")
    return deepcopy(message), finish, usage


def summarize(design, records):
    normalized = []
    for record in records:
        item = deepcopy(record)
        if item.get("score") is None:
            row = item["coordinate"]
            gold = design["batches"][row["batch_id"]]["gold"]
            item["score"] = s.score_missing(gold)
        normalized.append(item)
    result = s.summarize(design, normalized)
    result["schema"] = "leaf-role-tool-contract-analysis-v2"
    by_id = {record["coordinate"]["id"]: record for record in normalized}
    for cell in result["cells"]:
        selected = [record for record in normalized if
                    (record["coordinate"]["system_role"], record["coordinate"]["tools"],
                     record["coordinate"]["arm"], record["coordinate"]["decoder"],
                     record["coordinate"]["dataset"]) ==
                    (cell["system_role"], cell["tools"], cell["arm"], cell["decoder"],
                     cell["dataset"])]
        cell["physical_records"] = len(selected)
        cell["available_native_verified"] = sum(
            record["score"]["strict_correct_planned_denominator"] is not None for record in selected)
        cell["infrastructure_nulls"] = cell["planned"] - cell["available_native_verified"]
    result["physical_records"] = len(normalized)
    result["native_verified"] = sum(record.get("native_verified") is True for record in normalized)
    result["planned_nulls"] = len(design["plan"]) - result["native_verified"]
    return result

