import json

import protocol as p


def sample_context():
    labels = ("entailment", "neutral", "contradiction")
    records = [
        {"id": f"r{i:02d}", "premise": f"p{i}", "hypothesis": f"h{i}",
         "user": ("Ada", "Ben", "Cy", "Dee")[i % 4], "weight": 1 + i % 9,
         "gold_label": labels[i % 3]}
        for i in range(48)
    ]
    return {"id": "ctx0", "index": 0, "genre": "government", "records": records}


def test_leaf_requests_have_same_seed_and_distinct_hidden_keys():
    context = sample_context()
    sequential = p.leaf_request(context, "sequential_numeric")
    opaque = p.leaf_request(context, "opaque")
    assert sequential["seed"] == opaque["seed"] == 998431101
    seq_input = json.loads(sequential["messages"][1]["content"].split("Input records:\n", 1)[1])
    opaque_input = json.loads(opaque["messages"][1]["content"].split("Input records:\n", 1)[1])
    assert [row["id"] for row in seq_input] == [row["id"] for row in opaque_input]
    assert [row["key"] for row in seq_input] == list(range(48))
    assert all(str(row["key"]).startswith("k") for row in opaque_input)


def test_broker_normalizes_both_encodings_to_same_public_contract():
    context = sample_context()
    labels = [row["gold_label"] for row in context["records"]]
    sequential = [{"key": i, "label": label} for i, label in enumerate(labels)]
    opaque = [
        {"key": key, "label": label}
        for key, label in zip(p.anchor_values(context, "opaque"), labels, strict=True)
    ]
    left = p.broker(json.dumps(sequential), context, "sequential_numeric")
    right = p.broker(json.dumps(opaque), context, "opaque")
    assert left == right == {row["id"]: row["gold_label"] for row in context["records"]}


def test_broker_rejects_missing_key_without_partial_salvage():
    context = sample_context()
    values = [{"key": i, "label": "neutral"} for i in range(47)]
    try:
        p.broker(json.dumps(values), context, "sequential_numeric")
    except ValueError as error:
        assert "48" in str(error)
    else:
        raise AssertionError("missing key accepted")


def test_root_plan_is_exact64_and_pair_seeds_match():
    contexts = [sample_context() | {"id": f"ctx{i}", "index": i} for i in range(8)]
    plan = p.root_plan(contexts)
    assert len(plan) == 64
    for i in range(0, 64, 4):
        block = plan[i:i + 4]
        assert len({row["seed"] for row in block}) == 1
        assert {(row["encoding"], row["policy"]) for row in block} == {
            ("sequential_numeric", "supplied"), ("opaque", "supplied"),
            ("sequential_numeric", "free"), ("opaque", "free"),
        }


def test_reducers_are_varied_and_use_public_metadata():
    context = sample_context()
    labels = {row["id"]: row["gold_label"] for row in context["records"]}
    count = p.reduce_answer(context, labels, {"operator": "count", "relation": "entailment", "users": ["Ada"]})
    weight = p.reduce_answer(context, labels, {"operator": "weight", "relation": "entailment", "users": ["Ada"]})
    assert count == 4
    assert weight == sum(row["weight"] for row in context["records"] if row["user"] == "Ada" and row["gold_label"] == "entailment")
