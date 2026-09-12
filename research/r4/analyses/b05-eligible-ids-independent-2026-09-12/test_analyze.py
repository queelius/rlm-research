import analyze


def test_all_record_projection_retains_invalid_metadata_ids():
    text = '{"row_count":1,"rows":[{"implementation_id":"a","features":["z","a"]}]}'
    value = analyze.project_ids(text, "full_report")
    assert value["ids"] == ["a"]
    assert value["metadata_rows"][0]["features"] == ["z", "a"]


def test_id_metric_denominator_includes_missing_predictions():
    value = analyze.id_metric([], {"a", "b"})
    assert value["true_positive"] == 0
    assert value["false_negative"] == 2
    assert value["precision"] is None
    assert value["recall"] == 0.0


def test_host_lookup_does_not_filter_known_ineligible_id():
    study, interface = analyze.modules()
    candidates = []
    for root in study.active_roots():
        for child in root["safe_children"]:
            receipt = interface.reference().child_reference_receipt(child)
            candidates.extend(
                (child, row) for row in receipt["derivations"] if not row["eligible"]
            )
    child, rejected = candidates[0]
    identifier = rejected["implementation_id"]
    looked_up = interface.lookup([identifier], child)
    assert looked_up["row_count"] == 1
    assert looked_up["rows"][0]["implementation_id"] == identifier
