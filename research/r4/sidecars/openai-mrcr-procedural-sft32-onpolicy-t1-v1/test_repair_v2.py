"""Regression for the additive T1 transport repair.

The provider is local CPU-only, but the request crosses the real environment,
interception server, TrainClient renderer, and native HTTP route.
"""

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
    previous = {name: sys.modules.get(name) for name in ("study_v2", "checkpoint")}
    try:
        for name, filename in (("study_v2", "study_v2.py"), ("checkpoint", "checkpoint.py")):
            spec = importlib.util.spec_from_file_location(name, ROOT / filename)
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            assert spec.loader is not None
            spec.loader.exec_module(module)
        spec = importlib.util.spec_from_file_location("t1_collect_v2_test", ROOT / "collect_v2.py")
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


def test_context_is_proven_context_with_only_temperature_changed():
    collect = load_repair()
    endpoint = {
        "model_alias": collect.study.ADAPTED_ALIAS,
        "host": "127.0.0.1",
        "port": 1,
        "api_key_env": "T1_V2_CPU_KEY",
        "base_model": {"path": str(collect.study.BASE)},
    }
    coordinate = collect.study.schedule("train")[0]
    prior = collect.proven_model_context(endpoint, coordinate)
    repaired = collect.model_context(endpoint, coordinate)
    assert repaired.model == prior.model
    assert repaired.client == prior.client
    prior_sampling = prior.sampling.model_dump()
    repaired_sampling = repaired.sampling.model_dump()
    assert prior_sampling.pop("temperature") == 0.5
    assert repaired_sampling.pop("temperature") == 1.0
    assert repaired_sampling == prior_sampling


def test_actual_run_slot_posts_native_tokens_to_root_route(tmp_path, monkeypatch):
    asyncio.run(_actual_run_slot(tmp_path, monkeypatch))


async def _actual_run_slot(tmp_path, monkeypatch):
    collect = load_repair()
    study = collect.study
    from transformers import AutoTokenizer
    from verifiers.v1.env import RunSlot

    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "")
    monkeypatch.setenv("T1_V2_CPU_KEY", "cpu-fixture-only")
    os.environ["PATH"] = str(study.source().RUNTIME_BIN) + os.pathsep + os.environ.get("PATH", "")
    os.environ.setdefault("VERIFIERS_CACHE_DIR", "/project/alex_phd/cache/verifiers-prime")

    coordinate = study.schedule("train")[0]
    env = study.environment("train")
    task = next(item for item in env.taskset if item.data.name == coordinate["id"])
    tokenizer = AutoTokenizer.from_pretrained(str(study.BASE), local_files_only=True)
    answer = "CPU_T1_NATIVE_ROUTE_OK"
    requests = []

    async def provider(request):
        assert request.path == "/inference/v1/generate"
        assert request.headers.get("Authorization") == "Bearer cpu-fixture-only"
        body = await request.json()
        requests.append(body)
        assert body["model"] == study.ADAPTED_ALIAS
        assert body["sampling_params"]["temperature"] == 1.0
        ids = tokenizer.encode(answer, add_special_tokens=False) + [tokenizer.eos_token_id]
        return web.json_response(
            {
                "request_id": "CPU_T1_V2_1",
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
    endpoint = {
        "model_alias": study.ADAPTED_ALIAS,
        "host": "127.0.0.1",
        "port": site._server.sockets[0].getsockname()[1],
        "api_key_env": "T1_V2_CPU_KEY",
        "base_model": {"path": str(study.BASE)},
    }
    try:
        with collect.hooks.installed(), collect.native_checkpoints(
            tmp_path / "native-calls", {study.ADAPTED_ALIAS}
        ) as native:
            async with env.serving():
                episode = await asyncio.wait_for(
                    env.run_slot(RunSlot(task), collect.model_context(endpoint, coordinate)), 180
                )
        raw = episode.to_record()
    finally:
        await runner.cleanup()

    assert len(requests) == len(native) == 1
    expected_prefix = study.read(study.input_dir("train") / "PREFIXES.json")[coordinate["id"]][
        "token_ids"
    ]
    assert requests[0]["token_ids"] == expected_prefix
    assert native[0]["status"] == "returned"
    assert raw["traces"][0]["root_reply"] == answer

