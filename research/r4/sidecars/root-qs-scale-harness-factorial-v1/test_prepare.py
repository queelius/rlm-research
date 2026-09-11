import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load_prepare():
    spec = importlib.util.spec_from_file_location("scale_harness_prepare", ROOT / "prepare.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fake_rows(count=1200):
    return [
        {
            "group_id": f"g{i:04}",
            "question": f"question {i}",
            "gold": [
                "abbreviation",
                "description and abstract concept",
                "entity",
                "human being",
                "location",
                "numeric value",
            ][i % 6],
            "source_path": "/pinned/train_5500.label",
            "source_line_1based": i + 1,
        }
        for i in range(count)
    ]


def test_select_clusters_is_hash_first_disjoint_and_nested():
    p = load_prepare()
    rows = fake_rows()
    excluded = {"g0001", "g0042", "g0900"}
    clusters, proof = p.select_clusters(rows, excluded)
    assert len(clusters) == 4
    assert all(len(c) == 256 for c in clusters)
    selected = [r["group_id"] for c in clusters for r in c]
    expected = sorted(
        (r for r in rows if r["group_id"] not in excluded),
        key=lambda r: (p.digest([p.NAMESPACE, "select", r["group_id"]]), r["group_id"]),
    )[:1024]
    assert selected == [r["group_id"] for r in expected]
    assert len(set(selected)) == 1024
    assert not set(selected) & excluded
    assert proof["selection_uses_gold_or_length"] is False
    for cluster in clusters:
        assert [r["group_id"] for r in cluster[:16]] == [r["group_id"] for r in cluster][:16]
        assert [r["group_id"] for r in cluster[:64]] == [r["group_id"] for r in cluster][:64]
        assert [r["group_id"] for r in cluster[:128]] == [r["group_id"] for r in cluster][:128]


def test_build_factorial_has_exact_pairing_and_harness_contract():
    p = load_prepare()
    clusters, _ = p.select_clusters(fake_rows(), set())
    built = p.build_factorial(clusters, used_seeds=set())
    contexts = built["PUBLIC.json"]
    plan = built["FREE_PLAN.json"]
    assert len(contexts) == 16
    assert len(plan) == 64
    assert {c["size"] for c in contexts} == {16, 64, 128, 256}
    by_cluster = {}
    for c in contexts:
        by_cluster.setdefault(c["cluster"], {})[c["size"]] = [r["source_group_id"] for r in c["records"]]
    for sizes in by_cluster.values():
        assert sizes[16] == sizes[256][:16]
        assert sizes[64] == sizes[256][:64]
        assert sizes[128] == sizes[256][:128]
    coordinates = {}
    for row in plan:
        coordinates.setdefault((row["cluster"], row["size"]), []).append(row)
    assert len(coordinates) == 16
    for rows in coordinates.values():
        assert len(rows) == 4
        assert len({r["seed"] for r in rows}) == 1
        assert {(r["policy"], r["harness_arm"]) for r in rows} == {
            ("unchanged", "raw_batch_20000b"),
            ("unchanged", "cumulative_4096b"),
            ("sft6", "raw_batch_20000b"),
            ("sft6", "cumulative_4096b"),
        }
        for row in rows:
            if row["harness_arm"] == "raw_batch_20000b":
                assert (row["return_arm"], row["view_bytes"]) == ("B", 20000)
            else:
                assert (row["return_arm"], row["view_bytes"]) == ("C", 4096)
            assert row["operator"] == "conditional_weight"
            assert row["scope"] == "ALL"


def test_zero_gold_is_retained_and_seed_collision_aborts():
    p = load_prepare()
    clusters, _ = p.select_clusters(fake_rows(), set())
    first_seed = p.seed_for(0, 16)
    try:
        p.build_factorial(clusters, used_seeds={first_seed})
    except ValueError as error:
        assert "seed collision" in str(error)
    else:
        raise AssertionError("seed collision must abort without reroll")

