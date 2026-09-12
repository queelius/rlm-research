"""Catches old16-key reward/mask assumptions at the actual native boundary."""

import copy
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest


def test_four_key_raw_decode_reward_and_exact_grammar_masks(tmp_path, monkeypatch):
    path = Path(__file__).with_name("native_collect.py")
    assert path.exists(), "four-key native boundary is not implemented"
    spec = importlib.util.spec_from_file_location("ag_native_fixture", path)
    native = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(native)
    rows = native.study.schedule()
    row = rows[0]
    assert len(rows) == 128 and len(row["requested_ids"]) == 4
    gold = native.study.read(native.study.HOST_GOLD)
    expected = gold[row["context_id"]]["labels"]
    prediction = {key: expected[key] for key in row["requested_ids"]}
    labels = row["body"]["sampling_params"]["structured_outputs"]["json"]["properties"]
    key = row["requested_ids"][0]
    prediction[key] = next(label for label in labels[key]["enum"] if label != expected[key])
    tokenizer = native.tokenizer()
    tokens = tokenizer.encode(
        json.dumps(prediction, separators=(",", ":")), add_special_tokens=False
    ) + [151645]
    response = {
        "model": native.study.CHILD_ALIAS,
        "request_id": "cpu-four-key-fixture",
        "choices": [
            {
                "text": "",
                "token_ids": tokens,
                "finish_reason": "stop",
                "logprobs": {
                    "content": [
                        {"token": "token_id:" + str(token), "logprob": -0.2} for token in tokens
                    ]
                },
            }
        ],
        "usage": {"prompt_tokens": len(row["body"]["token_ids"]), "completion_tokens": len(tokens)},
    }
    request_bytes = json.dumps(row["body"]).encode()
    response_bytes = json.dumps(response).encode()
    record = native.persist_raw_and_normalize(
        row,
        response,
        1,
        2,
        gold,
        tmp_path,
        tokenizer,
        request_payload=request_bytes,
        response_payload=response_bytes,
    )
    assert record["correct_count"] == 3 and record["reward"] == 0.75
    assert record["prediction"] == prediction and record["action_ids"] == tokens
    assert Path(record["raw_response_path"]).read_bytes() == response_bytes
    modules = native.study.numeric_modules()
    manifest = modules.prepare.generate_masks([record], tmp_path / "masks")
    arrays = np.load(manifest["masks_npz"], allow_pickle=False)
    assert arrays[record["mask_key"]].shape[0] == len(tokens)
    owner = native.study.load("ag_native_owner_fixture", native.study.ROOT / "owner.py")
    config_path = native.study.old.BATCH_ROOT / "outputs/attempt-003/service/service/inference.json"
    config = native.study.read(config_path)
    audit = native.study.read(native.study.ROOT / "inputs/BUILD_AUDIT.json")
    assert owner.context_receipt(config, audit)["actual_max_model_len"] == 8192
    assert audit["max_prompt_plus_completion"] == 2157
    with pytest.raises(ValueError, match="context"):
        owner.context_receipt(config, {"max_prompt_plus_completion": 8193})
    monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY", "cpu-fixture-only-not-a-secret")
    lifecycle = owner.native_collect.lifecycle()
    with owner.study.aliases({"study": owner.study}):
        suite = lifecycle.dependencies()
    assert callable(suite.start_service) and callable(suite.release_service)
    evaluator = native.study.load(
        "ag_native_actual_evaluator_fixture", native.study.ROOT / "eval_owner.py"
    )
    collector = evaluator.build()
    assert collector.study.ATTEMPT == evaluator.ATTEMPT
    assert len(collector.study.schedule()) == 64
    assert len({key for entry in collector.study.schedule() for key in entry["ids"]}) == 256
    malformed = copy.deepcopy(response)
    malformed["choices"][0]["token_ids"] = tokens[:-1]
    with pytest.raises(ValueError):
        native.response_record(row, malformed, tokenizer, 1, 2, gold)
