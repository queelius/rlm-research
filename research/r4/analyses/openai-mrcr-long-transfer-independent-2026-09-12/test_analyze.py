from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("long_transfer_analysis", ROOT / "analyze.py")
analyze = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(analyze)


def test_retrieval_delivery_categories_are_exact_and_no_cleanup() -> None:
    answer = "MARK target  "
    marker = "MARK "
    assert analyze.mechanism(["target  \n"], answer, answer, marker)["category"] == "exact_after_clean_target"
    assert analyze.mechanism(["target  \n"], "MARK wrong", answer, marker)["category"] == "clean_target_copy_failure"
    assert analyze.mechanism(["large unrelated dump"], answer, answer, marker)["category"] == "exact_without_clean_target_observation"
    assert analyze.mechanism([], "MARK target", answer, marker)["category"] == "no_clean_target_and_wrong_final"


def test_pairing_keeps_unknown_separate() -> None:
    left = {
        "a": {"available": True, "raw_exact": False, "coordinate": {"id": "a", "seed": 1, "record_id": "r"}},
        "b": {"available": False, "raw_exact": False, "coordinate": {"id": "b", "seed": 2, "record_id": "s"}},
    }
    right = {
        "a": {"available": True, "raw_exact": True, "coordinate": {"id": "a", "seed": 1, "record_id": "r"}},
        "b": {"available": True, "raw_exact": True, "coordinate": {"id": "b", "seed": 2, "record_id": "s"}},
    }
    value = analyze.pair_rows(left, right)
    assert value["paired_available"] == 1
    assert value["checkpoint32_wins"] == 1 and value["checkpoint32_losses"] == 0
    assert value["unknown_pairs"] == 1


def test_native_role_cost_uses_causal_indices() -> None:
    native = [
        {"index": 4, "status": "returned", "response": {"id": "x", "tokens": {"prompt_ids": [1, 2], "completion_ids": [3]}}},
        {"index": 5, "status": "returned", "response": {"id": "y", "tokens": {"prompt_ids": [1], "completion_ids": [2, 3]}}},
    ]
    mapping = {"matches": [{"audit_index": 0, "role": "root"}, {"audit_index": 1, "role": "child"}]}
    value = analyze.role_cost(native, mapping)
    assert value["root"] == {"calls": 1, "prompt_tokens": 2, "completion_tokens": 1}
    assert value["child"] == {"calls": 1, "prompt_tokens": 1, "completion_tokens": 2}

