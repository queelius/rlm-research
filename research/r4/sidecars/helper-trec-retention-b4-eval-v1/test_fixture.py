"""Focused contract tests for the historically exposed TREC retention panel."""

import copy
import json

import metrics


def test_exact_retention_schedule_and_accounting():
    import study

    rows, gold = study.schedule(), study.gold()
    assert len(rows) == 32
    assert len(gold["labels"]) == 128
    assert set(key for row in rows for key in row["ids"]) == set(gold["labels"])
    assert all(row["dataset"] == "trec" and len(row["ids"]) == 4 for row in rows)
    assert all(row["body"]["sampling_params"]["temperature"] == 0 for row in rows)
    calls = [
        {
            "call_id": row["call_id"],
            "ids": row["ids"],
            "status": "returned_valid",
            "prediction": {key: gold["labels"][key] for key in row["ids"]},
            "prompt_tokens": 100,
            "completion_tokens": 20,
            "cached_prompt_tokens": 0,
            "wall_seconds": 1.0,
        }
        for row in rows
    ]
    result = metrics.summarize(calls, gold, rows)
    assert result["complete"] and result["metrics"]["correct"] == 128
    assert result["inventory"]["expected_calls"] == 32
    assert result["metrics"]["unavailable_predictions"] == 0
    changed = copy.deepcopy(calls)
    identifier = changed[0]["ids"][0]
    changed[0]["prediction"][identifier] = next(
        label for label in metrics.LABELS if label != gold["labels"][identifier]
    )
    updated = metrics.summarize(changed, gold, rows)
    paired = metrics.paired(result, updated, gold, rows)
    assert updated["metrics"]["correct"] == 127
    assert paired["wins"] == 0 and paired["losses"] == 1
    assert paired["clusters"] == 32
    incomplete = metrics.summarize(changed[:-1], gold, rows)
    assert not incomplete["complete"]
    assert incomplete["inventory"]["unattempted_calls"] == 1
    assert incomplete["metrics"]["unavailable_predictions"] == 4


def test_actual_native_response_decode_uses_trec_domain():
    from transformers import AutoTokenizer

    import collect
    import study

    row = study.schedule()[0]
    gold = study.gold()["labels"]
    prediction = {key: gold[key] for key in row["ids"]}
    tokenizer = AutoTokenizer.from_pretrained(study.MODEL, local_files_only=True)
    tokens = tokenizer.encode(
        json.dumps(prediction, separators=(",", ":")), add_special_tokens=False
    ) + [151645]
    response = {
        "model": study.CHILD_ALIAS,
        "request_id": "trec-retention-fixture",
        "choices": [{"token_ids": tokens, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": len(row["body"]["token_ids"]), "completion_tokens": len(tokens)},
    }
    decoded = collect.decode(row, response, tokenizer, 1, 2)
    assert decoded["status"] == "returned_valid"
    assert decoded["prediction"] == prediction
    assert decoded["dataset"] == "trec"


def test_policy_inventory_defers_incomplete_eightstep_seed2_not_old_onestep():
    import study

    assert study.ARMS == ("c32", "rl_step8", "sft_step8")
    receipt = study.read(study.PANEL / "MANIFEST.json")
    amendment = study.read(study.ROOT / "EVALUATOR_AMENDMENT.json")
    assert receipt["conditional_fourth_arm"].startswith("AG News one-step seed2")
    assert amendment["supersedes_panel_conditional_fourth_arm_for_evaluation"]
    assert "eightstep-seed2-v1" in study.SEED2_EXCLUSION["source"]
    assert study.SEED2_EXCLUSION["status"].startswith("deferred")
