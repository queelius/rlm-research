"""Focused fixtures: reject exposure/word duplicates; enforce the real context bound."""

from collections import Counter

import pytest

import prepare


def test_selection_rejects_exposure_and_all_word_duplicate_members():
    rows = []
    for label in range(4):
        for index in range(8):
            rows.append(
                {
                    "source_id": f"train:{label * 8 + index}",
                    "source_row_0based": label * 8 + index,
                    "text": f"unique class {label} article {index}",
                    "label_id": label,
                    "label": prepare.old.AG_LABELS[label],
                }
            )
    rows.extend(
        [
            {"source_id": "train:90", "text": "punctuation twin!", "label_id": 0, "label": "World"},
            {
                "source_id": "train:91",
                "text": "PUNCTUATION twin?",
                "label_id": 1,
                "label": "Sports",
            },
        ]
    )
    steps, heldout, audit = prepare.freeze_selection(
        rows,
        {"unique class 0 article 0"},
        {"train:8"},
        steps_count=2,
        train_per_step_label=1,
        heldout_per_label=1,
    )
    assert [len(step) for step in steps] == [4, 4]
    assert len(heldout) == 4
    selected = [row for step in steps for row in step] + heldout
    assert len({row["source_id"] for row in selected}) == 12
    assert not (
        {"train:0", "train:8", "train:90", "train:91"} & {row["source_id"] for row in selected}
    )
    assert audit["word_duplicate_rows_rejected"] == 2
    for step in steps:
        assert Counter(row["label_id"] for row in step) == Counter({0: 1, 1: 1, 2: 1, 3: 1})
        changed = [{**row, "label": "irrelevant", "label_id": 99} for row in step]
        assert [r["source_id"] for r in prepare.order_records(step, "fixture")] == [
            r["source_id"] for r in prepare.order_records(changed, "fixture")
        ]


def test_context_bound_includes_generation_budget_without_truncation():
    assert prepare.context_bound([7168])["max_prompt_plus_completion"] == 8192
    with pytest.raises(ValueError, match="8192"):
        prepare.context_bound([7169])
