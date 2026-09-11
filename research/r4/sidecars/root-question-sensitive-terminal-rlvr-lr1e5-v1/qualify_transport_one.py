"""One-slot CPU fake-provider proof through actual env.run_slot and native transport."""
import asyncio
import json
import os
import time

from aiohttp import web

import terminal_native as native
import terminal_collect as collect
import terminal_study as study


async def qualify():
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv, SingleAgentEnvConfig

    output = study.ROOT / "qualification-transport1"
    output.mkdir(exist_ok=False)
    started = time.time()
    public, host = study.data()
    contexts = {row["id"]: row for row in public}
    rows = study.candidate_plan(1)[:1]
    infos = study.read(study.ROOT / "inputs/TASKS.json")
    tasks = {}
    for row in rows:
        context = contexts[row["context_id"]]
        info = infos[row["task_name"]]
        task = native.make_task(context, info["question"],
                                host[context["id"]]["answers"][row["family"]], row["task_name"])
        if task.hash != info["task_hash"] or native.first_prefix(task) != info["first_prompt_token_ids"]:
            raise ValueError("repaired task identity/prefix differs before transport")
        tasks[row["id"]] = task
    old = study.read(study.SIDE / "leaf-role-routing-v1/BOUND_WEIGHTS.json")
    child = "strict-rlm-qwen3-4b-role-sft-selected-v1"
    root = "terminal-rlvr-recovery-CPU-root"
    initial = study.fixed_start()
    binding = {**old,
               "models": {root: {key: initial[key] for key in
                                  ("path", "adapter_sha256", "config_sha256")},
                          child: old["models"][child]},
               "role_map": {"root": root, "children": [child]},
               "fixed_child": child, "qualification_only": True}
    renderer = native.stack().native.renderer()
    calls = []

    async def provider(request):
        body = await request.json()
        calls.append(body)
        reply = "Answer: 0"
        ids = renderer._tokenizer.encode(reply, add_special_tokens=False) + [151645]
        return web.json_response({"request_id": "TERMINAL_RECOVERY_CPU_1",
            "usage": {"prompt_tokens": len(body["token_ids"]), "completion_tokens": len(ids),
                      "total_tokens": len(body["token_ids"]) + len(ids)},
            "choices": [{"token_ids": ids, "finish_reason": "stop",
                         "logprobs": {"content": [{"token": f"token_id:{value}",
                                                    "logprob": -0.5} for value in ids]}}]})

    app = web.Application()
    app.router.add_post("/inference/v1/generate", provider)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    endpoint = {"url": f"http://127.0.0.1:{site._server.sockets[0].getsockname()[1]}/v1",
                "model": root, "renderer_model": native.stack().prior.BASE.as_posix(),
                "api_key_env": "TERMINAL_RECOVERY_CPU_KEY"}
    before = {key: os.environ.get(key) for key in
              ("STRICT_RLM_CALIBRATION_API_KEY", "TERMINAL_RECOVERY_CPU_KEY")}
    os.environ["STRICT_RLM_CALIBRATION_API_KEY"] = "cpu-fixture-not-credential"
    os.environ["TERMINAL_RECOVERY_CPU_KEY"] = "cpu-fixture-not-credential"
    try:
        interface = native.interface(output)
        raw = {}
        installed_contexts = {row["context_id"]: contexts[row["context_id"]] for row in rows}
        with interface.installed(binding, output, rows, installed_contexts):
            env = SingleAgentEnv(SingleAgentEnvConfig.model_validate(interface.e.environment_config()))
            async with env.serving():
                async def one(row):
                    raw[row["id"]] = (await env.run_slot(
                        RunSlot(tasks[row["id"]]), interface.e.make_context(endpoint, row))).to_record()
                stop = await collect.dispatch(rows, one, time.time() + 360)
        expected = sorted(tuple(infos[row["task_name"]]["first_prompt_token_ids"]) for row in rows)
        observed = sorted(tuple(call["token_ids"]) for call in calls)
        if stop is not None or len(calls) != 1 or len(raw) != 1 or observed != expected:
            raise ValueError("actual one-slot transport did not complete frozen task")
        result = {"status": "PASS", "provider_calls": 1, "completed_slots": 1,
                  "workers": 1, "actual_model_calls": 0,
                  "gpu_calls": 0, "task_hashes": sorted({task.hash for task in tasks.values()}),
                  "first_transport_prefix_token_counts": sorted({len(call["token_ids"]) for call in calls}),
                  "all_root_replies": sorted({value["traces"][0]["root_reply"] for value in raw.values()}),
                  "elapsed_seconds": time.time() - started}
        study.write(output / "RESULT.json", result)
        study.write(output / "PROVIDER_REQUESTS.json", calls)
        return result
    finally:
        await runner.cleanup()
        for key, value in before.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


if __name__ == "__main__":
    print(asyncio.run(qualify()))
