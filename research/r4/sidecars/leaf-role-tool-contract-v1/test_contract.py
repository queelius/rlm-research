import importlib
import asyncio
import json
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def _contexts():
    labels = {"agnews": ["World", "Sports", "Business", "Sci/Tech"],
              "sst2": ["negative", "positive"]}
    result = []
    for dataset in labels:
        for context_index in range(2):
            records = [
                {"id": f"z{context_index}{i:03d}", "question": f"text {dataset} {context_index} {i}",
                 "gold_label": labels[dataset][i % len(labels[dataset])]}
                for i in range(64)
            ]
            result.append({"index": len(result), "dataset": dataset,
                           "source_context_index": context_index,
                           "labels": labels[dataset], "records": records})
    return result


def test_builds_exact_96_call_interface_factorial():
    s = importlib.import_module("study")
    design = s.build_design({"contexts": _contexts()})
    assert len(design["plan"]) == 96
    assert len({row["id"] for row in design["plan"]}) == 96
    assert {row["system_role"] for row in design["plan"]} == {"coding", "classifier"}
    assert {row["tools"] for row in design["plan"]} == {"present", "absent"}
    assert {row["arm"] for row in design["plan"]} == {"matching", "constant", "plain"}
    assert {row["decoder"] for row in design["plan"]} == {"free", "exact"}
    for dataset in ("agnews", "sst2"):
        assert sum(row["dataset"] == dataset for row in design["plan"]) == 48


def test_requests_change_only_declared_system_tool_and_decoder_fields():
    s = importlib.import_module("study")
    design = s.build_design({"contexts": _contexts()})
    rows = [row for row in design["plan"] if row["context_index"] == 0 and row["arm"] == "matching"]
    bodies = {(r["system_role"], r["tools"], r["decoder"]): s.make_request(design, r) for r in rows}
    coding = bodies[("coding", "present", "free")]
    no_tools = bodies[("coding", "absent", "free")]
    classifier = bodies[("classifier", "present", "free")]
    exact = bodies[("coding", "present", "exact")]
    assert coding["messages"][1:] == no_tools["messages"][1:] == classifier["messages"][1:]
    assert coding["messages"][0] == no_tools["messages"][0]
    assert coding["messages"][0] != classifier["messages"][0]
    assert "tools" in coding and "tools" not in no_tools
    assert "structured_outputs" not in coding
    assert {k: v for k, v in exact.items() if k != "structured_outputs"} == coding


def test_completed_tool_route_is_observed_zero_not_null():
    s = importlib.import_module("study")
    design = s.build_design({"contexts": _contexts()})
    row = next(row for row in design["plan"] if row["arm"] == "matching")
    gold = design["batches"][row["batch_id"]]["gold"]
    score = s.score_message({"content": None, "tool_calls": [{"id": "call1", "type": "function"}]},
                            gold, "tool_calls")
    assert score["observed_policy_output"] is True
    assert score["strict_correct_planned_denominator"] == 0
    assert score["planned_correct_bounds"] == [0, 0]
    assert score["route"] == "native_tool_call"
    missing = s.score_missing(gold)
    assert missing["strict_correct_planned_denominator"] is None
    assert missing["planned_correct_bounds"] == [0, 64]


def test_contract_requires_ordered_exact_tags_and_never_reorders():
    s = importlib.import_module("study")
    design = s.build_design({"contexts": _contexts()})
    row = next(row for row in design["plan"] if row["arm"] == "matching")
    gold = design["batches"][row["batch_id"]]["gold"]
    answer = [{"tag": record["id"], "label": record["gold_label"]}
              for record in gold["records"]]
    valid = s.score_message({"content": s.serialize(answer)}, gold, "stop")
    assert valid["full_contract_valid"] and valid["strict_correct_planned_denominator"] == 64
    answer[0]["tag"], answer[1]["tag"] = answer[1]["tag"], answer[0]["tag"]
    invalid = s.score_message({"content": s.serialize(answer)}, gold, "stop")
    assert not invalid["full_contract_valid"]
    assert invalid["strict_correct_planned_denominator"] == 0
    assert invalid["conditional_positional_correct"] == 64
    assert invalid["emitted_id_position_matches"] == 62


def test_driver_authorizes_only_exact_current_attempt(tmp_path):
    driver = importlib.import_module("driver")
    wanted = ROOT / "outputs/attempt-001/rollout"
    driver.validate_output(wanted)
    with pytest.raises(ValueError):
        driver.validate_output(ROOT / "outputs/attempt-002/rollout")


def test_driver_records_completed_tool_route_without_execution(tmp_path, monkeypatch):
    import httpx
    import study as s
    driver = importlib.import_module("driver")
    design = s.build_design({"contexts": _contexts()})
    design["plan"] = design["plan"][:1]
    design["coordinates"] = design["coordinates"][:1]
    row = design["plan"][0]
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
    monkeypatch.setattr(driver, "AUTHORIZED_OUTPUT", tmp_path / "rollout")
    monkeypatch.setenv("TEST_KEY", "fixture-not-secret")

    async def handler(request):
        if request.url.path == "/version":
            return httpx.Response(200, json={"version": "0.28.0"})
        if request.url.path == "/v1/models":
            return httpx.Response(200, json={"data": [{"id": s.MODEL["alias"],
                "root": s.MODEL["path"], "parent": None}]})
        return httpx.Response(200, json={"id": "native-response-1", "model": s.MODEL["alias"],
            "prompt_token_ids": [101, 102], "choices": [{"finish_reason": "tool_calls",
            "token_ids": [201], "message": {"content": None, "tool_calls": [{"id": "call1"}]}}],
            "usage": {"prompt_tokens": 2, "completion_tokens": 1, "total_tokens": 3}})

    original = httpx.AsyncClient
    monkeypatch.setattr(httpx, "AsyncClient",
                        lambda **kwargs: original(transport=httpx.MockTransport(handler), **kwargs))
    assert asyncio.run(driver.run(endpoint, spec, tmp_path / "rollout", time.time() + 30)) == 0
    record = s.read(next((tmp_path / "rollout/calls").glob("*.json")))
    assert record["score"]["route"] == "native_tool_call"
    assert record["score"]["strict_correct_planned_denominator"] == 0
    assert record["tools_executed"] is False
    assert record["provider_response_id"] == "native-response-1"


def test_owner_composes_exact_current_collector_namespace():
    owner = importlib.import_module("owner")
    argv = owner.collector_argv(ROOT / "stage", ROOT / "outputs/attempt-001", 1234.5)
    assert argv[1] == str(ROOT / "driver.py")
    assert argv[5:] == ["--output", str(ROOT / "outputs/attempt-001/rollout"),
                        "--deadline", "1234.5"]
    with pytest.raises(ValueError):
        owner.collector_argv(ROOT / "stage", ROOT / "outputs/attempt-002", 1234.5)
