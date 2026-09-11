"""Additive V2: full raw evidence stays in the native session tree, not task cwd."""
import asyncio
import json
from pathlib import Path
import time


def test_v2_overlay_uses_session_log_and_no_task_raw_file():
    import bv_overlay_v2 as overlay

    patched = overlay.patch_engine(overlay.composed_engine_source())
    assert "self.session.log_tool_result(turn, tool_name, result, duration)" in patched
    assert "self.session.log(_observation_record)" in patched
    assert ".observation_view.jsonl" not in patched
    assert "'raw_content'" not in patched
    assert "retained_payload_bytes" in patched
    compile(patched, "<bounded-view-v2-test>", "exec")


def test_v2_actual_native_harvests_session_private_raw_after_clipped_policy_view(
    tmp_path, monkeypatch
):
    import bv_collect_v2 as collect
    import bv_study_v2 as study
    from aiohttp import web

    monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY", "CPU_FIXTURE")
    monkeypatch.setenv("BOUNDED_VIEW_CPU_KEY", "CPU_FIXTURE")

    async def fixture():
        row = next(
            r
            for r in study.read(study.ROOT / "inputs/FREE_PLAN.json")
            if r["return_arm"] == "B" and r["view_bytes"] == 4096 and r["records"] == 128
        )
        context = next(
            x for x in study.read(study.ROOT / "inputs/PUBLIC.json") if x["id"] == row["context_id"]
        )
        binding = study.binding()
        native = study.stack().native
        tokenizer = native.renderer()._tokenizer
        roots = []
        code = 'print("A"*12000)'

        async def provider(request):
            body = await request.json()
            roots.append(body)
            if len(roots) == 1:
                reply = native.tool_action(code)
            else:
                decoded = tokenizer.decode(body["token_ids"], skip_special_tokens=False)
                assert "Warning: truncated output" in decoded and "A" * 6000 not in decoded
                reply = "Answer: 0"
            ids = tokenizer.encode(reply, add_special_tokens=False) + [151645]
            return web.json_response(
                {
                    "request_id": "BV2_CPU",
                    "usage": {"prompt_tokens": len(body["token_ids"]), "completion_tokens": len(ids)},
                    "choices": [
                        {
                            "token_ids": ids,
                            "finish_reason": "stop",
                            "logprobs": {
                                "content": [
                                    {"token": f"token_id:{value}", "logprob": -0.5} for value in ids
                                ]
                            },
                        }
                    ],
                }
            )

        async def models(request):
            return web.json_response(
                {
                    "data": [
                        {"id": alias, "root": model["path"], "max_model_len": 8192}
                        for alias, model in binding["models"].items()
                    ]
                }
            )

        app = web.Application()
        app.router.add_post("/inference/v1/generate", provider)
        app.router.add_get("/v1/models", models)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "127.0.0.1", 0)
        await site.start()
        descriptor = {
            "host": "127.0.0.1",
            "port": site._server.sockets[0].getsockname()[1],
            "api_key_env": "BOUNDED_VIEW_CPU_KEY",
        }
        try:
            await collect.implementation().episode(
                row, context, binding, descriptor, tmp_path / "native", time.time() + 120, "free"
            )
            episode = study.read(tmp_path / "native/EPISODE.json")
            audit = json.loads(episode["traces"][0]["info"]["bounded_observation_view_v2"]["raw"])
            raw = [x for x in audit if x.get("type") == "tool_result"]
            views = [x for x in audit if x.get("type") == "bounded_observation_view"]
            assert raw and raw[0]["content"].startswith("A" * 4096)
            assert views and views[0]["clipped"] and views[0]["retained_payload_bytes"] == 4096
            assert not (tmp_path / "native/.observation_view.jsonl").exists()
        finally:
            await runner.cleanup()

    asyncio.run(fixture())


def test_v2_owner_targets_attempt002_and_v2_collector():
    import bv_owner_v2 as owner
    import bv_study_v2 as study

    argv = owner.collector_argv(Path("/CPU/stage"), Path("/CPU/output"), 123.0)
    assert study.ATTEMPT.name == "attempt-002"
    assert Path(argv[1]).name == "bv_collect_v2.py"
