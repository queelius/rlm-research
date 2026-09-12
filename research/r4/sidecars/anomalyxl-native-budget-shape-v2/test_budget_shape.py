import importlib

import pytest


def test_equal_2048_budget_is_allocated_one_wide_vs_three_narrow():
    study = importlib.import_module("budget_study")
    assert study.allowance("python_wide1", 0, False) == 1536
    assert study.allowance("python_wide1", 1536, True) == 512
    assert study.allowance("python_repair3", 0, False) == 512
    assert study.allowance("python_repair3", 512, False) == 512
    assert study.allowance("python_repair3", 1536, True) == 512
    with pytest.raises(ValueError, match="exhausted"):
        study.allowance("python_wide1", 2048, True)


def test_same_ten_cases_have_direct_and_both_python_arms_with_uniform_90_seconds():
    study = importlib.import_module("budget_study")
    panel = study.panel()
    rows = study.schedule()
    assert len(panel) == 10 and len(rows) == 30
    assert study.EPISODE_CAP == 90
    by_id = {}
    for row in rows:
        by_id.setdefault(row["row_id"], set()).add(row["arm"])
    assert all(arms == {"direct", "python_wide1", "python_repair3"} for arms in by_id.values())
    prompt = study.inspection_prompt("Find the event.", "python_repair3")
    assert "complete executable cell" in prompt and "no prose" in prompt
    assert "fallback" not in prompt.lower()


def test_v1_outputs_remain_source_evidence_not_reused_answers():
    study = importlib.import_module("budget_study")
    assert (study.V1 / "outputs/attempt-001/RESULT.json").exists()
    assert not study.ATTEMPT.exists()
    assert study.read(study.V1 / "READY.json")["identity"] == "e275453f9dd88007eaa64d36168c5aa8390542376b08320ce8d301c6d3649a2d"


def test_owner_binds_additive_attempt_and_exact_turn_counts():
    study = importlib.import_module("budget_study")
    owner = importlib.import_module("owner")
    assert owner.source.m is study.base
    assert owner.source.m.ATTEMPT == study.ATTEMPT
    assert owner.turns("direct") == 0
    assert owner.turns("python_wide1") == 1
    assert owner.turns("python_repair3") == 3
    assert owner.research_admissible([{"engineering": False}] * 79)
    assert not owner.research_admissible([{"engineering": False}] * 80)
    assert owner.NativeCalls is not owner.source.NativeCalls
