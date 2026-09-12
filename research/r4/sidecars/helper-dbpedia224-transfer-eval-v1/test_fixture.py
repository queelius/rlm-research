import json
from pathlib import Path


def _response(row, labels, tokenizer, request_id="dbpedia-fixture"):
    prediction = {key: labels[key] for key in row["ids"]}
    tokens = tokenizer.encode(
        json.dumps(prediction, separators=(",", ":")), add_special_tokens=False
    ) + [151645]
    return {
        "model": "strict-rlm-qwen3-4b-role-sft-selected-v1",
        "request_id": request_id,
        "choices": [
            {
                "token_ids": tokens,
                "finish_reason": "stop",
                "logprobs": {
                    "content": [
                        {"token": f"token_id:{token}", "logprob": -0.1} for token in tokens
                    ]
                },
            }
        ],
        "usage": {
            "prompt_tokens": len(row["body"]["token_ids"]),
            "completion_tokens": len(tokens),
            "total_tokens": len(row["body"]["token_ids"]) + len(tokens),
            "prompt_tokens_details": {"cached_tokens": 0},
        },
    }


def test_exact_dbpedia_schedule_and_raw_send_decoder(tmp_path, monkeypatch):
    from transformers import AutoTokenizer

    import collect
    import metrics
    import study

    rows, gold = study.schedule(), study.gold()
    labels = gold["labels"]
    assert len(rows) == 56 and len(labels) == 224
    assert [key for row in rows for key in row["ids"]] == [
        item["id"] for item in study.read(study.EVAL_DATA / "inputs/PUBLIC.json")["records"]
    ]
    assert {value: list(labels.values()).count(value) for value in study.LABELS} == {
        value: 16 for value in study.LABELS
    }
    assert [row["body"]["sampling_params"]["seed"] for row in rows] == list(
        range(202609123500, 202609123556)
    )

    tokenizer = AutoTokenizer.from_pretrained(study.MODEL, local_files_only=True)
    response = _response(rows[0], labels, tokenizer)

    class Reply:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps(response).encode()

    monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY", "cpu-fixture")
    monkeypatch.setattr(collect, "urlopen", lambda request, timeout: Reply())
    call = collect.send("http://fixture/inference/v1/generate", rows[0], tokenizer, tmp_path, 10**12)
    assert call["status"] == "returned_valid"
    assert call["prediction"] == {key: labels[key] for key in rows[0]["ids"]}
    assert study.read(call["raw_request_path"]) == rows[0]["body"]
    assert study.read(call["raw_response_path"]) == response
    assert call["returned_logprob_entries"] == len(response["choices"][0]["token_ids"])

    calls = []
    for index, row in enumerate(rows):
        if index == 55:
            continue
        decoded = collect.decode(
            row, _response(row, labels, tokenizer, f"dbpedia-{index}"), tokenizer, 1, 2
        )
        calls.append(decoded)
    partial = metrics.summarize(calls, gold, rows)
    assert partial["complete"] is False
    assert partial["metrics"] == {
        "correct": 220,
        "available_predictions": 220,
        "unavailable_predictions": 4,
        "accuracy_available": 1.0,
        "primary_accuracy": None,
    }
    assert sum(row["unavailable"] for row in partial["per_class"].values()) == 4


def test_all_four_fixed_endpoints_and_actual_owner_entrypoint():
    import eligibility
    import owner
    import study

    assert study.ARMS == ("c32", "rl_step8", "sft_step8", "rl_seed2_step8")
    fixed = study.read(study.ROOT / "ENDPOINTS_FIXED.json")
    assert fixed["new_dbpedia_model_calls_before_fix"] == 0
    assert set(fixed["trained_endpoints"]) == set(study.ARMS)
    for arm in study.ARMS:
        current = eligibility.fixed_endpoints(arm)["arm_eligibility"]
        assert current["checkpoint"] == fixed["trained_endpoints"][arm]["checkpoint"]
    assert callable(owner.execute)

