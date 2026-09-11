"""Focused CPU contracts; only the network boundary is faked."""

import asyncio
import importlib.util
import json
from copy import deepcopy
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parent


def driver():
    assert (ROOT / "driver.py").exists(), "correspondence implementation missing"
    loader = importlib.util.spec_from_file_location(
        "correspondence_test_driver", ROOT / "driver.py"
    )
    mod = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(mod)
    return mod


def context(arm="anonymous"):
    labels = ["human being", "entity", "location", "numeric value"]
    return {
        "arm": arm,
        "order": [2, 3, 0, 1],
        "records": [
            {
                "id": f"q{i + 1:04d}",
                "question": f"Question {i + 1}?",
                "gold_label": g,
                "record_index": i + 1,
                "question_group_sha256": str(i),
                "source_line_1based": i + 11,
            }
            for i, g in enumerate(labels)
        ],
    }


def test_first256_preserve_declared_validation_manifest_order_and_pairing():
    d = driver()
    for name, n in [("representation", 24), ("rotation", 32)]:
        design = d.build_spec(name)["design"]
        assert len(design["plan"]) == n and len(design["contexts"]) == 4
        records = [r for c in design["contexts"] for r in c["records"]]
        assert [r["record_index"] for r in records] == list(range(1, 257))
        assert (
            records[0]["question_group_sha256"]
            == "004805d756aab77dce64b07dfe7382553200b1b50fb5f1f80e0074c09b84119e"
        )
        assert records[0]["source_line_1based"] == 625
        assert len({r["question_group_sha256"] for r in records}) == 256
        assert {r["seed"] for r in design["plan"]} == {981261401, 981261402}
        assert len({r["id"] for r in design["plan"]}) == n


def test_requests_preserve_native_contract_and_echo_strings_are_not_grammar_constants():
    d = driver()
    design = d.build_spec("representation")["design"]
    rows = {r["arm"]: r for r in design["plan"] if r["context_index"] == 0 and r["repeat"] == 0}
    for arm, row in rows.items():
        body = d.make_request(design, row)
        assert body["messages"][0] == design["contract"]["system_message"]
        assert body["tools"] == design["contract"]["tools"]
        assert body["temperature"] == 0.5 and body["return_token_ids"] is True
        assert body["max_tokens"] == 3072 and "logprobs" not in body
        assert design["definitions"] in body["messages"][1]["content"]
        assert "gold_label" not in json.dumps(body)
        schema = body["structured_outputs"]["json"]
        if arm == "anonymous":
            assert schema["minItems"] == schema["maxItems"] == 64
        else:
            assert len(schema["required"]) == 64 and schema["additionalProperties"] is False
        if arm == "echo":
            value = schema["properties"]["q0001"]
            assert value["properties"]["question"] == {"type": "string"}
            assert value["required"] == ["question", "label"]
            assert "What" not in json.dumps(schema)
    anonymous = d.make_request(design, rows["anonymous"])
    assert anonymous["messages"][1]["content"].startswith(
        design["contract"]["baseline_user_prefix"]
    )


def test_rotation_scoring_inverts_declared_permutation_without_voting():
    d = driver()
    result = d.score_response('["location","numeric value","human being","entity"]', context())
    assert result["predictions"] == ["human being", "entity", "location", "numeric value"]
    assert result["strict_correct"] == 4 and result["schema_valid"]
    assert result["input_positions"] == [3, 4, 1, 2]


def test_rotation_request_payload_and_positions_match_declared_source_order():
    d = driver()
    design = d.build_spec("rotation")["design"]
    source = design["contexts"][0]["records"]
    rows = [r for r in design["plan"] if r["context_index"] == 0 and r["repeat"] == 0]
    observed = []
    for row in rows:
        body = d.make_request(design, row)
        prefix = design["contract"]["baseline_user_prefix"] + "\n" + design["definitions"] + "\n"
        questions = json.loads(body["messages"][1]["content"].removeprefix(prefix))
        offset = row["offset"]
        assert questions == [r["question"] for r in source[offset:] + source[:offset]]
        assert body["max_tokens"] == 1024
        observed.append(questions.index(source[0]["question"]) + 1)
    assert sorted(observed) == [1, 17, 33, 49]


def test_host_gold_mutation_cannot_change_dispatched_request():
    d = driver()
    design = d.build_spec("representation")["design"]
    changed = deepcopy(design)
    for batch in changed["batches"]:
        for record in batch["gold"]["records"]:
            record["gold_label"] = "HOST_ONLY_SENTINEL"
            record["coarse"] = "HOST_ONLY_SENTINEL"
    for row in design["plan"][:3]:
        assert d.make_request(design, row) == d.make_request(changed, row)


def test_frozen_json_round_trip_preserves_physical_tool_key_order():
    d = driver()
    spec = d.build_spec("representation")
    frozen = json.loads(json.dumps(spec, sort_keys=True))
    for row in spec["design"]["plan"][:3]:
        before = d.make_request(spec["design"], row)
        after = d.make_request(frozen["design"], row)
        assert json.dumps(before["tools"]) == json.dumps(after["tools"])
        assert json.dumps(before["messages"]) == json.dumps(after["messages"])


@pytest.mark.parametrize(
    "content",
    [
        '{"q0001":"human being","q0001":"human being","q0002":"entity","q0003":"location","q0004":"numeric value"}',
        '{"q0001":"human being","q0002":"entity","q0003":"location"}',
        '["human being","entity","location","numeric value"]',
        'not JSON: {"q0001":"human being"}',
    ],
)
def test_wrong_or_duplicate_index_contract_never_repairs_predictions(content):
    result = driver().score_response(content, context("indexed"))
    assert not result["schema_valid"]
    assert result["predictions"] == [None] * 4 and result["aligned_records"] == 0


def test_copy_fidelity_is_separate_from_semantic_and_enum_scoring():
    d = driver()
    c = context("echo")
    raw = {r["id"]: {"question": r["question"], "label": r["gold_label"]} for r in c["records"]}
    raw["q0002"]["question"] = "Wrong copied question?"
    score = d.score_response(json.dumps(raw), c)
    assert score["schema_valid"] and score["strict_correct"] == 4
    assert score["copy_exact"] == [True, False, True, True]
    raw["q0003"]["label"] = "LOC"
    score = d.score_response(json.dumps(raw), c)
    assert not score["schema_valid"] and score["strict_correct"] == 3
    assert score["predictions"][2] == "LOC"


def test_real_collector_dispatches_each_representation_and_keeps_raw_capture(tmp_path):
    d = driver()
    s = d.build_spec("representation")
    s["design"]["plan"] = s["design"]["plan"][:3]
    s["design"]["coordinates"] = s["design"]["coordinates"][:3]
    (tmp_path / "calls").mkdir()
    (tmp_path / "coordinates").mkdir()
    seen = []

    def reply(request):
        body = json.loads(request.content)
        seen.append(body)
        ids = (
            d.tokenizer()
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
                        "message": {"content": '["entity"]'},
                        "token_ids": [1, 2],
                    }
                ],
                "usage": {
                    "prompt_tokens": len(ids),
                    "completion_tokens": 2,
                    "total_tokens": len(ids) + 2,
                    "prompt_tokens_details": {"cached_tokens": 0},
                },
            },
        )

    async def execute():
        async with httpx.AsyncClient(transport=httpx.MockTransport(reply)) as client:
            return await d.collect_calls(client, "http://cpu.invalid/v1", s, tmp_path)

    records, reason = asyncio.run(execute())
    assert reason is None and len(records) == 3
    assert sorted(b["structured_outputs"]["json"]["type"] for b in seen) == [
        "array",
        "object",
        "object",
    ]
    assert all(not r["score"]["schema_valid"] for r in records)
    assert len(list((tmp_path / "calls").glob("*.json"))) == 3
    assert all(r["raw_response"]["prompt_token_ids"] for r in records)
    assert all(r["usage"]["completion_tokens"] == 2 for r in records)
    assert all(r["capture"]["tools_executed"] is False for r in records)


def test_binding_rejects_other_weights_and_live_alias_path_mismatch():
    d = driver()
    descriptor = json.loads(d.HISTORICAL_SELECTED.read_text())
    d.validate_endpoint(descriptor)
    bad = deepcopy(descriptor)
    bad["adapter"]["model_sha256"] = "wrong"
    with pytest.raises(ValueError, match="old selected"):
        d.validate_endpoint(bad)
    cards = {
        "data": [
            {
                "id": descriptor["model_alias"],
                "root": "/wrong",
                "parent": descriptor["base_model"]["path"],
            }
        ]
    }
    with pytest.raises(ValueError, match="live alias"):
        d.validate_live_models(descriptor, cards)


def test_wrong_alias_remains_infrastructure_null_but_retains_observed_cost(tmp_path):
    d = driver()
    s = d.build_spec("representation")
    s["design"]["plan"] = s["design"]["plan"][:1]
    s["design"]["coordinates"] = s["design"]["coordinates"][:1]
    (tmp_path / "calls").mkdir()
    (tmp_path / "coordinates").mkdir()
    seen = []

    def reply(request):
        seen.append(request)
        return httpx.Response(
            200,
            json={
                "model": "wrong-alias",
                "choices": [],
                "usage": {
                    "prompt_tokens": 99,
                    "completion_tokens": 11,
                    "prompt_tokens_details": {"cached_tokens": 7},
                },
            },
        )

    async def execute():
        async with httpx.AsyncClient(transport=httpx.MockTransport(reply)) as client:
            return await d.collect_calls(client, "http://cpu.invalid/v1", s, tmp_path)

    records, reason = asyncio.run(execute())
    assert reason == "request_error" and len(seen) == 1
    result = d.score_coordinate(s["design"], s["design"]["coordinates"][0], records)
    assert result["model_completed"] is False
    assert result["counts"]["human being"]["strict"] is None
    assert result["usage"]["logical_input_tokens"] == 99
    assert result["usage"]["completion_tokens"] == 11
    assert result["usage"]["uncached_input_tokens"] == 92
