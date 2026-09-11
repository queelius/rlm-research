"""Real rootless native root-child-root CPU qualification; provider tokens are fixtures."""

import asyncio
import json
import os
from pathlib import Path

from aiohttp import web

import capture
from credit_data import ROOT, read
from native_routing import installed_hooks, write_once


async def qualify(output):
    from renderers import Qwen3RendererConfig, create_renderer
    from renderers.base import load_tokenizer
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv, SingleAgentEnvConfig

    if output.exists():
        raise ValueError("new CPU qualification directory required")
    output.mkdir(parents=True)
    descriptor = read(capture.ENDPOINT)
    renderer = create_renderer(load_tokenizer(descriptor["base_model"]["path"]), Qwen3RendererConfig(enable_thinking=True))
    tokenizer = renderer._tokenizer
    requests = []
    async def provider(request):
        body = await request.json()
        requests.append(body)
        prompt = tokenizer.decode(body["token_ids"])
        if body["model"] == capture.role.SELECTED:
            assert "CPU native child fixture" in prompt
            completion = '["entity"]'
        elif len(requests) == 1:
            code = 'child = await rlm("CPU native child fixture: return only a JSON array containing entity")\nprint(child.answer)'
            completion = '<tool_call>\n' + json.dumps({"name": "ipython", "arguments": {"code": code}}) + '\n</tool_call>'
        else:
            assert '["entity"]' in prompt
            completion = "Answer: 0"
        ids = tokenizer.encode(completion, add_special_tokens=False) + [151645]
        return web.json_response({"request_id": f"CPU_ONLY_{len(requests)}", "choices": [{
            "token_ids": ids, "finish_reason": "stop", "logprobs": {"content": [
                {"token": f"token_id:{token}", "logprob": -0.5} for token in ids]}}]})
    async def models(request):
        return web.json_response({"data": [{"id": alias, "max_model_len": 8192} for alias in (capture.role.ORIGINAL, capture.role.SELECTED)]})
    app = web.Application()
    app.router.add_post("/inference/v1/generate", provider)
    app.router.add_get("/v1/models", models)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]
    endpoint = {"url": f"http://127.0.0.1:{port}/v1", "model": capture.role.ORIGINAL,
        "renderer_model": descriptor["base_model"]["path"], "api_key_env": "ROOT_CREDIT_CPU_FIXTURE_KEY"}
    os.environ["ROOT_CREDIT_CPU_FIXTURE_KEY"] = "cpu-only-not-a-provider-secret"
    os.environ["PATH"] = str(capture.q.ROOTLESS / "bin") + os.pathsep + os.environ.get("PATH", "")
    os.environ.setdefault("VERIFIERS_CACHE_DIR", "/project/alex_phd/cache/verifiers-prime")
    environment = SingleAgentEnv(SingleAgentEnvConfig.model_validate(read(capture.ROLE / "SPEC.json")["environment"]))
    coordinate = read(ROOT / "inputs/PLAN.json")[0]
    bound = capture.binding()
    try:
        with installed_hooks(bound, output):
            async with environment.serving():
                task = capture.role.with_prompt(capture.make_tasks()[coordinate["task_name"]], "sft_child")
                episode = await asyncio.wait_for(environment.run_slot(RunSlot(task), capture.make_context(endpoint, coordinate)), timeout=420)
                raw = episode.to_record()
        write_once(output / "EPISODE.json", raw)
        write_once(output / "PROVIDER_REQUESTS.json", requests)
        from root_export import episode_turns
        roots, all_calls = episode_turns(raw, output, bound)
        if len(requests) != 3 or len(roots) != 2 or len(all_calls) != 3:
            raise ValueError("real native root-child-root three-call proof failed")
        result = {"real_owned_rootless_runtime": True, "real_TrainClient_and_native_renderer": True,
            "provider_calls": 3, "credited_root_calls": 2, "uncredited_child_calls": 1,
            "exact_physical_prefix_and_wire_tokens_verified": True, "gpu_calls": 0,
            "provider": "CPU deterministic fixture only", "synthetic_logprobs_not_measurements": True}
        write_once(output / "RESULT.json", result)
        print(json.dumps(result), flush=True)
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "qualification-attempt-001")
    asyncio.run(qualify(parser.parse_args().output))
