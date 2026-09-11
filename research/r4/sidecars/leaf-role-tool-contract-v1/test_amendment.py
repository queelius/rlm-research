import asyncio
import importlib
import json
import sys
import time
from copy import deepcopy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def _fixture():
    import study as s

    labels = ["negative", "positive"]
    records = [{"id": f"q{i + 1000}", "question": f"text {i}",
                "gold_label": labels[i % 2]} for i in range(64)]
    data = {"contexts": [{"index": 0, "dataset": "sst2", "source_context_index": 0,
                           "labels": labels, "records": records},
                          {"index": 1, "dataset": "sst2", "source_context_index": 1,
                           "labels": labels, "records": deepcopy(records)},
                          {"index": 2, "dataset": "agnews", "source_context_index": 0,
                           "labels": ["World", "Sports", "Business", "Sci/Tech"],
                           "records": [{"id": f"q{i + 2000}", "question": f"news {i}",
                               "gold_label": "World"} for i in range(64)]},
                          {"index": 3, "dataset": "agnews", "source_context_index": 1,
                           "labels": ["World", "Sports", "Business", "Sci/Tech"],
                           "records": [{"id": f"q{i + 3000}", "question": f"news2 {i}",
                               "gold_label": "World"} for i in range(64)]}]}
    design = s.build_design(data)
    row = next(row for row in design["plan"] if row["arm"] == "plain" and row["decoder"] == "free")
    design["plan"] = [row]
    design["coordinates"] = [row]
    body = s.make_request(design, row)
    design["rendered_prompts"] = {row["id"]: {"typed_token_ids_sha256": s.digest([101, 102])}}
    spec = {"design": design, "requests": {row["id"]: body},
            "ordered_request_sha256": {row["id"]: __import__("hashlib").sha256(
                s.serialize(body).encode()).hexdigest()}, "source_sha256": {},
            "weight_stat_identity": {}}
    spec["spec_id"] = s.digest(spec)
    endpoint = {"host": "127.0.0.1", "port": 18601, "api_key_env": "TEST_KEY",
                "model_alias": s.MODEL["alias"], "base_model": s.MODEL,
                "adapter": None, "max_model_len": 8192, "vllm_version": "0.28.0"}
    answer = [record["gold_label"] for record in design["batches"][row["batch_id"]]["gold"]["records"]]
    return s, design, row, spec, endpoint, s.serialize(answer)


@pytest.mark.parametrize("corruption", ["prompt", "pre_score", "http500"])
def test_corrupt_native_or_pre_score_response_stays_null_and_finalizes(tmp_path, monkeypatch, corruption):
    import httpx
    from transformers import AutoTokenizer

    s, design, row, spec, endpoint, content = _fixture()
    driver = importlib.import_module("driver_v2")
    tokenizer = AutoTokenizer.from_pretrained(s.MODEL["path"], local_files_only=True,
                                               trust_remote_code=False)
    outgoing = tokenizer.encode(content, add_special_tokens=False)
    monkeypatch.setattr(driver, "AUTHORIZED_OUTPUT", tmp_path / "rollout")
    monkeypatch.setenv("TEST_KEY", "fixture-not-secret")

    async def handler(request):
        if request.url.path == "/version":
            return httpx.Response(200, json={"version": "0.28.0"})
        if request.url.path == "/v1/models":
            return httpx.Response(200, json={"data": [{"id": s.MODEL["alias"],
                "root": s.MODEL["path"], "parent": None}]})
        if corruption == "http500":
            return httpx.Response(500, text="fixture failure")
        raw = {"id": "native-response", "model": s.MODEL["alias"],
               "prompt_token_ids": [101, 999] if corruption == "prompt" else [101, 102],
               "choices": [{"index": 0, "finish_reason": "stop", "token_ids": outgoing,
                            "message": {"role": "assistant", "content": content}}],
               "usage": {"prompt_tokens": 2, "completion_tokens": len(outgoing),
                         "total_tokens": len(outgoing) + 2}}
        if corruption == "pre_score":
            raw["choices"] = []
        return httpx.Response(200, json=raw)

    original = httpx.AsyncClient
    monkeypatch.setattr(httpx, "AsyncClient",
                        lambda **kwargs: original(transport=httpx.MockTransport(handler), **kwargs))
    assert asyncio.run(driver.run(endpoint, spec, tmp_path / "rollout", time.time() + 30)) == 2
    record = s.read(next((tmp_path / "rollout/calls").glob("*.json")))
    if corruption == "http500":
        assert "raw_response" not in record and record["http_status"] == 500
    else:
        assert record["raw_response"]["id"] == "native-response"
    assert record["native_verified"] is False and record["model_completed"] is False
    assert record["score"]["strict_correct_planned_denominator"] is None
    analysis = s.read(tmp_path / "rollout/analysis.json")
    assert analysis["coordinates"][0]["score"]["planned_correct_bounds"] == [0, 64]


def test_authenticated_native_tool_envelope_is_observed_zero():
    from transformers import AutoTokenizer
    import scoring_v2

    s, design, row, spec, endpoint, content = _fixture()
    tokenizer = AutoTokenizer.from_pretrained(s.MODEL["path"], local_files_only=True,
                                               trust_remote_code=False)
    code = "print(2)"
    envelope = "<tool_call>\n" + json.dumps(
        {"name": "ipython", "arguments": {"code": code}}) + "\n</tool_call>"
    outgoing = tokenizer.encode(envelope, add_special_tokens=False) + [151645]
    raw = {"id": "native-tool", "model": s.MODEL["alias"], "prompt_token_ids": [101, 102],
           "choices": [{"index": 0, "finish_reason": "tool_calls", "token_ids": outgoing,
                        "message": {"role": "assistant", "content": None,
                                    "tool_calls": [{"type": "function", "function": {
                                        "name": "ipython", "arguments": json.dumps({"code": code})}}]}}],
           "usage": {"prompt_tokens": 2, "completion_tokens": len(outgoing),
                     "total_tokens": len(outgoing) + 2}}
    message, finish, usage = scoring_v2.verified_response(raw, [101, 102], tokenizer)
    gold = design["batches"][row["batch_id"]]["gold"]
    score = s.score_message(message, gold, finish)
    assert score["observed_policy_output"] is True
    assert score["route"] == "native_tool_call"
    assert score["strict_correct_planned_denominator"] == 0
    broken = deepcopy(raw)
    broken["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"] = json.dumps(
        {"code": "print(3)"})
    with pytest.raises(ValueError):
        scoring_v2.verified_response(broken, [101, 102], tokenizer)


def test_amended_owner_targets_v2_collector_and_same_attempt():
    owner = importlib.import_module("owner_v2")
    assert callable(owner.module.driver.verify)
    argv = owner.module.collector_argv(ROOT / "stage", ROOT / "outputs/attempt-001", 1234.5)
    assert argv[1] == str(ROOT / "driver_v2.py")
    assert argv[6] == str(ROOT / "outputs/attempt-001/rollout")
    with pytest.raises(ValueError):
        owner.module.collector_argv(ROOT / "stage", ROOT / "outputs/attempt-002", 1234.5)


def test_authenticator_accepts_all_completed_free_id_native_branches_without_score_change():
    from transformers import AutoTokenizer
    import scoring_v2
    import study as s

    old = s.SIDE / "leaf-free-id-correspondence-v1"
    output = old / "outputs/attempt-003/rollout/calls"
    spec = s.read(old / "SPEC.json")
    tokenizer = AutoTokenizer.from_pretrained(s.MODEL["path"], local_files_only=True,
                                               trust_remote_code=False)
    checked = 0
    routes = set()
    for path in sorted(output.glob("*.json")):
        record = s.read(path)
        raw = record["raw_response"]
        row = record["coordinate"]
        message, finish, usage = scoring_v2.verified_response(
            raw, raw["prompt_token_ids"], tokenizer)
        gold = spec["design"]["batches"][row["batch_id"]]["gold"]
        score = s.score_message(message, gold, finish)
        assert score["strict_correct_planned_denominator"] == \
            record["score"]["strict_correct_planned_denominator"]
        routes.add(score["route"])
        checked += 1
    assert checked == 96
    assert {"native_tool_call", "literal_tool_wrapper", "final_text"} <= routes
