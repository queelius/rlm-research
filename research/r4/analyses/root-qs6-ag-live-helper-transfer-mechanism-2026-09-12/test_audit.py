import audit


def test_static_scope_and_host_reduction_without_execution():
    records = [
        {"id": "a", "user": "u0", "weight": 4},
        {"id": "b", "user": "u2", "weight": 7},
    ]
    labels = {"a": "World", "b": "World"}
    code = (
        "matches = [record for record in records "
        "if record['user'] in ['u0', 'u1'] and labels[record['id']] == 'World']\n"
        "answer = len(matches)"
    )
    result = audit.inspect_reducer(code, "count", "World", records, labels)
    assert result == {
        "ast_valid": True,
        "has_print": False,
        "supported": True,
        "users": ["u0", "u1"],
        "host_value_for_generated_scope": 1,
        "host_value_for_question_scope": 2,
        "scope_matches_question": False,
    }


def test_weight_sum_and_unsupported_code():
    records = [{"id": "a", "user": "u0", "weight": 4}]
    labels = {"a": "Business"}
    code = (
        "matches = [record for record in records if labels[record['id']] == 'Business']\n"
        "answer = sum(record['weight'] for record in matches)\nprint(answer)"
    )
    got = audit.inspect_reducer(code, "weight_sum", "Business", records, labels)
    assert got["supported"] and got["has_print"]
    assert got["host_value_for_generated_scope"] == 4
    assert audit.inspect_reducer("x = await rlm('q')", "count", "World", records, labels)[
        "supported"
    ] is False
