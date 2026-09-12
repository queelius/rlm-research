from __future__ import annotations

import asyncio
import importlib.util
import json
from pathlib import Path
import sys

import pytest
from aiohttp import web


ROOT = Path(__file__).resolve().parent


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_fixed_schedule_and_input_bytes() -> None:
    study = load("study")
    schedule = study.schedule()
    assert len(schedule) == 16
    assert [row["seed"] for row in schedule] == list(range(202609210000, 202609210016))
    assert len({row["id"] for row in schedule}) == 16
    assert [row["record_id"] for row in schedule] == [row["id"] for row in study.records()]
    report = study.prepare_inputs()
    assert report == {"records": 16, "episodes": 16, "contexts": 16,
                      "prefixes": 16, "schedule_sha256": study.digest(schedule)}
    tasks = study.read(study.INPUTS / "tasks.json")
    public = study.read(study.INPUTS / "PUBLIC.json")
    assert len(tasks) == len(public["plan"]) == 16
    for row, task in zip(study.records(), tasks, strict=True):
        assert task["document_sha256"] == row["prompt_json_sha256"]
        assert Path(row["prompt_json_path"]).read_bytes() == (
            study.INPUTS / "contexts" / f"{row['prompt_json_sha256']}.json"
        ).read_bytes()
        assert Path(row["final_question_path"]).read_text() in task["prompt"]
        assert row["prompt_json_path"] not in task["prompt"]


def test_checkpoint_and_terminal_hook_contracts() -> None:
    study = load("study")
    previous = sys.modules.get("study")
    sys.modules["study"] = study
    try:
        checkpoint = load("checkpoint")
        hooks = study.terminal_hooks()
    finally:
        if previous is None:
            sys.modules.pop("study", None)
        else:
            sys.modules["study"] = previous
    assert hooks.qualify()["condition"] == "terminal-strip-disabled"
    for arm in ("base", "checkpoint32"):
        binding = checkpoint.binding(arm)
        assert binding["fixed_child"] == study.BASE_ALIAS
        assert binding["role_map"]["children"] == [study.BASE_ALIAS]
        assert binding["role_map"]["root"] == (
            study.BASE_ALIAS if arm == "base" else study.ADAPTED_ALIAS
        )


def test_real_environment_setup_uses_frozen_context() -> None:
    study = load("study")
    study.prepare_inputs()
    env = study.environment()
    task = next(iter(env.taskset))

    class Runtime:
        def __init__(self):
            self.values = {}

        async def write(self, path, payload):
            self.values[path] = payload

        async def read(self, path):
            return self.values[path]

    runtime = Runtime()
    asyncio.run(task.setup(None, runtime))
    assert "/context.json" in runtime.values
    assert len(runtime.values["/context.json"]) >= 80_000


def test_collector_enters_exact_hook_and_preserves_real_run_signature(monkeypatch, tmp_path) -> None:
    study = load("study")
    previous = {name: sys.modules.get(name) for name in ("study", "checkpoint")}
    sys.modules["study"] = study
    sys.modules["checkpoint"] = load("checkpoint")
    try:
        collect = load("collect")
    finally:
        for name, value in previous.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value
    events = []

    class Installed:
        def __enter__(self):
            events.append("enter")
            return {"condition": "terminal-strip-disabled", "general_lossless_parser": False}

        def __exit__(self, *_):
            events.append("exit")

    monkeypatch.setattr(collect.hooks, "installed", lambda: Installed())

    async def fake_run(phase, arm, endpoint, output, deadline):
        assert phase == "long"
        assert arm == "base"
        assert endpoint == tmp_path / "endpoint.json"
        assert deadline == 42.0
        assert events == ["enter"]
        output.mkdir(parents=True)
        return 0

    monkeypatch.setattr(collect.source, "run", fake_run)
    output = tmp_path / "science"
    assert asyncio.run(collect.run("long", "base", tmp_path / "endpoint.json", output, 42.0)) == 0
    assert events == ["enter", "exit"]
    assert json.loads((output / "TERMINAL_STRIP_CONTRACT.json").read_text())["condition"] == (
        "terminal-strip-disabled"
    )


def test_actual_long_run_slot_hits_native_provider_and_preserves_prefix(monkeypatch, tmp_path) -> None:
    async def run() -> None:
        from transformers import AutoTokenizer
        from verifiers.v1.env import RunSlot

        study = load("study")
        study.prepare_inputs()
        previous = {name: sys.modules.get(name) for name in ("study", "checkpoint")}
        sys.modules["study"] = study
        sys.modules["checkpoint"] = load("checkpoint")
        try:
            collect = load("collect")
        finally:
            for name, value in previous.items():
                if value is None:
                    sys.modules.pop(name, None)
                else:
                    sys.modules[name] = value
        source = collect.source
        coordinate = study.schedule()[0]
        env = study.environment()
        task = next(item for item in env.taskset if item.data.name == coordinate["id"])
        gold = study.read(study.INPUTS / "HOST_GOLD.json")[coordinate["record_id"]]
        tokenizer = AutoTokenizer.from_pretrained(str(study.BASE), local_files_only=True)
        reply = gold["answer"]
        requests = []

        async def provider(request):
            body = await request.json()
            requests.append(body)
            ids = tokenizer.encode(reply, add_special_tokens=False) + [tokenizer.eos_token_id]
            return web.json_response(
                {
                    "request_id": "CPU_LONG_DIRECT_FINAL",
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
            "model_alias": study.BASE_ALIAS,
            "base_model": {"path": str(study.BASE)},
            "adapter": None,
            "host": "127.0.0.1",
            "port": site._server.sockets[0].getsockname()[1],
            "api_key_env": "MRCR_LONG_CPU_KEY",
        }
        monkeypatch.setenv("MRCR_LONG_CPU_KEY", "not-a-real-secret")
        monkeypatch.setenv(
            "PATH", str(study.source().RUNTIME_BIN) + os.pathsep + os.environ.get("PATH", "")
        )
        monkeypatch.setenv("VERIFIERS_CACHE_DIR", "/project/alex_phd/cache/verifiers-prime")
        try:
            with collect.hooks.installed(), source.native_checkpoints(
                tmp_path / "native-calls", {study.BASE_ALIAS}
            ) as native:
                async with env.serving():
                    episode = await asyncio.wait_for(
                        env.run_slot(RunSlot(task), source.model_context(endpoint, coordinate)), 180
                    )
        finally:
            await runner.cleanup()
        raw = episode.to_record()
        prefix = study.read(study.INPUTS / "PREFIXES.json")[coordinate["id"]]["token_ids"]
        derived = source.inspect_trace(raw, gold, native, prefix)
        assert len(requests) == len(native) == 1
        assert requests[0]["token_ids"] == prefix
        assert derived["initial_root_prefix_verified"] is True
        assert derived["native_mapping_complete"] is True
        assert derived["raw_exact"] is True
        assert derived["reward"] == 1.0

    import os

    asyncio.run(run())


def test_owner_has_two_independent_fixed_stages() -> None:
    study = load("study")
    previous = {name: sys.modules.get(name) for name in ("study", "checkpoint")}
    sys.modules["study"] = study
    sys.modules["checkpoint"] = load("checkpoint")
    try:
        owner = load("owner")
    finally:
        for name, value in previous.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value
    assert set(owner.STAGES) == {"base", "checkpoint32"}
    assert {value["output"].name for value in owner.STAGES.values()} == {
        "base-001", "checkpoint32-001"
    }
    assert study.SCIENCE_SECONDS == 900
    assert study.OWNER_SECONDS == 1100
    with pytest.raises(ValueError, match="exact 1100-second"):
        owner.execute("base", owner.STAGES["base"]["output"], 1099)
