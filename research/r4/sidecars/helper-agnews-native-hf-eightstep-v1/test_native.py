"""Actual four-key grammar/reward boundary and authenticated parent binding."""

import copy
import json
from pathlib import Path

import numpy as np
import pytest


def test_four_key_native_masks_and_exact_parent_weight_binding(tmp_path):
    assert Path(__file__).with_name("core.py").exists(), "per-step policy binding is missing"
    import core

    initial = core.initial_parent()
    binding = core.binding_from_parent(initial)
    child = binding["models"][core.original.CHILD_ALIAS]
    assert child["path"] == initial["checkpoint"]
    assert child["adapter_sha256"] == core.original.CHILD_SHA
    source = core.read(core.original.SOURCE_BINDING)
    for alias, value in source["models"].items():
        if alias != core.original.CHILD_ALIAS:
            assert binding["models"][alias] == value
    wrong = copy.deepcopy(initial)
    wrong["adapter_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="parent adapter"):
        core.binding_from_parent(wrong)
    # A distinct actual checkpoint may be served at the same fixed alias, but never
    # by retaining c32's hash/path when the authenticated parent is different.
    other_checkpoint = (
        core.SIDE / "helper-hf-onpolicy-fourstep-v1/outputs/attempt-001/checkpoint-0004"
    )
    parent = {
        "step": 4,
        "checkpoint": str(other_checkpoint),
        "adapter_sha256": core.sha(other_checkpoint / "adapter_model.safetensors"),
        "config_sha256": core.sha(other_checkpoint / "adapter_config.json"),
    }
    updated_binding = core.binding_from_parent(parent)
    assert updated_binding["models"][core.original.CHILD_ALIAS]["path"] == str(other_checkpoint)
    assert (
        updated_binding["models"][core.original.CHILD_ALIAS]["adapter_sha256"]
        != child["adapter_sha256"]
    )
    view = core.step_view(1, parent=initial)
    native = core.native_module(view)
    row = view.schedule()[0]
    gold = view.read(view.HOST_GOLD)
    expected = gold[row["context_id"]]["labels"]
    prediction = {key: expected[key] for key in row["requested_ids"]}
    first = row["requested_ids"][0]
    schema = row["body"]["sampling_params"]["structured_outputs"]["json"]
    prediction[first] = next(
        label for label in schema["properties"][first]["enum"] if label != prediction[first]
    )
    decoder = native.tokenizer()
    tokens = decoder.encode(
        json.dumps(prediction, separators=(",", ":")), add_special_tokens=False
    ) + [151645]
    response = {
        "model": view.CHILD_ALIAS,
        "request_id": "cpu-eightstep-native-fixture",
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
    request_bytes = json.dumps(row["body"], separators=(",", ":")).encode()
    response_bytes = json.dumps(response).encode()
    record = native.persist_raw_and_normalize(
        row,
        response,
        1,
        2,
        gold,
        tmp_path,
        decoder,
        request_payload=request_bytes,
        response_payload=response_bytes,
    )
    assert record["correct_count"] == 3 and record["reward"] == 0.75
    assert record["action_ids"] == tokens and record["prediction"] == prediction
    assert Path(record["raw_request_path"]).read_bytes() == request_bytes
    masks = view.numeric_modules().prepare.generate_masks([record], tmp_path / "masks")
    arrays = np.load(masks["masks_npz"], allow_pickle=False)
    assert arrays[record["mask_key"]].shape[0] == len(tokens)
    malformed = copy.deepcopy(response)
    malformed["choices"][0]["token_ids"] = tokens[:-1]
    with pytest.raises(ValueError):
        native.response_record(row, malformed, decoder, 1, 2, gold)
    stage_owner = core.step_owner(view)
    assert callable(stage_owner.execute)
    assert initial == stage_owner.study.PARENT
    assert (
        stage_owner.context_receipt(
            {"vllm": {"max_model_len": 8192}}, core.read(core.ROOT / "inputs/BUILD_AUDIT.json")
        )["actual_max_model_len"]
        == 8192
    )
