import asyncio
import json
import os
from pathlib import Path
import time

from aiohttp import web

import collect_v2 as c
import protocol_v2 as p
import study_v2 as s


def test_exact_v2_inventory_and_base_alias():
    plan = s.read(s.INPUTS / "ROOT_PLAN.json"); leaf = s.read(s.INPUTS / "LEAF_REQUESTS.json")
    assert len(plan) == 96 and sum(len(v) for v in leaf.values()) == 24
    assert set(leaf) == set(p.ENCODINGS)
    assert {body["model"] for values in leaf.values() for body in values.values()} == {s.BASE_ALIAS}
    assert s.read(s.INPUTS / "BASE_ALIAS_SUPPORT.json")["observed_in_qualified_service"] is True


def test_labels_only_broker_is_positional_and_strict():
    context = s.read(s.INPUTS / "DATA.json")["contexts"][0]
    values = ["neutral"] * 48
    assert list(p.broker(json.dumps(values), context, "labels_only").values()) == values


def test_actual_nonempty_root_episode_through_fake_native_transport(tmp_path, monkeypatch):
    asyncio.run(_root_episode(tmp_path, monkeypatch))


async def _root_episode(tmp_path, monkeypatch):
    from verifiers.v1.envs.single_agent import SingleAgentEnv
    plan = s.read(s.INPUTS / "ROOT_PLAN.json"); row = next(r for r in plan if r["encoding"] == "opaque" and r["policy"] == "supplied")
    context = next(v for v in s.read(s.INPUTS / "PUBLIC.json") if v["id"] == row["context_id"])
    gold = s.read(s.INPUTS / "HOST_GOLD.json")[context["id"]]; predicted = gold["labels"]
    s.ACTIVE_MAPS = {encoding: {v["id"]: ({r["id"]: "neutral" for r in v["records"]}) for v in s.read(s.INPUTS / "PUBLIC.json")} for encoding in p.ENCODINGS}
    s.ACTIVE_MAPS["opaque"][context["id"]] = predicted
    binding = s.binding(); stage = tmp_path / "stage"; stage.mkdir(); s.write(stage / "BINDING.json", binding)
    renderer = s.qnative.stack().native.renderer(); calls = 0
    code = "import json\nfrom map_api import classify_all\nrecords=json.load(open('records.json'))\nlabels=classify_all()\nprint(sum(r['weight'] if labels[r['id']]=='" + row["question"]["relation"] + "' and r['user'] in " + repr(row["question"]["users"]) + " else 0 for r in records))" if row["family"] == "weight" else "import json\nfrom map_api import classify_all\nrecords=json.load(open('records.json'))\nlabels=classify_all()\nprint(sum(labels[r['id']]=='" + row["question"]["relation"] + "' and r['user'] in " + repr(row["question"]["users"]) + " for r in records))"
    answer = gold["answers"][str(row["query_index"])]
    def payload(reply, request_id):
        ids = renderer._tokenizer.encode(reply, add_special_tokens=False) + [151645]
        return {"request_id": request_id, "usage": {"prompt_tokens": 0, "completion_tokens": len(ids), "total_tokens": len(ids)},
            "choices": [{"token_ids": ids, "finish_reason": "stop", "logprobs": {"content": [{"token": f"token_id:{v}", "logprob": -.1} for v in ids]}}]}
    async def generate(request):
        nonlocal calls
        body = await request.json(); assert body["model"] == binding["role_map"]["root"]; calls += 1
        reply = s.qnative.stack().native.tool_action(code) if calls == 1 else "Answer: " + str(answer)
        return web.json_response(payload(reply, f"V2_CPU_ROOT_{calls}"))
    async def models(request):
        return web.json_response({"data": [{"id": alias, "root": model["path"], "parent": s.BASE_ALIAS} for alias, model in binding["models"].items()] + [{"id": s.BASE_ALIAS, "root": s.BASE_ALIAS}]})
    app = web.Application(); app.router.add_post("/inference/v1/generate", generate); app.router.add_get("/v1/models", models)
    runner = web.AppRunner(app); await runner.setup(); site = web.TCPSite(runner, "127.0.0.1", 0); await site.start()
    descriptor = {"host": "127.0.0.1", "port": site._server.sockets[0].getsockname()[1], "api_key_env": "BRIDGE_V2_CPU_KEY",
        "model_alias": binding["role_map"]["root"], "role_binding_sha256": s.sha(stage / "BINDING.json"),
        "adapter": {"path": binding["models"][binding["role_map"]["root"]]["path"], "model_sha256": binding["models"][binding["role_map"]["root"]]["adapter_sha256"], "config_sha256": binding["models"][binding["role_map"]["root"]]["config_sha256"]},
        "base_model": {"path": s.BASE_ALIAS, "manifest_sha256": "19619b44b0bd30bf5debe0960e6dfd6acc5be8287c581727456aa5d17699c18f"}}
    monkeypatch.setenv("BRIDGE_V2_CPU_KEY", "cpu-only"); monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY", "cpu-only")
    monkeypatch.setattr(s, "verify", lambda: {"identity": "cpu"}); monkeypatch.setattr(s, "runtime", lambda: None)
    try:
        module = c.root_implementation()
        await module.episode(row, context, binding, descriptor, tmp_path / "episode", time.time() + 180, "free")
        assert (tmp_path / "episode/RESULT.json").exists() and calls == 2
    finally:
        await runner.cleanup()
