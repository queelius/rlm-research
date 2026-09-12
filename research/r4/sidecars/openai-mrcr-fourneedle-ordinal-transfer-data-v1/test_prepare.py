import prepare as p


def test_balanced_selection_is_short_disjoint_and_outcome_blind():
    value = p.select()
    assert value["eligible_counts"]["3"] >= 8
    assert value["eligible_counts"]["4"] >= 8
    assert [sum(row["target_occurrence_one_indexed"] == ordinal for row in value["selected"]) for ordinal in (3, 4)] == [8, 8]
    assert all(row["o200k_prompt_plus_answer"] <= 8192 for row in value["selected"])
    assert not value["selected_conflicts"]
    assert value["selection_uses_model_answers"] is False
    assert value["selection_uses_previous_outcomes"] is False


def test_selected_rows_retain_official_four_needle_request_semantics():
    value = p.select()
    assert all(row["n_needles"] == 4 for row in value["selected"])
    assert {row["target_occurrence_one_indexed"] for row in value["selected"]} == {3, 4}
    assert all(row["official_question_exact"] for row in value["selected"])
