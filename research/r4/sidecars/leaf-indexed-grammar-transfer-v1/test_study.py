"""Focused behavioral checks; only HTTP provider is faked, never a model/GPU call."""

import asyncio
import importlib
import json
from collections import Counter
from copy import deepcopy
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parent


def module():
    assert (ROOT / "study.py").exists(), "indexed grammar study is not implemented"
    return importlib.import_module("study")


def test_exact_factorial_excludes_both_prior_sst_studies():
    s = module()
    data = s.load_data()
    value = s.build_design(data)
    assert len(value["plan"]) == len(value["coordinates"]) == 160
    assert Counter((r["weight"], r["arm"], r["grammar"]) for r in value["plan"]) == {
        (w, a, g): 20 for w in ("old_sft", "indexed_final")
        for a in ("anonymous", "indexed") for g in ("free", "exact")}
    assert data["sst_provenance"]["remaining_after_both"] == 360
    assert data["sst_provenance"]["new_groups"] == 256
    assert data["sst_provenance"]["intersection_with_each_prior"] == [0, 0]
    for c in data["contexts"]:
        assert len(c["records"]) == len({r["group_id"] for r in c["records"]}) == 64
        assert sorted(c["permutation"]) == list(range(64))
        assert [r["id"] for r in c["records"]] == [f"q{i:04d}" for i in range(1, 65)]


def test_requests_have_identical_input_and_grammar_is_only_extra_field():
    s = module()
    d = s.build_design(s.load_data())
    row = d["plan"][0]
    exact = s.make_request(d, {**row, "arm": "indexed", "grammar": "exact"})
    free = s.make_request(d, {**row, "arm": "indexed", "grammar": "free"})
    assert {k: v for k, v in exact.items() if k != "structured_outputs"} == free
    anonymous = s.make_request(d, {**row, "arm": "anonymous", "grammar": "free"})
    assert exact["messages"][1]["content"].split(s.INPUT_MARKER)[1] == anonymous["messages"][1]["content"].split(s.INPUT_MARKER)[1]
    assert exact["messages"][0] == anonymous["messages"][0] and exact["tools"] == anonymous["tools"]
    assert exact["max_tokens"] == free["max_tokens"] == 3072
    modified = deepcopy(d)
    for b in modified["batches"]:
        for r in b["gold"]["records"]:
            r["gold_label"] = "HOST_ONLY_SENTINEL"
    assert s.make_request(modified, {**row, "arm": "indexed", "grammar": "free"}) == free
    assert "HOST_ONLY_SENTINEL" not in s.serialize(free)


def test_complete_parser_rejects_prefix_duplicate_or_missing_ids():
    s = module()
    gold = {"records": [{"id": "q0001", "gold_label": "positive"}, {"id": "q0002", "gold_label": "negative"}],
            "order": [0, 1], "arm": "indexed", "labels": ["negative", "positive"]}
    valid = s.score_labels('{"q0002":"negative","q0001":"positive"}', gold)
    assert valid["schema_valid"] and valid["strict_correct"] == 2
    assert valid["output_positions"] == [2, 1]
    for content in ['{"q0001":"positive"}', '{"q0001":"positive","q0001":"negative","q0002":"negative"}',
                    '{"q0001":"positive","q0002":"negative"', '["positive"]']:
        scored = s.score_labels(content, {**gold, "arm": "anonymous" if content.startswith("[") else "indexed"})
        assert not scored["schema_valid"] and scored["aligned_records"] == 0
        assert scored["strict_correct"] == 0 and scored["predictions"] == [None, None]
    assert not s.score_labels('{"q0001":"positive","q0002":"entity"}', gold)["schema_valid"]


def test_real_collector_dispatches_both_aliases_and_free_exact_contracts(tmp_path):
    s = module()
    assert (ROOT / "driver.py").exists(), "driver wire capture is not implemented"
    driver = importlib.import_module("driver")
    value = s.build_design(s.load_data())
    chosen = value["plan"][:8]
    value["plan"] = chosen
    value["coordinates"] = chosen
    value["model_aliases"] = {"old_sft": "fake-old", "indexed_final": "fake-indexed"}
    bodies = {r["id"]: s.make_request(value, r) for r in chosen}
    spec = {"design": value, "requests": bodies, "request_sha256": {k: s.digest(v) for k, v in bodies.items()}}

    async def provider(request):
        body = json.loads(request.content)
        row = next(r for r in chosen if bodies[r["id"]] == body)
        records = value["batches"][row["batch_id"]]["gold"]["records"]
        content = json.dumps([r["gold_label"] for r in records] if row["arm"] == "anonymous"
                             else {r["id"]: r["gold_label"] for r in records})
        return httpx.Response(200, json={"id": row["id"], "model": body["model"], "prompt_token_ids": [1],
            "choices": [{"message": {"content": content}, "finish_reason": "stop", "token_ids": [2]}],
            "usage": {"prompt_tokens": 1, "prompt_tokens_details": {"cached_tokens": 0}, "completion_tokens": 1}})

    async def go():
        async with httpx.AsyncClient(transport=httpx.MockTransport(provider),
                event_hooks={"request": [driver.wire_hook(spec, tmp_path)]}) as client:
            return await s.collect_calls(client, "http://fake/v1", spec, tmp_path)
    records, reason = asyncio.run(go())
    assert reason is None and len(records) == 8
    assert Counter(r["request"]["model"] for r in records) == {"fake-old": 4, "fake-indexed": 4}
    assert sum("structured_outputs" in r["request"] for r in records) == 4
    assert all(r["score"]["schema_valid"] and r["score"]["strict_correct"] == 64 for r in records)
    assert len(list((tmp_path / "calls").glob("*.json"))) == len(list((tmp_path / "wire").glob("*.json"))) == 8
    assert all(r["usage"]["completion_tokens"] == 1 and not r["capture"]["tools_executed"] for r in records)


def test_indexed_checkpoint_gate_rejects_wrong_step_or_selection():
    module()
    assert (ROOT / "driver.py").exists(), "indexed binding gate is not implemented"
    driver = importlib.import_module("driver")
    selected = {"epoch": 2, "checkpoint": "/frozen/checkpoint-0204"}
    result = {"identity": driver.INDEXED_ID, "optimizer_steps": 204, "selected": selected}
    selection = {"identity": driver.INDEXED_ID, "post_training_test_inspected": False, "selected": selected}
    state = {"identity": driver.INDEXED_ID, "epoch": 2, "cursor": 0, "step": 204}
    driver.check_final_identity(result, selection, state, Path(selected["checkpoint"]))
    with pytest.raises(ValueError):
        driver.check_final_identity(result, selection, {**state, "step": 203}, Path(selected["checkpoint"]))
    with pytest.raises(ValueError):
        driver.check_final_identity(result, {**selection, "post_training_test_inspected": True}, state, Path(selected["checkpoint"]))


def test_expired_overall_budget_cannot_start_collection():
    module()
    driver = importlib.import_module("driver")
    assert driver.collection_budget(1000, 2000) == 1700
    assert driver.collection_budget(1000, 1001) == 1800
    with pytest.raises(TimeoutError):
        driver.collection_budget(1000, 3700)
