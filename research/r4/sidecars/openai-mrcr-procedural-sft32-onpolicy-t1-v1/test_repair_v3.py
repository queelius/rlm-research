"""Actual T1 role-audit plus native HTTP regression for attempt-003."""

from __future__ import annotations

import asyncio
import importlib.util
import json
import os
from pathlib import Path
import sys

from aiohttp import web


ROOT = Path(__file__).resolve().parent


def load_repair():
    previous = {name: sys.modules.get(name) for name in ("study_v3", "checkpoint")}
    try:
        for name, filename in (("study_v3", "study_v3.py"), ("checkpoint", "checkpoint.py")):
            spec = importlib.util.spec_from_file_location(name, ROOT / filename)
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            assert spec.loader is not None
            spec.loader.exec_module(module)
        spec = importlib.util.spec_from_file_location("t1_collect_v3_test", ROOT / "collect_v3.py")
        collect = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(collect)
        return collect
    finally:
        for name, module in previous.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module


def test_actual_role_hook_accepts_t1_and_posts_native_request(tmp_path, monkeypatch):
    asyncio.run(_actual_role_hook(tmp_path, monkeypatch))


async def _actual_role_hook(tmp_path, monkeypatch):
    collect = load_repair()
    study = collect.study
    from transformers import AutoTokenizer
    from verifiers.v1.env import RunSlot

    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "")
    monkeypatch.setenv("T1_V3_CPU_KEY", "cpu-fixture-only")
    os.environ["PATH"] = str(study.source().RUNTIME_BIN) + os.pathsep + os.environ.get("PATH", "")
    os.environ.setdefault("VERIFIERS_CACHE_DIR", "/project/alex_phd/cache/verifiers-prime")
    coordinate = study.schedule("train")[0]
    env = study.environment("train")
    task = next(item for item in env.taskset if item.data.name == coordinate["id"])
    tokenizer = AutoTokenizer.from_pretrained(str(study.BASE), local_files_only=True)
    answer = "CPU_T1_ROLE_AND_NATIVE_OK"
    requests = []

    async def provider(request):
        body = await request.json()
        requests.append(body)
        assert request.path == "/inference/v1/generate"
        assert body["sampling_params"]["temperature"] == 1.0
        ids = tokenizer.encode(answer, add_special_tokens=False) + [tokenizer.eos_token_id]
        return web.json_response(
            {
                "request_id": "CPU_T1_V3_1",
                "usage": {
                    "prompt_tokens": len(body["token_ids"]),
                    "completion_tokens": len(ids),
                    "total_tokens": len(body["token_ids"]) + len(ids),
                },
                "choices": [
                    {
                        "token_ids": ids,
                        "finish_reason": "stop",
                        "logprobs": {
                            "content": [
                                {"token": f"token_id:{token}", "logprob": -0.5}
                                for token in ids
                            ]
                        },
                    }
                ],
            }
        )

    app = web.Application()
    app.router.add_post("/inference/v1/generate", provider)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    binding = collect.checkpoint.binding("checkpoint32")
    root = binding["models"][study.ADAPTED_ALIAS]
    endpoint = {
        "model_alias": study.ADAPTED_ALIAS,
        "host": "127.0.0.1",
        "port": site._server.sockets[0].getsockname()[1],
        "api_key_env": "T1_V3_CPU_KEY",
        "base_model": {"path": str(study.BASE)},
        "adapter": {
            "path": root["path"],
            "model_sha256": root["adapter_sha256"],
            "config_sha256": root["config_sha256"],
        },
    }
    try:
        with collect.hooks.installed(), collect.native_checkpoints(
            tmp_path / "native-calls", set(binding["models"])
        ) as native:
            with collect.role_hooks().installed_hooks(binding, tmp_path):
                async with env.serving():
                    episode = await asyncio.wait_for(
                        env.run_slot(RunSlot(task), collect.model_context(endpoint, coordinate)), 180
                    )
        raw = episode.to_record()
    finally:
        await runner.cleanup()

    audits = [json.loads(path.read_text()) for path in (tmp_path / "role-audit").glob("*-result.json")]
    assert len(requests) == len(native) == len(audits) == 1
    assert audits[0]["status"] == "returned"
    assert audits[0]["native_wire_request"]["body"]["sampling_params"]["temperature"] == 1.0
    assert raw["traces"][0]["root_reply"] == answer

