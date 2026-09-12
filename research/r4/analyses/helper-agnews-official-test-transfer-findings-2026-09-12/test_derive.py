import importlib.util
from pathlib import Path


HERE = Path(__file__).resolve().parent


def module():
    spec = importlib.util.spec_from_file_location("official_transfer_tested", HERE / "derive.py")
    value = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(value)
    return value


def test_class_effect_separates_wins_losses_and_wrong_churn():
    value = module()
    gold = {"a": "World", "b": "World", "c": "Sports", "d": "Sports"}
    before = {"a": "Business", "b": "World", "c": "Sports", "d": "World"}
    after = {"a": "World", "b": "Business", "c": "World", "d": "Business"}
    result = value.class_effect(before, after, gold)
    assert result["World"]["wins"] == 1
    assert result["World"]["losses"] == 1
    assert result["Sports"]["losses"] == 1
    assert result["Sports"]["wrong_to_different_wrong"] == 1
    assert result["Sports"]["net"] == -1


def test_seed_agreement_reports_all_fixed_labels_without_selecting_seed():
    value = module()
    gold = {"a": "World", "b": "Sports", "c": "Business"}
    first = {"a": "World", "b": "World", "c": "Business"}
    second = {"a": "World", "b": "Sports", "c": "Sci/Tech"}
    result = value.seed_agreement(first, second, gold)
    assert result == {
        "paired_available": 3,
        "same_prediction": 1,
        "different_prediction": 2,
        "both_correct": 1,
        "first_only_correct": 1,
        "second_only_correct": 1,
        "both_wrong": 0,
    }


def test_group_summary_uses_official_request_id_schema():
    value = module()
    gold = {"a": "World", "b": "Sports"}
    before = {"a": "Business", "b": "Sports"}
    after = {"a": "World", "b": "Sports"}
    result = value.group_summary(
        before, after, gold, [{"request_id": "official-request", "ids": ["a", "b"]}]
    )
    assert result["groups"] == [
        {
            "call_id": "official-request",
            "available": True,
            "before_correct": 1,
            "after_correct": 2,
            "net": 1,
            "changed": 1,
        }
    ]
