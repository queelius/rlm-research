"""One-slot actual RLM graph smoke with two root and two child turns."""

import asyncio
import json
import os
from pathlib import Path
import time

from aiohttp import web

import collect
import collect_v2
import study


OUTPUT = study.ROOT / "cpu-child-smoke-v2"
PROOF = study.ROOT / "CPU_CHILD_ROLE_SMOKE_V2.json"


async def smoke():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("CPU smoke requires CUDA hidden")
    if OUTPUT.exists() or PROOF.exists():
        raise FileExistsError("additive child-role smoke already exists")
    from renderers import Qwen3RendererConfig, create_renderer
    from renderers.base import load_tokenizer
    from verifiers.v1.env import RunSlot

    env = study.environment(study.INPUTS)
    task = list(env.taskset)[0]
    coordinate = next(row for row in study.plan() if row["id"] == task.data.name)
    gold = study.read(study.INPUTS / "HOST_GOLD.json")[coordinate["record_id"]]
    tokenizer = create_renderer(
        load_tokenizer(study.MODEL), Qwen3RendererConfig(enable_thinking=True)
    )._tokenizer
    requests = []
    replies = [
        (
            "<tool_call>\n"
            + json.dumps(
                {
                    "name": "ipython",
                    "arguments": {
                        "code": (
                            "child = await rlm(\"Use ipython once to print 2+2, then answer "
                            "exactly CHILD_OK.\"); print(child.answer)"
                        )
                    },
                },
                separators=(",", ":"),
            )
            + "\n</tool_call>"
        ),
        (
            "<tool_call>\n"
            + json.dumps(
                {"name": "ipython", "arguments": {"code": "print(2+2)"}},
                separators=(",", ":"),
            )
            + "\n</tool_call>"
        ),
        "CHILD_OK",
        gold["answer"],
    ]

    async def provider(request):
        body = await request.json()
        requests.append(body)
        if len(requests) > len(replies):
            raise RuntimeError("unexpected hidden retry/model attempt")
        ids = tokenizer.encode(replies[len(requests) - 1], add_special_tokens=False) + [151645]
        return web.json_response(
            {
                "request_id": f"SHORT32_CHILD_CPU_{len(requests)}",
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
    port = site._server.sockets[0].getsockname()[1]
    endpoint = {
        "model_alias": study.MODEL_ALIAS,
        "host": "127.0.0.1",
        "port": port,
        "api_key_env": "SHORT32_CHILD_CPU_KEY",
        "base_model": {"path": str(study.MODEL)},
        "adapter": None,
    }
    context = collect.model_context(endpoint, coordinate)
    before_path = os.environ.get("PATH", "")
    before_secret = os.environ.get(endpoint["api_key_env"])
    os.environ["PATH"] = str(study.RUNTIME_BIN) + os.pathsep + before_path
    os.environ[endpoint["api_key_env"]] = "cpu-fixture-not-a-service-secret"
    os.environ.setdefault("VERIFIERS_CACHE_DIR", "/project/alex_phd/cache/verifiers-prime")
    recorder = collect.v7_recorder()
    started = time.time()
    try:
        with recorder.native_checkpoints(OUTPUT / "native-calls", study.MODEL_ALIAS) as rows:
            async with env.serving():
                episode = await asyncio.wait_for(env.run_slot(RunSlot(task), context), timeout=300)
        raw = episode.to_record()
    finally:
        await runner.cleanup()
        os.environ["PATH"] = before_path
        if before_secret is None:
            os.environ.pop(endpoint["api_key_env"], None)
        else:
            os.environ[endpoint["api_key_env"]] = before_secret
    derived = collect_v2.inspect_trace(raw, gold, rows)
    mapping = derived["causal_mapping"]
    proof = {
        "schema": "openai-mrcr-short32-child-role-cpu-smoke-v2",
        "elapsed_seconds": time.time() - started,
        "provider_requests": len(requests),
        "native_returned": derived["native_returned"],
        "native_mapping_complete": derived["native_mapping_complete"],
        "root_actions": mapping["root_actions"],
        "child_actions": mapping["child_actions"],
        "child_invocations": mapping["child_invocations"],
        "mapped_nodes": [row["node"] for row in mapping["matches"]],
        "roles": [row["role"] for row in mapping["matches"]],
        "official_reward": derived["reward"],
        "gpu_calls": 0,
        "weighted_model_calls": 0,
        "synthetic_provider_logprobs": True,
    }
    proof["passed"] = bool(
        proof["provider_requests"] == proof["native_returned"] == 4
        and proof["native_mapping_complete"]
        and proof["root_actions"] == 2
        and proof["child_actions"] == 2
        and proof["child_invocations"] == 1
        and proof["roles"] == ["root", "child", "child", "root"]
        and proof["official_reward"] == 1.0
    )
    study.write_x(OUTPUT / "EPISODE.json", raw)
    study.write_x(OUTPUT / "PROVIDER_REQUESTS.json", requests)
    study.write_x(PROOF, proof)
    if not proof["passed"]:
        raise ValueError("actual multi-turn child role smoke failed")
    print(json.dumps(proof, sort_keys=True))


if __name__ == "__main__":
    asyncio.run(smoke())
