"""Selection, exclusion and exact request-wire fixtures."""

import prepare


def test_balanced_outcome_blind_selection_and_no_exposure_overlap():
    bundle = prepare.make_inputs()
    records = bundle["public"]["records"]
    assert len(records) == 512
    assert bundle["audit"]["selection_used_model_outcomes"] is False
    assert bundle["audit"]["selected_per_label"] == {0: 128, 1: 128, 2: 128, 3: 128}
    assert bundle["audit"]["selected_source_id_overlap"] == 0
    assert bundle["audit"]["selected_normalized_overlap"] == 0
    assert bundle["audit"]["selected_duplicate_group_members"] == 0


def test_exact_b4_temperature_zero_wire_and_ordered_schema():
    bundle = prepare.make_inputs()
    requests = bundle["requests"]
    assert len(requests) == 128
    assert all(len(row["ids"]) == 4 for row in requests)
    assert all(row["body_template"]["sampling_params"]["temperature"] == 0 for row in requests)
    assert all(
        list(__import__("json").loads(row["schema_ordered_json"])["properties"]) == row["ids"]
        for row in requests
    )
    assert [key for row in requests for key in row["ids"]] == [
        row["id"] for row in bundle["public"]["records"]
    ]
