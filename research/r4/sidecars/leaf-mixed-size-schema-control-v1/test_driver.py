"""Focused CPU tests for the additive fixed-weight format control."""

import asyncio
import importlib.util
import json
from copy import deepcopy
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parent


def driver():
    assert (ROOT / "driver.py").exists(), "mixed schema driver missing"
    loader = importlib.util.spec_from_file_location("mixed_schema_cpu_test", ROOT / "driver.py")
    module = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(module)
    return module


def test_fixed64_layout_is_four_weights_and_sixteen_paired_requests():
    d = driver()
    spec = d.build_spec()
    assert spec["weight_conditions"] == ["original", "old_sft", "Afinal", "Bfinal"]
    assert spec["total_calls"] == 64
    design = spec["design"]
    assert len(design["plan"]) == 16
    assert {r["seed"] for r in design["plan"]} == {981261401, 981261402}
    records = [r for c in design["contexts"] for r in c["records"]]
    assert [r["record_index"] for r in records] == list(range(1, 257))
    assert len({r["question_group_sha256"] for r in records}) == 256
    pairs = {}
    for row in design["plan"]:
        pairs.setdefault(row["parent_row_id"], set()).add(row["arm"])
    assert len(pairs) == 8 and all(v == {"free64", "schema64"} for v in pairs.values())


def test_schema_is_exact_parent_offset0_body_and_free_removes_only_schema():
    d = driver()
    spec = d.build_spec()
    parent = d.read(d.PARENT_SPEC)
    parent_rows = {r["id"]: r for r in parent["design"]["plan"]}
    design = spec["design"]
    for row in design["plan"]:
        body = d.make_request(design, row)
        original = d.corr.make_request(parent["design"], parent_rows[row["parent_row_id"]])
        original["model"] = body["model"]
        if row["arm"] == "free64":
            original.pop("structured_outputs")
        assert json.dumps(body) == json.dumps(original)
        assert body["max_tokens"] == 1024 and body["temperature"] == 0.5
    for a, b in zip(design["plan"][::2], design["plan"][1::2], strict=True):
        left, right = d.make_request(design, a), d.make_request(design, b)
        left.pop("structured_outputs", None)
        right.pop("structured_outputs", None)
        assert json.dumps(left) == json.dumps(right)


def test_strict_scorer_does_not_convert_malformed_arrays_into_semantic_errors():
    d = driver()
    spec = d.build_spec()
    scoring = spec["design"]["batches"][0]["gold"]
    result = d.corr.score_response('["entity"]', scoring)
    assert not result["schema_valid"] and result["aligned_records"] == 0
    assert result["predictions"] == [None] * 64
    result = d.corr.score_response(json.dumps(["LOC"] * 64), scoring)
    assert result["aligned_records"] == 64 and not result["schema_valid"]
    assert result["noncanonical_labels"] == 64


def test_real_collector_keeps_both_physical_prompts_and_per_source_metrics(tmp_path):
    d = driver()
    spec = d.build_spec()
    spec["design"]["plan"] = spec["design"]["plan"][:2]
    spec["design"]["coordinates"] = spec["design"]["coordinates"][:2]
    (tmp_path / "calls").mkdir()
    (tmp_path / "coordinates").mkdir()
    seen = []

    def reply(request):
        body = json.loads(request.content)
        seen.append(body)
        ids = (
            d.corr.tokenizer()
            .encode(body["messages"][0]["content"] + "\n" + body["messages"][1]["content"])
            .ids
        )
        return httpx.Response(
            200,
            json={
                "model": body["model"],
                "prompt_token_ids": ids,
                "choices": [
                    {
                        "finish_reason": "stop",
                        "message": {"content": json.dumps(["entity"] * 64)},
                        "token_ids": [1, 2],
                    }
                ],
                "usage": {
                    "prompt_tokens": len(ids),
                    "completion_tokens": 2,
                    "prompt_tokens_details": {"cached_tokens": 0},
                },
            },
        )

    async def execute():
        async with httpx.AsyncClient(transport=httpx.MockTransport(reply)) as client:
            return await d.collect_calls(client, "http://cpu.invalid/v1", spec, tmp_path)

    records, reason = asyncio.run(execute())
    assert reason is None and len(records) == 2
    assert sum("structured_outputs" in body for body in seen) == 1
    summary = d.summarize(spec["design"], records)
    assert len(summary["paired"]) == 1
    assert summary["paired"][0]["physical_input_ids_equal"] is True
    assert all(cell["aligned_assignments"] == 64 for cell in summary["cells"])
    assert all(cell["usage"]["completion_tokens"] == 2 for cell in summary["cells"])
    assert len(list((tmp_path / "calls").glob("*.json"))) == 2


def test_authentication_rejects_wrong_old_weights_without_a_live_call():
    d = driver()
    endpoint = d.read(d.corr.HISTORICAL_SELECTED)
    sources = {}
    d.authenticate("old_sft", endpoint, sources)
    assert any(p.endswith("adapter_model.safetensors") for p in sources)
    bad = deepcopy(endpoint)
    bad["adapter"]["model_sha256"] = "wrong"
    with pytest.raises(ValueError, match="weight identity"):
        d.authenticate("old_sft", bad, {})


def test_frozen_spec_rejects_unapproved_request_cap_drift():
    d = driver()
    spec = d.build_spec()
    spec["design"]["max_tokens"] = 1025
    with pytest.raises(ValueError, match="frozen specification differs"):
        d.verify_inputs(spec)
