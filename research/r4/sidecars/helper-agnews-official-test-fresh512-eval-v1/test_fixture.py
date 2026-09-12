"""Actual new-panel schedule, decoder, endpoint and entrypoint fixtures."""

import json


def test_exact_official_test_schedule_and_decoder():
    from transformers import AutoTokenizer
    import collect
    import metrics
    import study

    rows, gold = study.schedule(), study.gold()
    assert len(rows) == 128 and len(gold["labels"]) == 512
    assert [key for row in rows for key in row["ids"]] == [x["id"] for x in study.read(study.EVAL_DATA / "inputs/PUBLIC.json")["records"]]
    assert all(row["body"]["sampling_params"]["temperature"] == 0 for row in rows)
    row = rows[0]
    prediction = {key: gold["labels"][key] for key in row["ids"]}
    tokenizer = AutoTokenizer.from_pretrained(study.MODEL, local_files_only=True)
    tokens = tokenizer.encode(json.dumps(prediction, separators=(",", ":")), add_special_tokens=False) + [151645]
    response = {"model": study.CHILD_ALIAS, "request_id": "official-test-fixture", "choices": [{"token_ids": tokens, "finish_reason": "stop"}], "usage": {"prompt_tokens": len(row["body"]["token_ids"]), "completion_tokens": len(tokens)}}
    decoded = collect.decode(row, response, tokenizer, 1, 2)
    assert decoded["status"] == "returned_valid" and decoded["prediction"] == prediction
    calls = [{"call_id": r["call_id"], "ids": r["ids"], "status": "returned_valid", "prediction": {k: gold["labels"][k] for k in r["ids"]}} for r in rows]
    result = metrics.summarize(calls, gold, rows)
    assert result["complete"] and result["metrics"]["correct"] == 512


def test_all_four_endpoints_fixed_before_panel_query_and_owner_bound():
    import eligibility
    import owner
    import study

    assert study.ARMS == ("c32", "rl_step8", "sft_step8", "rl_seed2_step8")
    fixed = study.read(study.ROOT / "ENDPOINTS_FIXED.json")
    assert fixed["new_panel_model_calls_before_fix"] == 0
    assert fixed["seed2_exposed_panel_score_consulted_before_fix"] is False
    assert set(fixed["trained_endpoints"]) == set(study.ARMS)
    for arm in study.ARMS:
        current = eligibility.fixed_endpoints(arm)["arm_eligibility"]
        assert current["checkpoint"] == fixed["trained_endpoints"][arm]["checkpoint"]
    assert callable(owner.execute)
