import json

import scoring_v2


def matching_gold():
    return {
        "arm": "matching",
        "labels": ["a", "b"],
        "records": [
            {"id": "x1", "gold_label": "a"},
            {"id": "x2", "gold_label": "b"},
        ],
    }


def test_wrong_ids_keep_positional_diagnostic_but_zero_contract_primary():
    score = scoring_v2.score_content(
        json.dumps([{"tag": "x2", "label": "a"}, {"tag": "x1", "label": "b"}]),
        matching_gold(),
    )

    assert score["full_shape_valid"] is True
    assert score["strict_correct_planned_denominator"] == 2
    assert score["full_contract_valid"] is False
    assert score["contract_valid_correct_planned_denominator"] == 0


def test_wrong_field_order_is_separate_and_invalidates_ordered_contract():
    score = scoring_v2.score_content(
        '[{"label":"a","tag":"x1"},{"tag":"x2","label":"b"}]',
        matching_gold(),
    )

    assert score["emitted_id_position_matches"] == 2
    assert score["field_order_valid"] is False
    assert score["full_contract_valid"] is False
    assert score["contract_valid_correct_planned_denominator"] == 0


def test_matching_contract_and_missing_bounds_are_conservative():
    valid = scoring_v2.score_content(
        '[{"tag":"x1","label":"a"},{"tag":"x2","label":"b"}]',
        matching_gold(),
    )
    missing = scoring_v2.score_missing(matching_gold())

    assert valid["full_contract_valid"] is True
    assert valid["contract_valid_correct_planned_denominator"] == 2
    assert missing["full_contract_valid"] is None
    assert missing["contract_valid_correct_planned_denominator"] is None
    assert missing["contract_valid_correct_bounds"] == [0, 2]

