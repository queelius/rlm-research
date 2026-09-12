import pytest

from prepare import choose, deduplicate


def test_duplicate_titles_and_contents_are_excluded_as_groups():
    rows = [
        {"source_id": "a", "title": "Same", "content": "one", "label_id": 0},
        {"source_id": "b", "title": "same!", "content": "two", "label_id": 1},
        {"source_id": "c", "title": "C", "content": "duplicate!", "label_id": 0},
        {"source_id": "d", "title": "D", "content": "DUPLICATE", "label_id": 1},
        {"source_id": "e", "title": "", "content": "unique one", "label_id": 0},
        {"source_id": "f", "title": "", "content": "unique two", "label_id": 1},
    ]
    kept, rejected = deduplicate(rows)
    assert {row["source_id"] for row in kept} == {"e", "f"}
    assert rejected == {"a", "b", "c", "d"}


def test_balanced_selection_is_deterministic_and_does_not_resample_for_answers():
    rows = [
        {"source_id": f"{label}:{i}", "label_id": label}
        for label in range(3) for i in range(4)
    ]
    selected = choose(rows, range(3), 2)
    assert selected == choose(list(reversed(rows)), range(3), 2)
    assert [sum(row["label_id"] == label for row in selected) for label in range(3)] == [2, 2, 2]
    with pytest.raises(ValueError):
        choose(rows, range(3), 5)
