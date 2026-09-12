import json


def _response(row, gold, tokenizer, request_id):
    prediction = {key: gold[key] for key in row["ids"]}
    token_ids = tokenizer.encode(
        json.dumps(prediction, separators=(",", ":")), add_special_tokens=False
    ) + [151645]
    return {
        "model": "Qwen3-4B-Instruct-2507-no-research-adapter",
        "request_id": request_id,
        "choices": [
            {
                "token_ids": token_ids,
                "finish_reason": "stop",
                "logprobs": {
                    "content": [
                        {"token": f"token_id:{token}", "logprob": -0.1} for token in token_ids
                    ]
                },
            }
        ],
        "usage": {
            "prompt_tokens": len(row["body"]["token_ids"]),
            "completion_tokens": len(token_ids),
            "total_tokens": len(row["body"]["token_ids"]) + len(token_ids),
            "prompt_tokens_details": {"cached_tokens": 0},
        },
    }


def test_schedules_match_frozen_panels_except_true_base_alias():
    import study

    ag, db = study.schedules()
    assert len(ag) == 128 and sum(len(row["ids"]) for row in ag) == 512
    assert len(db) == 56 and sum(len(row["ids"]) for row in db) == 224
    assert [row["body"]["sampling_params"]["seed"] for row in ag] == list(
        range(202609122800, 202609122928)
    )
    assert [row["body"]["sampling_params"]["seed"] for row in db] == list(
        range(202609123500, 202609123556)
    )
    assert all(row["body"]["model"] == study.BASE_ALIAS for row in ag + db)
    assert study.exact_source_request_match()
    binding = study.binding()
    assert binding["adapter"] is None
    assert binding["checkpoint"]["alias"] == study.BASE_ALIAS
    assert binding["checkpoint"]["path"] == str(study.MODEL)


def test_actual_raw_decoder_handles_both_label_spaces_and_missing_call():
    from transformers import AutoTokenizer

    import collect
    import metrics
    import study

    tokenizer = AutoTokenizer.from_pretrained(study.MODEL, local_files_only=True)
    panels = study.schedules()
    gold = study.gold()
    decoded = []
    for panel, rows in zip(study.PANELS, panels, strict=True):
        row = rows[0]
        call = collect.decode(
            row,
            _response(row, gold[panel], tokenizer, "base-fixture-" + panel),
            tokenizer,
            1,
            2,
        )
        assert call["status"] == "returned_valid"
        assert call["prediction"] == {key: gold[panel][key] for key in row["ids"]}
        decoded.append(call)
    assert decoded[0]["dataset"] == "ag_news"
    assert decoded[1]["dataset"] == "dbpedia14"

    ag_rows = panels[0]
    calls = [
        collect.decode(
            row,
            _response(row, gold["ag_news"], tokenizer, f"base-ag-{index}"),
            tokenizer,
            1,
            2,
        )
        for index, row in enumerate(ag_rows[:-1])
    ]
    partial = metrics.summarize_panel("ag_news", calls, gold["ag_news"], ag_rows)
    assert partial["complete"] is False
    assert partial["metrics"]["correct"] == 508
    assert partial["metrics"]["unavailable_predictions"] == 4
    assert partial["metrics"]["primary_accuracy"] is None


def test_owner_loads_current_released_base_service_dependency():
    import owner
    import study

    suite = study.dependencies()
    assert suite.SERVE == study.SERVICE_WRAPPER
    assert suite.life.ALLOCATION_SERVICE == study.SERVICE_WRAPPER
    assert callable(owner.execute)


def test_owner_authenticates_preexec_and_actual_kernel_log(tmp_path):
    import owner
    import study

    service = tmp_path / "service"
    engine = service / "service"
    engine.mkdir(parents=True)
    command = ["inference", "@", "inference.json"]
    start = {
        "pid": 4242,
        "command": command,
        "launcher_sha256": study.sha(study.SERVICE_WRAPPER),
    }
    study.write_x(engine / "SERVER_START.json", start)
    study.write_x(
        engine / "ENGINE_ENV_ATTESTATION.json",
        {
            "schema": "batch-invariant-engine-preexec-attestation-v1",
            "pid": 4242,
            "VLLM_BATCH_INVARIANT": "1",
            "command_sha256": study.digest(command),
            "wrapper_sha256": study.sha(study.SERVICE_WRAPPER),
            "credentials_persisted": False,
        },
    )
    (engine / "inference.log").write_text("EngineCore batch_invariant.py matmul_persistent\n")
    receipt = owner.attest_start(service)
    final = owner.finalize_attestation(service, receipt, True)
    assert final["actual_kernel_marker"] == "batch_invariant.py / matmul_persistent"
    assert final["VLLM_BATCH_INVARIANT"] == "1"
