import json


def test_plan_is_balanced_paired_96():
    import protocol as p

    rows = p.plan()
    assert len(rows) == len({row["id"] for row in rows}) == 96
    for ci in range(8):
        block = [row for row in rows if row["context_index"] == ci]
        assert len(block) == 12
        assert {row["arm"] for row in block} == set(p.ARMS)
        assert {row["seed"] for row in block} == {996217101 + ci}


def test_input_row_is_only_record_change():
    import protocol as p

    context = p.contexts()[0]
    for relation in p.RELATIONS:
        absent = p.visible_records(context, relation, False)
        present = p.visible_records(context, relation, True)
        assert len(absent) == len(present) == 48
        for index, (left, right) in enumerate(zip(absent, present, strict=True)):
            assert right["row"] == index
            assert {key: value for key, value in right.items() if key != "row"} == left


def test_output_contracts_are_whole_ordered_and_never_repair():
    import protocol as p
    import scoring

    context = p.contexts()[0]
    labels = [record["gold_label"] for record in context["records"]]
    good_labels = scoring.score({"content": json.dumps(labels)}, context, "aligned_absent_labels_only")
    assert good_labels["available"] and good_labels["contract_valid"]
    assert good_labels["strict_correct"] == 48
    good_rows = [dict(row=i, label=label) for i, label in enumerate(labels)]
    good = scoring.score({"content": json.dumps(good_rows)}, context, "aligned_present_row_first")
    assert good["contract_valid"] and good["row_position_matches"] == 48
    reversed_fields = [dict(reversed(list(value.items()))) for value in good_rows]
    assert scoring.score({"content": json.dumps(reversed_fields)}, context, "aligned_present_row_first")["strict_correct"] == 0
    wrong_row = [dict(value) for value in good_rows]
    wrong_row[17]["row"] = 16
    assert scoring.score({"content": json.dumps(wrong_row)}, context, "aligned_present_row_first")["strict_correct"] == 0
    assert scoring.score({"content": json.dumps(labels[:-1])}, context, "aligned_absent_labels_only")["strict_correct"] == 0


def test_primary_summary_is_absent_input_late_anchor_effect():
    import protocol as p
    import scoring

    rows = []
    for coordinate in p.plan():
        score = scoring.missing(p.contexts()[coordinate["context_index"]])
        score.update(available=True, strict_correct=0, strict_bounds=[0, 0], late_correct=0, early_correct=0)
        if coordinate["input_row"] == "absent" and coordinate["output"] == "row_first":
            score.update(strict_correct=32, late_correct=32)
        rows.append({"coordinate": coordinate, "score": score})
    summary = scoring.summarize(rows)
    assert summary["primary"]["late_output_anchor_effect_absent_input_correct"] == 768
    assert summary["primary"]["planned_late_labels"] == 768
    assert summary["primary"]["positive_contexts"] == 8
