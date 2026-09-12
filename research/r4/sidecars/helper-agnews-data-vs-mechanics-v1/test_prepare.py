import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("ag_prepare", ROOT / "prepare.py")
prepare = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prepare)


def test_selection_is_balanced_disjoint_and_deterministic():
    rows = [
        {
            "source_id": f"train:{label * 100 + index}",
            "source_row_0based": label * 100 + index,
            "text": f"label {label} unique item {index}",
            "label_id": label,
            "label": prepare.AG_LABELS[label],
        }
        for label in range(4)
        for index in range(8)
    ]
    excluded = {prepare.whitespace_norm("label 0 unique item 0")}
    first = prepare.select_rows(rows, excluded, train_per_label=2, heldout_per_label=3)
    second = prepare.select_rows(rows, excluded, train_per_label=2, heldout_per_label=3)
    assert first == second
    train, heldout, audit = first
    assert len(train) == 8
    assert len(heldout) == 12
    assert audit["excluded_union"] == 1
    assert {row["normalized_text_sha256"] for row in train}.isdisjoint(
        row["normalized_text_sha256"] for row in heldout
    )
    assert sorted(row["label_id"] for row in train).count(0) == 2
    assert sorted(row["label_id"] for row in heldout).count(3) == 3


def test_public_rows_do_not_contain_gold():
    row = {
        "source_id": "train:7",
        "source_row_0based": 7,
        "text": "A story",
        "label_id": 2,
        "label": "Business",
        "normalized_text_sha256": "a" * 64,
    }
    public = prepare.public_bundle([row], "train")
    gold = prepare.gold_bundle([row], "train")
    assert public["contains_gold"] is False
    assert set(public["records"][0]) == {"id", "dataset", "source_id", "text"}
    assert list(gold["labels"].values()) == ["Business"]
    assert gold["never_include_in_model_prompt"] is True


def test_all_normalized_duplicates_are_rejected_including_label_conflicts():
    rows = [
        {
            "source_id": f"train:{label * 100 + index}",
            "source_row_0based": label * 100 + index,
            "text": f"label {label} item {index}",
            "label_id": label,
            "label": prepare.AG_LABELS[label],
        }
        for label in range(4)
        for index in range(5)
    ]
    rows.extend(
        [
            {**rows[0], "source_id": "train:999"},
            {**rows[1], "source_id": "train:998", "label_id": 1, "label": "Sports"},
        ]
    )
    train, heldout, audit = prepare.select_rows(
        rows, set(), train_per_label=1, heldout_per_label=1
    )
    selected_sources = {row["source_id"] for row in train + heldout}
    assert not {"train:0", "train:999", "train:1", "train:998"} & selected_sources
    assert audit["duplicate_same_label_groups"] == 1
    assert audit["duplicate_conflicting_label_groups"] == 1
