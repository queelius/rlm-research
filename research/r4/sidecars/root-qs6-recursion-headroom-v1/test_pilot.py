import json
from pathlib import Path


ROOT = Path(__file__).parent


def test_actual_prefix_and_depth_zero_abi_contract():
    import study

    plans = study.make_blocks()
    assert [row["mode"] for block in plans for row in block] == (
        ["no_child"] * 24 + ["enabled"] * 48 + ["no_child"] * 24
    )
    assert len({row["pair_id"] for block in plans for row in block}) == 48
    assert len({row["id"] for block in plans for row in block}) == 96
    for mode in study.MODES:
        contract = study.condition_contract(mode)
        assert contract["environment"]["agent"]["harness"]["max_depth"] == (
            0 if mode == "no_child" else 1
        )
        assert contract["raw_files"] == ["batch_contract.py", "records.json", "context.txt", "query.txt"]
        assert contract["python_available"] is True
        assert contract["rlm_callable_advertised"] is (mode == "enabled")
        assert contract["max_tokens"] == 2048
        assert contract["temperature"] == 0.5
    rows = [row for block in plans for row in block]
    for pair_id in {row["pair_id"] for row in rows}:
        pair = [row for row in rows if row["pair_id"] == pair_id]
        assert {row["mode"] for row in pair} == set(study.MODES)
        assert len({row["seed"] for row in pair}) == 1
        assert len({row["task_name"] for row in pair}) == 1
    prefixes = study.build_prefix_manifest()
    assert len(prefixes["coordinates"]) == 96
    assert prefixes["nano_rlm_commit"] == "4ef3438d55fdd39b18d34035833c73e13b006733"
    for item in prefixes["coordinates"]:
        assert item["token_count"] == len(item["token_ids"])
        assert item["system_advertises_rlm"] is (item["mode"] == "enabled")
        assert item["user_prompt_sha256"] == prefixes["common_user_prompt_sha256_by_task"][item["task_name"]]


def test_score_reports_pairs_clusters_missing_and_router_without_naive_pvalue(tmp_path):
    import score

    rows = []
    # Context 00: enabled wins one, ties one, and one missing. Context 01: no-child wins one.
    fixtures = [
        ("00", "J1", 0, 0, 1),
        ("00", "J1", 1, 1, 1),
        ("00", "M2", 0, None, 0),
        ("01", "J1", 0, 1, 0),
    ]
    for context, family, repeat, direct, enabled in fixtures:
        for mode, reward in (("no_child", direct), ("enabled", enabled)):
            coordinate = {
                "pair_id": f"{context}:{family}:{repeat}",
                "context_id": f"question-sensitive-sft-train-{context}",
                "family": family,
                "repeat": repeat,
                "mode": mode,
            }
            rows.append({
                "coordinate": coordinate,
                "endpoint_reward": reward,
                "terminal_observable": reward is not None,
                "model_calls": 1,
                "action_tokens": 10,
                "child_action_tokens": 2 if mode == "enabled" else 0,
                "wall_seconds": 3.0,
            })
    result = score.compute(rows)
    assert result["paired_observed"] == {"enabled_win": 1, "no_child_win": 1, "tie": 1, "incomplete": 1}
    assert result["contexts"]["question-sensitive-sft-train-00"]["enabled_minus_no_child"] == 1
    assert result["contexts"]["question-sensitive-sft-train-01"]["enabled_minus_no_child"] == -1
    assert result["inference"] == {"naive_48_pair_p_value": None, "unit": "context cluster", "context_clusters": 2}
    assert result["family_router"]["kind"] == "cross-fit diagnostic using supplied family metadata"
    assert result["family_router"]["held_context_groups"] == 2
    assert result["family_router"]["missing_pairs_not_dropped"] == 1
    path = tmp_path / "rows.json"
    path.write_text(json.dumps(rows))
    assert score.compute(json.loads(path.read_text())) == result
