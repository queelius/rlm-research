import json
from collections import Counter

import study


def test_factorial_has_exact_paired_96_call_shape():
    design = study.build_design(study.build_data())

    assert len(design["plan"]) == 96
    assert Counter((r["dataset"], r["arm"], r["decoder"]) for r in design["plan"]) == {
        (task, arm, decoder): 8
        for task in ("agnews", "sst2")
        for arm in ("matching", "constant", "plain")
        for decoder in ("free", "exact")
    }
    groups = {}
    for row in design["plan"]:
        key = (row["dataset"], row["context_index"], row["arm"], row["seed"])
        groups.setdefault(key, {})[row["decoder"]] = study.make_request(design, row)
    assert len(groups) == 48
    for pair in groups.values():
        free = pair["free"]
        exact = pair["exact"]
        assert "structured_outputs" not in free
        assert {k: v for k, v in exact.items() if k != "structured_outputs"} == free


def test_completed_malformed_is_observed_zero_while_missing_is_null():
    gold = {
        "arm": "plain",
        "labels": ["a", "b"],
        "records": [
            {"id": "x1", "gold_label": "a"},
            {"id": "x2", "gold_label": "b"},
        ],
    }

    malformed = study.score_content("not json", gold)
    missing = study.score_missing(gold)

    assert malformed["observed_policy_output"] is True
    assert malformed["strict_correct_planned_denominator"] == 0
    assert malformed["conditional_correct"] is None
    assert missing["observed_policy_output"] is False
    assert missing["strict_correct_planned_denominator"] is None
    assert missing["planned_correct_bounds"] == [0, 2]


def test_wrong_ids_do_not_reorder_or_erase_positional_labels():
    gold = {
        "arm": "matching",
        "labels": ["a", "b"],
        "records": [
            {"id": "x1", "gold_label": "a"},
            {"id": "x2", "gold_label": "b"},
        ],
    }
    content = json.dumps(
        [
            {"tag": "x2", "label": "a"},
            {"label": "b", "tag": "x1"},
        ]
    )

    score = study.score_content(content, gold)

    assert score["full_shape_valid"] is True
    assert score["strict_correct_planned_denominator"] == 2
    assert score["emitted_id_position_matches"] == 0
    assert score["emitted_id_set_coverage"] == 2
    assert score["duplicate_emitted_ids"] == []
    assert score["field_order_valid"] is False
    assert score["predictions"] == ["a", "b"]


def test_duplicate_and_omitted_ids_remain_separate_diagnostics():
    gold = {
        "arm": "matching",
        "labels": ["a", "b"],
        "records": [
            {"id": "x1", "gold_label": "a"},
            {"id": "x2", "gold_label": "b"},
        ],
    }
    score = study.score_content(
        json.dumps([{"tag": "x1", "label": "a"}, {"tag": "x1", "label": "b"}]),
        gold,
    )

    assert score["strict_correct_planned_denominator"] == 2
    assert score["duplicate_emitted_ids"] == ["x1"]
    assert score["missing_input_ids"] == ["x2"]
    assert score["extra_emitted_ids"] == []

