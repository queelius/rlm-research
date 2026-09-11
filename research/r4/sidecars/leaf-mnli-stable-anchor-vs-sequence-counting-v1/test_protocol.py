import json

import protocol as p
import study as s


def fake_context(index=0):
    return {
        "index": index,
        "records": [
            {
                "id": f"m{i:012x}",
                "premise": f"premise {i}",
                "hypothesis": f"hypothesis {i}",
                "label": i % 3,
            }
            for i in range(48)
        ],
    }


def test_inherited_inventory_scanner_interface_is_complete():
    assert s.BASE == s.PRIOR.parent / "leaf-mnli-correspondence-v1"


def test_exact_192_paired_inventory():
    rows = p.plan()
    assert len(rows) == len({row["id"] for row in rows}) == 192
    assert {row["anchor"] for row in rows} == set(p.ANCHORS)
    for context_index in range(16):
        selected = [row for row in rows if row["context_index"] == context_index]
        assert len(selected) == 12
        assert {row["seed"] for row in selected} == {998317101 + context_index}


def test_stable_anchor_namespaces_and_permutation():
    context = fake_context()
    public = {record["id"] for record in context["records"]}
    sequential = p.anchor_values(context, "sequential_numeric")
    permuted = p.anchor_values(context, "permuted_numeric")
    opaque = p.anchor_values(context, "opaque")
    assert sequential == list(range(48))
    assert sorted(permuted) == list(range(48)) and permuted != sequential
    assert len(set(opaque)) == 48
    assert all(value.startswith("k") and len(value) == 13 for value in opaque)
    assert not (set(opaque) & public)


def test_request_hides_gold_and_schema_forces_exact_displayed_keys():
    context = fake_context()
    for anchor in p.ANCHORS:
        row = next(row for row in p.plan() if row["anchor"] == anchor)
        body = p.request(context, row, [f"alien{i}" for i in range(48)])
        assert "gold_label" not in json.dumps(body)
        assert '"label":' not in body["messages"][1]["content"]
        schema = body["structured_outputs"]["json"]
        if anchor == "labels_only":
            assert "prefixItems" not in schema
        else:
            expected = p.anchor_values(context, anchor)
            items = schema["prefixItems"]
            assert [item["properties"]["key"]["const"] for item in items] == expected
            assert all(item["required"] == ["key", "label"] for item in items)
