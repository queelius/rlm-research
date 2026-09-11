"""Whole-contract native scoring and frozen clustered summaries."""

import json

import protocol as p
import study as s


native = s.load(
    "stable_anchor_native_auth",
    s.SIDE / "leaf-role-tool-contract-v1/scoring_v2.py",
    "8028956dfe19b05097b5cd0f80b64c1a5b8f966885d0704dbfb7dc5d3dee0236",
    {"study": s},
)
verified_response = native.verified_response


def missing(context):
    return {
        "available": False,
        "strict_correct": None,
        "strict_bounds": [0, len(context["records"])],
        "contract_valid": None,
        "shape_valid": None,
        "key_position_matches": None,
        "early_correct": None,
        "late_correct": None,
        "predictions": None,
        "reason": "unavailable",
    }


def unique(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate object key")
        value[key] = item
    return value


def anchor_from_arm(arm):
    if arm in p.ANCHORS:
        return arm
    for anchor in p.ANCHORS:
        if arm.endswith("_" + anchor):
            return anchor
    raise ValueError(arm)


def score(message, context, arm):
    result = {
        **missing(context),
        "available": True,
        "strict_correct": 0,
        "strict_bounds": [0, 0],
        "early_correct": 0,
        "late_correct": 0,
        "contract_valid": False,
        "shape_valid": False,
        "reason": "whole_contract_failure",
    }
    if message.get("tool_calls"):
        return {**result, "reason": "wrong_route_no_execution"}
    anchor = anchor_from_arm(arm)
    try:
        values = json.loads(
            message.get("content"),
            object_pairs_hook=unique,
            parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
        )
        if not isinstance(values, list) or len(values) != 48:
            raise ValueError("incomplete array")
        if anchor == "labels_only":
            if any(type(value) is not str or value not in p.LABELS for value in values):
                raise ValueError("noncanonical label array")
            labels = values
            key_matches = None
        else:
            expected = p.anchor_values(context, anchor)
            shape = all(
                isinstance(value, dict)
                and list(value) == ["key", "label"]
                and type(value["key"]) is type(expected[index])
                and type(value["label"]) is str
                and value["label"] in p.LABELS
                for index, value in enumerate(values)
            )
            result["shape_valid"] = bool(shape)
            key_matches = sum(
                isinstance(value, dict) and value.get("key") == expected[index]
                for index, value in enumerate(values)
            )
            result["key_position_matches"] = key_matches
            if not shape or key_matches != 48:
                raise ValueError("ordered key contract")
            labels = [value["label"] for value in values]
        gold = [record["gold_label"] for record in context["records"]]
        correct = [left == right for left, right in zip(labels, gold, strict=True)]
        total = sum(correct)
        result.update(
            contract_valid=True,
            shape_valid=True,
            strict_correct=total,
            strict_bounds=[total, total],
            early_correct=sum(correct[:16]),
            late_correct=sum(correct[16:]),
            predictions=labels,
            key_position_matches=key_matches,
            reason="strict_contract",
        )
    except (ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
        result["reason"] = str(error)
    return result


def summarize(rows):
    cells = {}
    for arm in p.ARMS:
        values = [row for row in rows if row["coordinate"]["arm"] == arm]
        available = [row for row in values if row["score"]["available"]]
        cells[arm] = {
            "planned": len(values),
            "available": len(available),
            "null": len(values) - len(available),
            "strict_correct": sum(row["score"]["strict_correct"] for row in available),
            "early_correct": sum(row["score"]["early_correct"] or 0 for row in available),
            "late_correct": sum(row["score"]["late_correct"] or 0 for row in available),
            "contract_valid": sum(bool(row["score"]["contract_valid"]) for row in available),
            "key_position_matches": sum(row["score"].get("key_position_matches") or 0 for row in available),
        }

    denominator = 16 * len(p.RELATIONS) * 32
    context_gains = {anchor: {} for anchor in p.ANCHORS[1:]}
    total_gains = {}
    total_bounds = {}
    known_pairs = {}
    for anchor in p.ANCHORS[1:]:
        for context_index in range(16):
            value = 0
            lower = 0
            upper = 0
            pairs = 0
            for relation in p.RELATIONS:
                base_row = next(
                    row for row in rows
                    if row["coordinate"].get("context_index") == context_index
                    and row["coordinate"]["arm"] == f"{relation}_labels_only"
                )
                keyed_row = next(
                    row for row in rows
                    if row["coordinate"].get("context_index") == context_index
                    and row["coordinate"]["arm"] == f"{relation}_{anchor}"
                )
                base = base_row["score"]
                keyed = keyed_row["score"]
                base_known = base.get("available") and type(base.get("late_correct")) is int
                keyed_known = keyed.get("available") and type(keyed.get("late_correct")) is int
                base_bounds = [base["late_correct"], base["late_correct"]] if base_known else [0, 32]
                keyed_bounds = [keyed["late_correct"], keyed["late_correct"]] if keyed_known else [0, 32]
                lower += keyed_bounds[0] - base_bounds[1]
                upper += keyed_bounds[1] - base_bounds[0]
                if base_known and keyed_known:
                    value += keyed["late_correct"] - base["late_correct"]
                    pairs += 1
            context_gains[anchor][str(context_index)] = {
                "paired_known_gain_correct": value,
                "paired_known_pairs": pairs,
                "planned_gain_correct_bounds": [lower, upper],
            }
        total_gains[anchor] = sum(
            value["paired_known_gain_correct"] for value in context_gains[anchor].values()
        )
        known_pairs[anchor] = sum(
            value["paired_known_pairs"] for value in context_gains[anchor].values()
        )
        total_bounds[anchor] = [
            sum(value["planned_gain_correct_bounds"][0] for value in context_gains[anchor].values()),
            sum(value["planned_gain_correct_bounds"][1] for value in context_gains[anchor].values()),
        ]

    gain_pp = {
        anchor: (100 * total_gains[anchor] / (32 * known_pairs[anchor]))
        if known_pairs[anchor] else None
        for anchor in p.ANCHORS[1:]
    }
    gain_pp_bounds = {
        anchor: [100 * value / denominator for value in total_bounds[anchor]]
        for anchor in p.ANCHORS[1:]
    }

    def relative_bounds(left_anchor, right_anchor):
        lower = 0
        upper = 0
        for context_index in range(16):
            for relation in p.RELATIONS:
                selected = {}
                for anchor in (left_anchor, right_anchor):
                    row = next(
                        value for value in rows
                        if value["coordinate"].get("context_index") == context_index
                        and value["coordinate"]["arm"] == f"{relation}_{anchor}"
                    )
                    score = row["score"]
                    known = score.get("available") and type(score.get("late_correct")) is int
                    selected[anchor] = (
                        [score["late_correct"], score["late_correct"]] if known else [0, 32]
                    )
                lower += selected[left_anchor][0] - selected[right_anchor][1]
                upper += selected[left_anchor][1] - selected[right_anchor][0]
        return [100 * lower / denominator, 100 * upper / denominator]

    def gate(anchor):
        cell_available = all(
            cells[f"{relation}_{condition}"]["available"] >= 15
            for relation in p.RELATIONS
            for condition in p.ANCHORS
        )
        no_disadvantage = all(
            cells[f"{relation}_{anchor}"]["available"]
            >= cells[f"{relation}_labels_only"]["available"]
            and cells[f"{relation}_{anchor}"]["contract_valid"]
            >= cells[f"{relation}_labels_only"]["contract_valid"]
            for relation in p.RELATIONS
        )
        positive = sum(
            value["planned_gain_correct_bounds"][0] > 0
            for value in context_gains[anchor].values()
        )
        relative = relative_bounds(anchor, "sequential_numeric")
        return {
            "paired_known_gain_correct": total_gains[anchor],
            "paired_known_pairs": known_pairs[anchor],
            "paired_known_denominator": 32 * known_pairs[anchor],
            "paired_known_gain_pp": gain_pp[anchor],
            "planned_denominator": denominator,
            "planned_gain_correct_bounds": total_bounds[anchor],
            "planned_gain_pp_bounds": gain_pp_bounds[anchor],
            "relative_to_sequential_pp_bounds": relative,
            "lower_bound_within_10pp_of_sequential": relative[0] >= -10,
            "positive_contexts_by_lower_bound": positive,
            "all_cells_at_least_15_available": cell_available,
            "no_contract_or_availability_disadvantage": no_disadvantage,
            "promote": (
                gain_pp_bounds[anchor][0] >= 25
                and relative[0] >= -10
                and positive >= 12
                and cell_available
                and no_disadvantage
            ),
        }

    pooled = (
        (gain_pp["permuted_numeric"] + gain_pp["opaque"]) / 2
        if gain_pp["permuted_numeric"] is not None and gain_pp["opaque"] is not None
        else None
    )
    pooled_bounds = [
        (gain_pp_bounds["permuted_numeric"][index] + gain_pp_bounds["opaque"][index]) / 2
        for index in range(2)
    ]
    permuted_relative = relative_bounds("permuted_numeric", "sequential_numeric")
    opaque_relative = relative_bounds("opaque", "sequential_numeric")
    pooled_retention_bounds = [
        (permuted_relative[index] + opaque_relative[index]) / 2 for index in range(2)
    ]
    return {
        "cells": cells,
        "primary_descriptive": {
            "population": "positions 17 through 48",
            "denominator_per_condition": denominator,
            "paired_known_gain_pp": gain_pp,
            "planned_gain_pp_bounds": gain_pp_bounds,
            "pooled_paired_known_stable_gain_pp": pooled,
            "pooled_planned_stable_gain_pp_bounds": pooled_bounds,
            "pooled_stable_retention_vs_sequential_pp_bounds": pooled_retention_bounds,
            "context_gains": context_gains,
            "bounds_are_missing_outcome_worst_best_not_confidence_intervals": True,
        },
        "opaque_downstream_gate": gate("opaque"),
        "permuted_numeric_gate": gate("permuted_numeric"),
        "forced_grammar_caveat": (
            "Structured decoding forces key-bearing grammar and may supply key continuations; key "
            "fidelity is a contract diagnostic, not proof of freely learned retrieval or copying."
        ),
        "cluster_unit": "16 paired contexts; calls, premise groups, and labels are dependent",
    }
