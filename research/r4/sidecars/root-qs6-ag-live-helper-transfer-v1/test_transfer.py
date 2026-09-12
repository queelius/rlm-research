"""Focused observable contract fixtures, no GPU or scientific model calls."""

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent


def load_protocol():
    path = ROOT / "protocol.py"
    assert path.exists(), "live AG serialization/merge contract is not implemented"
    spec = importlib.util.spec_from_file_location("ag_transfer_protocol_fixture", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_live_full16_contract_preserves_ids_and_rejects_bad_child_map():
    """A permissive ID join or a leaked public gold field must fail this fixture."""
    p = load_protocol()
    records = [dict(id=f"r{i:02}", text=f"Article {i}", user=f"u{i % 4}", weight=i % 7 + 1)
               for i in range(16)]
    serialized = p.request_for(records)
    assert p.match_request(serialized, records) is True
    assert p.match_request(serialized.replace("Article 2", "Different 2"), records) is False
    assert "weight" not in serialized and '"user"' not in serialized
    ids = [row["id"] for row in records]
    maps = [dict(zip(ids[i:i + 4], ["World", "Sports", "Business", "Sci/Tech"]))
            for i in range(0, 16, 4)]
    merged = p.merge_maps(maps, ids)
    assert list(merged) == ids and merged["r15"] == "Sci/Tech"
    schema = p.schema(ids[:4])
    wire = json.loads(json.dumps(schema, separators=(",", ":")))
    assert list(wire["properties"]) == ["r00", "r01", "r02", "r03"]
    assert wire["properties"]["r00"]["enum"] == ["World", "Sports", "Business", "Sci/Tech"]
    with pytest.raises(ValueError):
        p.merge_maps([*maps[:3], {**maps[3], "unknown": "World"}], ids)
    with pytest.raises(ValueError):
        p.strict_map('{"r00":"World","r00":"Business"}', ["r00"])
    with pytest.raises(ValueError):
        p.strict_map('{"r00":"entity"}', ["r00"])
    # Truth has no influence on runtime bytes; host-only aggregate is transparent.
    assert p.aggregate(records, merged, {"operator": "count", "target": "World"}) == 4
    assert p.aggregate(records, merged, {"operator": "weight_sum", "target": "Sports"}) == 18


@pytest.mark.parametrize("arm", ["no_child_python", "c32"])
def test_real_collector_container_and_four_native_label_maps(tmp_path, monkeypatch, arm):
    """Catch wrong task identities, child wire order, fake wrapper likelihood, or lost root mapping."""
    import asyncio
    asyncio.run(_actual_collection(tmp_path, monkeypatch, arm))


async def _actual_collection(tmp_path, monkeypatch, arm):
    from aiohttp import web
    import collect
    import study

    monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY", "cpu-fixture-no-science")
    row = study.plan(arm)[0]
    binding = study.read(study.INPUTS / "BINDING_c32.json")
    original_plan = study.plan
    monkeypatch.setattr(study, "plan", lambda value: [row] if value == arm else original_plan(value))
    monkeypatch.setattr(study, "verify", lambda: {"identity": "CPU fixture"})
    # READY is read for a provenance hash only by the collector. A temporary path facade
    # avoids inventing a production READY before qualification.
    original_sha = study.sha
    monkeypatch.setattr(study, "sha", lambda path: "CPU_UNSEALED" if Path(path) == ROOT / "READY.json" else original_sha(path))
    native = study.sources()[1].qs.qnative().stack().native
    renderer = native.renderer()
    root_alias = binding["role_map"]["root"]
    child_alias = binding["fixed_child"]
    model = str(study.sources()[2].MODEL)
    code = ("import json\nfrom batch_contract import request_for, strict_map\n"
            "records=json.load(open('records.json'))\n"
            "result=await rlm(request_for(records))\n"
            "labels=strict_map(result.answer,[r['id'] for r in records])\n"
            "print(len(labels))")
    if arm == "no_child_python":
        code = "import json\nrecords=json.load(open('records.json'))\nprint(len(records))"
    requests, root_count = [], 0

    async def models(_request):
        return web.json_response({"data": [{"id": alias, "root": info["path"], "parent": model}
                                          for alias, info in binding["models"].items()]})

    async def generate(request):
        nonlocal root_count
        body = await request.json()
        requests.append(body)
        if body["model"] == root_alias:
            root_count += 1
            assert body["sampling_params"].get("structured_outputs") is None
            text = native.tool_action(code) if root_count == 1 else "Answer: 0"
        else:
            assert body["model"] == child_alias
            schema = body["sampling_params"]["structured_outputs"]["json"]
            ids = schema["required"]
            assert len(ids) == 4 and list(schema["properties"]) == ids
            assert schema["properties"][ids[0]]["enum"] == ["World", "Sports", "Business", "Sci/Tech"]
            assert body["sampling_params"]["temperature"] == 0
            assert len(body["token_ids"]) + 1024 <= 8192
            text = json.dumps(dict(zip(ids, ["World", "Sports", "Business", "Sci/Tech"])), separators=(",", ":"))
        ids = renderer._tokenizer.encode(text, add_special_tokens=False) + [151645]
        return web.json_response({"request_id": f"AG_LIVE_CPU_{len(requests)}", "model": body["model"],
            "usage": {"prompt_tokens": len(body["token_ids"]), "completion_tokens": len(ids),
                      "total_tokens": len(body["token_ids"]) + len(ids), "prompt_tokens_details": {"cached_tokens": 0}},
            "choices": [{"token_ids": ids, "finish_reason": "stop", "logprobs": {"content": [
                {"token": f"token_id:{token}", "logprob": -.1} for token in ids]}}]})

    app = web.Application()
    app.router.add_get("/v1/models", models)
    app.router.add_post("/inference/v1/generate", generate)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]
    descriptor = {"host": "127.0.0.1", "port": port, "api_key_env": "STRICT_RLM_CALIBRATION_API_KEY",
                  "model_alias": root_alias, "base_model": {"path": model}}
    study.write_x(tmp_path / "ENDPOINT.json", descriptor)
    study.write_x(tmp_path / "BINDING.json", binding)
    try:
        await collect.run(arm, tmp_path / "ENDPOINT.json", tmp_path / "BINDING.json",
                          tmp_path / "rollout", __import__("time").time() + 100)
    finally:
        await runner.cleanup()
    output = tmp_path / "rollout"
    records = [study.read(path) for path in (output / "episodes").glob("*.json")]
    assert len(records) == 1
    record = records[0]
    assert record["derived"]["available"], record
    assert record["derived"]["status"] == "valid_final", record
    assert record["derived"]["root_native_mapping"]["complete"], record
    assert record["derived"]["root_native_mapping"]["root_actions"] == 2
    expected_helper = 4 if arm == "c32" else 0
    assert record["derived"]["helper"]["records"] == (16 if arm == "c32" else 0)
    assert len(requests) == 2 + expected_helper and root_count == 2
    calls = [study.read(path) for path in (output / "helper-calls").glob("*.json")]
    assert len(calls) == expected_helper and all(call["status"] == "returned_valid" for call in calls)
    wrappers = [study.read(path) for path in (output / "helper-wrappers").glob("*.json")]
    assert len(wrappers) == (1 if arm == "c32" else 0)
    if wrappers:
        assert wrappers[0]["logical_wrapper_is_model_sample"] is False
        assert wrappers[0]["wrapper_native_tokens"] is None
    # Generated code is the authored fixture, never an automatic aggregate implementation.
    assert record["derived"]["parsed_answer"] == 0
    import metrics
    root_calls = [study.read(path) for path in (output / "root-native").glob("*-result.json")]
    summary = metrics.summarize(records, root_calls, calls)
    assert summary["physical_costs"]["root"]["attempts"] == 2
    assert summary["physical_costs"]["helper_B4"]["attempts"] == expected_helper
    assert summary["physical_costs"]["helper_B4"]["completion_tokens_unknown_calls"] == 0
    assert summary["complete"] is False  # One authored CPU episode is not the fixed48 study.
