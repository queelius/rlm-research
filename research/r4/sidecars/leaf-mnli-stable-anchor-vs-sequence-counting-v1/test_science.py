import json

import protocol as p
import scoring

from test_protocol import fake_context


def scored_row(context_index, relation, anchor, late):
    row = {
        "context_index": context_index,
        "relation": relation,
        "anchor": anchor,
        "arm": f"{relation}_{anchor}",
    }
    return {
        "coordinate": row,
        "physical_attempt": True,
        "usage_observed": None,
        "score": {
            "available": True,
            "strict_correct": late,
            "early_correct": 0,
            "late_correct": late,
            "contract_valid": True,
            "key_position_matches": None if anchor == "labels_only" else 48,
        },
    }


def unavailable_row(context_index, relation, anchor):
    row = scored_row(context_index, relation, anchor, 0)
    row["score"] = scoring.missing(fake_context())
    return row


def test_whole_contract_rejects_wrong_key_without_partial_salvage():
    context = fake_context()
    keys = p.anchor_values(context, "opaque")
    values = [{"key": key, "label": "neutral"} for key in keys]
    values[19]["key"] = "kffffffffffff"
    result = scoring.score({"content": json.dumps(values), "tool_calls": []}, context, "opaque")
    assert result["available"] and not result["contract_valid"]
    assert result["strict_correct"] == 0 and result["predictions"] is None
    assert result["key_position_matches"] == 47


def test_observed_invalid_is_known_wrong_but_unavailable_remains_unknown():
    context = fake_context()
    observed = scoring.score({"content": "not json", "tool_calls": []}, context, "opaque")
    unavailable = scoring.missing(context)
    assert observed["available"] and observed["strict_correct"] == 0
    assert observed["early_correct"] == 0 and observed["late_correct"] == 0
    assert not unavailable["available"] and unavailable["strict_correct"] is None
    assert unavailable["early_correct"] is None and unavailable["late_correct"] is None


def test_summary_keeps_pooled_descriptive_but_gates_opaque_alone():
    rows = []
    late = {"labels_only": 0, "sequential_numeric": 30, "permuted_numeric": 30, "opaque": 8}
    for context_index in range(16):
        for relation in p.RELATIONS:
            for anchor in p.ANCHORS:
                rows.append(scored_row(context_index, relation, anchor, late[anchor]))
    summary = scoring.summarize(rows)
    assert summary["primary_descriptive"]["pooled_paired_known_stable_gain_pp"] > 25
    assert summary["opaque_downstream_gate"]["paired_known_gain_pp"] == 25
    assert not summary["opaque_downstream_gate"]["promote"]
    assert summary["permuted_numeric_gate"]["promote"]
    assert summary["forced_grammar_caveat"]


def test_missing_labels_baseline_is_unknown_not_a_zero_baseline():
    rows = []
    for context_index in range(16):
        for relation in p.RELATIONS:
            for anchor in p.ANCHORS:
                rows.append(scored_row(context_index, relation, anchor, 8 if anchor != "labels_only" else 0))
    missing_index = next(
        index for index, row in enumerate(rows)
        if row["coordinate"]["context_index"] == 0
        and row["coordinate"]["relation"] == "wrong"
        and row["coordinate"]["anchor"] == "labels_only"
    )
    rows[missing_index] = unavailable_row(0, "wrong", "labels_only")
    summary = scoring.summarize(rows)
    opaque = summary["opaque_downstream_gate"]
    assert opaque["paired_known_pairs"] == 47
    assert opaque["paired_known_gain_correct"] == 47 * 8
    assert opaque["planned_gain_correct_bounds"] == [47 * 8 - 24, 48 * 8]
    assert opaque["planned_gain_pp_bounds"][0] < 25
    assert opaque["relative_to_sequential_pp_bounds"] == [0, 0]
    assert not opaque["promote"]


def test_missing_keyed_treatment_is_unknown_not_a_zero_treatment():
    rows = []
    for context_index in range(16):
        for relation in p.RELATIONS:
            for anchor in p.ANCHORS:
                rows.append(scored_row(context_index, relation, anchor, 8 if anchor != "labels_only" else 0))
    missing_index = next(
        index for index, row in enumerate(rows)
        if row["coordinate"]["context_index"] == 0
        and row["coordinate"]["relation"] == "wrong"
        and row["coordinate"]["anchor"] == "opaque"
    )
    rows[missing_index] = unavailable_row(0, "wrong", "opaque")
    summary = scoring.summarize(rows)
    opaque = summary["opaque_downstream_gate"]
    assert opaque["paired_known_pairs"] == 47
    assert opaque["paired_known_gain_correct"] == 47 * 8
    assert opaque["planned_gain_correct_bounds"] == [47 * 8, 47 * 8 + 32]
    assert opaque["planned_gain_pp_bounds"][1] > 25
    assert not opaque["promote"]
