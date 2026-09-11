from collections import Counter
from pathlib import Path


def test_exact_balanced_mechanical_factorial_and_unchanged_sources():
    import bv_study as s

    rows = s.read(s.ROOT / "inputs/FREE_PLAN.json")
    pairs = s.read(s.ROOT / "inputs/PAIRS.json")
    assert len(rows) == 32 and len(pairs) == 8
    assert Counter((r["return_arm"], r["view_bytes"]) for r in rows) == {
        ("B", 20000): 8,
        ("B", 4096): 8,
        ("C", 20000): 8,
        ("C", 4096): 8,
    }
    assert Counter(r["operator"] for r in rows) == {"count": 16, "weight_sum": 16}
    assert len({r["seed"] for r in rows}) == 8
    assert all(len({r["seed"] for r in rows if r["block_id"] == p["block_id"]}) == 1 for p in pairs)
    assert all(len(p["order"]) == 4 for p in pairs)
    assert s.read(s.ROOT / "inputs/PROVENANCE.json")["selection_algorithm"] == "enumerate balanced one-operator-per-parent-size assignments; minimize integer SHA256(namespace, ordered source IDs)"
    assert Path(s.ROOT / "inputs/MECHANISM_GATE.json").is_file()

