import protocol as p


def test_j1_reducer_uses_only_predicted_labels_and_public_records():
    records = [
        {"id": "a", "user": "u0", "weight": 7},
        {"id": "b", "user": "u0", "weight": 3},
        {"id": "c", "user": "u1", "weight": 5},
    ]
    labels = {"a": "human being", "b": "location", "c": "location"}
    result = p.reduce_j1(records, labels, {"target": "human being", "target_b": "location",
                                           "users": ["u0", "u1"]})
    assert result["answer"] == 3
    assert result["qualifying_users"] == ["u0"]
    assert result["contributions"] == {"a": 0, "b": 3, "c": 0}


def test_map_contract_never_salvages_incomplete_output():
    score = p.score('{"a":"location"}', ["a", "b"], {"a": "location", "b": "entity"}, True)
    assert score["available"] and not score["complete_map"] and score["strict_correct"] == 0
    assert score["labels"] is None
