"""Authored native composition fixture; no sampled code is executed."""
import asyncio
import json
import time

from aiohttp import web

import id_collect as collect
import id_study as study


def test_actual_composed_episode_uses_exact_new_prompt_and_control_prefix(tmp_path, monkeypatch):
    monkeypatch.setenv("DOSE_INTERMEDIATE_CPU_KEY", "CPU_FIXTURE_NOT_CREDENTIAL")
    monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY", "CPU_FIXTURE_NOT_CREDENTIAL")

    async def fixture():
        row = study.read(study.ROOT / "inputs/FREE_PLAN.json")[0]
        context = next(item for item in study.read(study.ROOT / "inputs/PUBLIC.json")
                       if item["id"] == row["context_id"])
        binding = study.binding("sft18")
        renderer = study.stack().native.renderer()
        tokenizer = renderer._tokenizer
        roots, children = [], []
        expected = study.answer(context["records"],
                                {record["id"]: row["target"] for record in context["records"]}, row)
        code = (
            'import json\nfrom rlm.api import run as rlm\n'
            'from batch_contract import request_for, strict_map\n'
            'records=json.load(open("records.json"))\n'
            'child=await rlm(request_for(records))\n'
            'labels=strict_map(child.answer,[r["id"] for r in records])\n'
            f'answer={expected}\nprint(answer)'
        )

        async def provider(request):
            body = await request.json()
            if body["model"] == binding["role_map"]["root"]:
                roots.append(body)
                if len(roots) == 1:
                    assert body["token_ids"] == study.read(
                        study.ROOT / "inputs/PROMPTS_ACCURATE.json")[row["id"]]["token_ids"]
                    reply = study.stack().native.tool_action(code)
                else:
                    reply = f"Answer: {expected}"
            else:
                children.append(body)
                ids = body["sampling_params"]["structured_outputs"]["json"]["required"]
                reply = json.dumps({key: row["target"] for key in ids})
            ids = tokenizer.encode(reply, add_special_tokens=False) + [151645]
            return web.json_response({
                "request_id": f"CPU_{len(roots) + len(children)}",
                "usage": {"prompt_tokens": len(body["token_ids"]), "completion_tokens": len(ids)},
                "choices": [{"token_ids": ids, "finish_reason": "stop",
                             "logprobs": {"content": [
                                 {"token": f"token_id:{token}", "logprob": -.5} for token in ids]}}],
            })

        async def models(_request):
            return web.json_response({"data": [
                {"id": alias, "root": model["path"], "max_model_len": 8192}
                for alias, model in binding["models"].items()]})

        app = web.Application()
        app.router.add_post("/inference/v1/generate", provider)
        app.router.add_get("/v1/models", models)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "127.0.0.1", 0)
        await site.start()
        descriptor = {"host": "127.0.0.1", "port": site._server.sockets[0].getsockname()[1],
                      "api_key_env": "DOSE_INTERMEDIATE_CPU_KEY"}
        try:
            with study.aliases({"od_study": study, "od_protocol": study.protocol(),
                                "od_binding": study}):
                await collect.implementation().episode(row, context, binding, descriptor,
                                                       tmp_path / "native", time.time() + 120, "free")
            result = study.read(tmp_path / "native/RESULT.json")
            assert result["available"] and result["final_branch_token_identity_verified"]
            assert len(roots) == 2 and len(children) == 1
        finally:
            await runner.cleanup()

    asyncio.run(fixture())
