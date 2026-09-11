import hashlib
import importlib.util
from pathlib import Path

import pytest

MODULE = Path(__file__).with_name("prepare.py")
spec = importlib.util.spec_from_file_location("composition_prepare", MODULE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def rows():
    return [
        {
            "group_id": hashlib.sha256(f"question-{i}".encode()).hexdigest(),
            "question": f"Question {i}?",
            "gold": ("human being", "numeric value", "entity")[i % 3],
            "coarse": ("HUM", "NUM", "ENTY")[i % 3],
            "source_line_1based": i + 1,
            "all_source_lines_1based": [i + 1],
            "source_path": "/fixed/test-source",
        }
        for i in range(489)
    ]


def test_group_selection_is_order_and_label_independent():
    first = module.build(rows())
    changed = [dict(row, gold="location", coarse="LOC") for row in reversed(rows())]
    second = module.build(changed)
    assert [c["group_ids"] for c in first["contexts"]] == [
        c["group_ids"] for c in second["contexts"]
    ]
    ids = [group for c in first["contexts"] for group in c["group_ids"]]
    assert len(ids) == len(set(ids)) == 384
    assert len(first["contexts"]) == 6
    assert len(first["tasks"]) == 12


def test_context_and_prompt_have_no_gold_and_counts_are_host_only():
    result = module.build(rows())
    lookup = {row["group_id"]: row for row in rows()}
    for context in result["contexts"]:
        assert context["text"].count(" || Instance: ") == 64
        assert "human being" not in context["text"]
        assert "numeric value" not in context["text"]
        for task in (t for t in result["tasks"] if t["context_id"] == context["id"]):
            expected = sum(lookup[g]["gold"] == task["label"] for g in context["group_ids"])
            assert task["answer"] == repr([expected])
            assert str(expected) not in task["question"]
            assert task["answer_type"] == "ANSWER_TYPE.NUMERIC"


def test_plan_is_paired_fresh_and_uses_every_task_twice():
    result = module.build(rows())
    plan = result["plan"]
    assert len(plan) == 48
    assert len({r["id"] for r in plan}) == 48
    assert len({r["pair_id"] for r in plan}) == 24
    for start in range(0, 48, 2):
        left, right = plan[start : start + 2]
        assert left["pair_id"] == right["pair_id"]
        assert left["seed"] == right["seed"]
        assert left["task_name"] == right["task_name"]
        assert {left["arm"], right["arm"]} == {"original_child", "sft_child"}


def test_duplicate_or_insufficient_group_input_is_rejected():
    with pytest.raises(ValueError):
        module.build(rows()[:383])
    duplicated = rows()
    duplicated[-1] = duplicated[0]
    with pytest.raises(ValueError):
        module.build(duplicated)
