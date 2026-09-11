"""CPU-only actual env.run_slot to one fake provider call under every binding."""
import asyncio
import json
import os
from pathlib import Path
import tempfile

from aiohttp import web
import study as s


async def main():
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv, SingleAgentEnvConfig
    plan = s.read(s.ROOT / "inputs/FREE_PLAN.json")
    row = plan[0]; contexts = {item["id"]: item for item in s.read(s.ROOT / "inputs/PUBLIC.json")}
    context = contexts[row["context_id"]]
    gold = s.read(s.ROOT / "inputs/HOST_GOLD.json")[context["id"]]["answers"][row["family"]]
    task = s.make_task(context, row, gold)
    expected = s.base.qnative().first_prefix(task)
    renderer = s.base.qnative().stack().native.renderer()
    calls = []
    async def provider(request):
        body = await request.json(); calls.append(body)
        reply = "Answer: 0"; ids = renderer._tokenizer.encode(reply, add_special_tokens=False) + [151645]
        return web.json_response({"request_id": f"FRESH_CPU_{len(calls)}",
            "usage": {"prompt_tokens": len(body["token_ids"]), "completion_tokens": len(ids),
                      "total_tokens": len(body["token_ids"]) + len(ids)},
            "choices": [{"token_ids": ids, "finish_reason": "stop",
                         "logprobs": {"content": [{"token": f"token_id:{value}", "logprob": -0.5}
                                                   for value in ids]}}]})
    app = web.Application(); app.router.add_post("/inference/v1/generate", provider)
    runner = web.AppRunner(app); await runner.setup(); site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start(); port = site._server.sockets[0].getsockname()[1]
    old = os.environ.get("STRICT_RLM_CALIBRATION_API_KEY")
    os.environ["STRICT_RLM_CALIBRATION_API_KEY"] = "cpu-fixture-not-credential"
    prefixes, models = {}, {}
    try:
        with tempfile.TemporaryDirectory(prefix="fresh-bindings-") as temporary:
            root = Path(temporary)
            for arm in ("fixed24", "original_sft6", "new_corpus_sft6"):
                (root / arm).mkdir()
                binding = s.binding(arm); models[arm] = len(binding["models"])
                root_alias = binding["role_map"]["root"]
                endpoint = {"url": f"http://127.0.0.1:{port}/v1", "model": root_alias,
                            "renderer_model": str(s.base.qnative().stack().prior.BASE),
                            "api_key_env": "STRICT_RLM_CALIBRATION_API_KEY"}
                interface = s.base.qnative().interface(root / arm)
                with interface.installed(binding, root / arm, [row], {context["id"]: context}):
                    env = SingleAgentEnv(SingleAgentEnvConfig.model_validate(interface.e.environment_config()))
                    async with env.serving():
                        result = await env.run_slot(RunSlot(task), interface.e.make_context(endpoint, row))
                        record = result.to_record()
                        if not record["traces"] or not record["traces"][0]["root_reply"]:
                            raise ValueError("nonempty root transport required")
                prefixes[arm] = len(calls[-1]["token_ids"])
                if calls[-1]["token_ids"] != expected:
                    raise ValueError("first transport prefix differs")
    finally:
        await runner.cleanup()
        if old is None: os.environ.pop("STRICT_RLM_CALIBRATION_API_KEY", None)
        else: os.environ["STRICT_RLM_CALIBRATION_API_KEY"] = old
    value = {"schema": "fresh-input-three-binding-cpu-qualification-v1",
             "arms": ["fixed24", "original_sft6", "new_corpus_sft6"],
             "provider_calls": len(calls), "nonempty_binding_models": models,
             "first_transport_prefix_tokens": prefixes, "gpu_calls": 0, "service_calls": 0}
    s.write(s.ROOT / "QUALIFICATION.json", value); print(json.dumps(value, sort_keys=True))


if __name__ == "__main__":
    asyncio.run(main())
