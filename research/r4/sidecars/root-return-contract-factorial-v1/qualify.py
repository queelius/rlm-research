"""Two real rootless/native CPU fixture episodes; no actual model or GPU calls."""

import argparse
import asyncio
import json
import os
from pathlib import Path

from aiohttp import web

import study as s

c, capture = s.c, s.native.capture


async def qualify(output):
    from renderers import Qwen3RendererConfig, create_renderer
    from renderers.base import load_tokenizer
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv, SingleAgentEnvConfig

    if output.exists():
        raise ValueError("CPU qualification requires an unused directory")
    output.mkdir(parents=True)
    renderer = create_renderer(load_tokenizer(c.pilot_recipe()["base_model"]), Qwen3RendererConfig(enable_thinking=True))
    tokenizer = renderer._tokenizer
    binding = s.binding_for(s.policies()["original"])
    root, child = binding["role_map"]["root"], binding["fixed_child"]
    tasks = s.make_tasks()
    coordinate = next(row for row in s.build_plan(tasks) if row["weight"] == "original")
    calls, current = [], {}

    async def provider(request):
        body = await request.json()
        calls.append({"arm": current["arm"], "body": body})
        text = tokenizer.decode(body["token_ids"])
        if body["model"] == child:
            assert "CPU return-contract child fixture" in text and s.SUFFIX not in text
            completion = '["entity"]'
        elif not current["root_calls"]:
            assert (s.SUFFIX in text) == (current["arm"] == "contract")
            current["root_calls"] += 1
            code = 'child = await rlm("CPU return-contract child fixture: return only a JSON array containing entity")\nprint(child.answer)'
            completion = '<tool_call>\n' + json.dumps({"name": "ipython", "arguments": {"code": code}}) + '\n</tool_call>'
        else:
            assert '["entity"]' in text
            completion = "Answer: 0"
        ids = tokenizer.encode(completion, add_special_tokens=False) + [151645]
        return web.json_response({"request_id": f"CPU_FIXTURE_{len(calls)}", "choices": [{
            "token_ids": ids, "finish_reason": "stop", "logprobs": {"content": [
                {"token": f"token_id:{token}", "logprob": -.5} for token in ids]}}]})

    async def models(request):
        return web.json_response({"data": [{"id": alias, "max_model_len": 8192} for alias in (root, child)]})

    app = web.Application()
    app.router.add_post("/inference/v1/generate", provider)
    app.router.add_get("/v1/models", models)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]
    endpoint = {**s.planned_endpoint(binding), "url": f"http://127.0.0.1:{port}/v1", "api_key_env": "RETURN_CONTRACT_CPU_FIXTURE_KEY"}
    os.environ[endpoint["api_key_env"]] = "cpu-fixture-not-a-provider-secret"
    os.environ["PATH"] = str(capture.q.ROOTLESS / "bin") + os.pathsep + os.environ.get("PATH", "")
    os.environ.setdefault("VERIFIERS_CACHE_DIR", "/project/alex_phd/cache/verifiers-prime")
    results = []
    try:
        for arm in s.ARMS:
            current.update(arm=arm, root_calls=0)
            target = output / arm
            environment = SingleAgentEnv(SingleAgentEnvConfig.model_validate(c.read(c.PILOT / "SPEC.json")["environment"]))
            with capture.installed_hooks(binding, target):
                async with environment.serving():
                    task = s.with_prompt(tasks[coordinate["task_name"]], arm)
                    episode = await asyncio.wait_for(environment.run_slot(RunSlot(task), capture.make_context(endpoint, coordinate)), timeout=180)
                    raw = episode.to_record()
            c.write_once(target / "EPISODE.json", raw)
            roots, all_calls = s.native.exporter.episode_turns(raw, target, binding)
            if len(roots) != 2 or len(all_calls) != 3:
                raise ValueError("real native root-child-root capture proof failed")
            results.append({"arm": arm, "root_calls": 2, "child_calls": 1, "physical_prefixes_verified": True})
        c.write_once(output / "PROVIDER_REQUESTS.json", calls)
        result = {"conditions": list(s.ARMS), "results": results, "provider_calls": len(calls),
            "gpu_calls": 0, "actual_model_calls": 0, "real_rootless_runtime": True,
            "real_native_client_renderer": True, "root_suffix_present_iff_contract": True,
            "child_fixture_did_not_receive_suffix": True,
            "provider_output_and_logprobs": "deterministic CPU fixtures, not model behavior or probabilities"}
        c.write_once(output / "RESULT.json", result)
        print(json.dumps(result), flush=True)
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=s.ROOT / "qualification-attempt-001")
    asyncio.run(qualify(parser.parse_args().output.resolve()))
