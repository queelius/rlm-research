import collections

import prepare


def test_selection_is_balanced_disjoint_and_outcome_blind():
    value = prepare.select()
    assert len(value["selected"]) == 32
    assert collections.Counter(row["requested_ordinal"] for row in value["selected"]) == {
        1: 8,
        2: 8,
        3: 8,
        4: 8,
    }
    assert value["explicit_exposed_rows"] == 88
    assert value["selection_uses_model_answers"] is False
    assert value["selection_uses_previous_outcomes"] is False


def test_selected_answers_and_source_rows_fit_frozen_caps():
    value = prepare.select()
    assert all(row["o200k_prompt_plus_answer"] <= 8192 for row in value["selected"])
    assert all(row["answer_qwen_tokens"] <= 2048 for row in value["selected"])
    assert len({row["row_sha256"] for row in value["selected"]}) == 32
