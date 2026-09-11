import json
from collections import Counter

import prepare
import protocol
import owner


def test_official_test_keeps_all_source_lines_and_duplicates():
    rows, provenance = prepare.official_rows()
    assert len(rows) == 500
    assert len({row["id"] for row in rows}) == 500
    assert provenance["normalized_question_groups"] == 500
    assert provenance["duplicate_source_lines_retained"] == 0
    assert Counter(row["gold"] for row in rows) == {
        "abbreviation": 9,
        "description and abstract concept": 138,
        "entity": 94,
        "human being": 65,
        "location": 81,
        "numeric value": 113,
    }


def test_official_test_groups_do_not_intersect_optimizer_train_groups():
    _, provenance = prepare.official_rows()
    assert provenance["optimizer_train_normalized_group_intersection"] == []
    assert provenance["optimizer_train_groups"] == 5065
    assert provenance["raw_train_overlap_groups"] == 11


def test_plan_covers_all_500_records_in_every_condition():
    rows, _ = prepare.official_rows()
    plan = prepare.plan_only(rows)
    assert len(plan) == 148
    for seed in (991902701, 991902702):
        for policy in ("base", "c32"):
            for arm in ("W", "S"):
                selected = [row for row in plan if (row["seed"], row["model_policy"], row["arm"]) == (seed, policy, arm)]
                assert sum(row["n"] for row in selected) == 500
                assert [row["n"] for row in selected] == ([100] * 5 if arm == "W" else [16] * 31 + [4])


def test_protocol_rejects_duplicate_ids():
    result = protocol.score('{"x":"entity","x":"entity"}', ["x"], {"x": "entity"}, True)
    assert result["available"] and not result["complete_map"] and result["strict_correct"] == 0


def test_model_dispatch_is_exact():
    assert prepare.model_for("base", "/base", "child") == "/base"
    assert prepare.model_for("c32", "/base", "child") == "child"


def test_owner_collector_argv_is_exact_new_namespace(tmp_path):
    stage = tmp_path / "service"
    output = tmp_path / "rollout"
    argv = owner.collector_argv(stage, output, 123.0)
    assert argv[1].endswith("leaf-trec-test-adapter-granularity-v1/collect.py")
    assert argv[-2:] == ["--deadline", "123.0"]
