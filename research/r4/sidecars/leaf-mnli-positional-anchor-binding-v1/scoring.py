"""Whole-contract positional scoring without reordering or partial salvage."""

import json
from collections import defaultdict

import protocol as p
import study as s


native = s.load(
    "position_anchor_native_auth",
    s.SIDE / "leaf-role-tool-contract-v1/scoring_v2.py",
    "8028956dfe19b05097b5cd0f80b64c1a5b8f966885d0704dbfb7dc5d3dee0236",
    {"study": s},
)
verified_response = native.verified_response


def missing(context):
    return {"available": False, "strict_correct": None, "strict_bounds": [0, len(context["records"])], "contract_valid": None, "shape_valid": None, "row_position_matches": None, "early_correct": None, "late_correct": None, "predictions": None, "reason": "unavailable"}


def unique(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate object key")
        value[key] = item
    return value


def score(message, context, arm):
    result = {**missing(context), "available": True, "strict_correct": 0, "strict_bounds": [0, 0], "contract_valid": False, "shape_valid": False, "reason": "whole_contract_failure"}
    if message.get("tool_calls"):
        return {**result, "reason": "wrong_route_no_execution"}
    _, _, output = p.parts(arm)
    try:
        values = json.loads(message.get("content"), object_pairs_hook=unique, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
        if not isinstance(values, list) or len(values) != 48:
            raise ValueError("incomplete array")
        if output == "labels_only":
            if any(type(value) is not str or value not in p.LABELS for value in values):
                raise ValueError("noncanonical label array")
            labels = values
            row_matches = None
        else:
            shape = all(isinstance(value, dict) and list(value) == ["row", "label"] and type(value["row"]) is int and type(value["label"]) is str and value["label"] in p.LABELS for value in values)
            result["shape_valid"] = bool(shape)
            row_matches = sum(isinstance(value, dict) and value.get("row") == index for index, value in enumerate(values))
            result["row_position_matches"] = row_matches
            if not shape or row_matches != 48:
                raise ValueError("ordered row contract")
            labels = [value["label"] for value in values]
        gold = [record["gold_label"] for record in context["records"]]
        correct = [left == right for left, right in zip(labels, gold, strict=True)]
        result.update(contract_valid=True, shape_valid=True, strict_correct=sum(correct), strict_bounds=[sum(correct), sum(correct)], early_correct=sum(correct[:16]), late_correct=sum(correct[16:]), predictions=labels, row_position_matches=row_matches, reason="strict_contract")
    except (ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
        result["reason"] = str(error)
    return result


def summarize(rows):
    cells = {}
    for arm in p.ARMS:
        values = [row for row in rows if row["coordinate"]["arm"] == arm]
        available = [row for row in values if row["score"]["available"]]
        cells[arm] = {"planned": len(values), "available": len(available), "null": len(values) - len(available), "strict_correct": sum(row["score"]["strict_correct"] for row in available), "early_correct": sum(row["score"]["early_correct"] or 0 for row in available), "late_correct": sum(row["score"]["late_correct"] or 0 for row in available), "contract_valid": sum(bool(row["score"]["contract_valid"]) for row in available)}
    by_context = defaultdict(lambda: {"row_first": 0, "labels_only": 0})
    available = {"row_first": 0, "labels_only": 0}
    for row in rows:
        c = row["coordinate"]
        if c["input_row"] != "absent" or not row["score"]["available"]:
            continue
        by_context[c["context_index"]][c["output"]] += row["score"]["late_correct"] or 0
        available[c["output"]] += 1
    differences = {str(context): value["row_first"] - value["labels_only"] for context, value in sorted(by_context.items())}
    primary = {"late_output_anchor_effect_absent_input_correct": sum(differences.values()), "planned_late_labels": 8 * 3 * 32, "context_differences": differences, "positive_contexts": sum(value > 0 for value in differences.values()), "row_first_available_calls": available["row_first"], "labels_only_available_calls": available["labels_only"], "availability_difference": available["row_first"] - available["labels_only"]}
    return {"cells": cells, "primary": primary, "cluster_unit": "eight exposed paired contexts; labels and arms within context are dependent"}
