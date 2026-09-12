"""One-slot real-runtime/renderer/V7-recorder CPU fake-provider qualification."""

import asyncio
import json
import os
from pathlib import Path
import time

from aiohttp import web

import collect
import study


OUTPUT = study.ROOT / "cpu-smoke"


async def smoke():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("CPU smoke requires CUDA hidden")
    if OUTPUT.exists() or (study.ROOT / "CPU_SMOKE.json").exists():
        raise FileExistsError("CPU smoke output already exists")
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

    async def provider(request):
        body = await request.json()
        requests.append(body)
        if len(requests) == 1:
            reply = (
                "<tool_call>\n"
                + json.dumps(
                    {
                        "name": "ipython",
                        "arguments": {
                            "code": (
                                "import hashlib; p=open('/context.json','rb').read(); "
                                "print(len(p), hashlib.sha256(p).hexdigest())"
                            )
                        },
                    },
                    separators=(",", ":"),
                )
                + "\n</tool_call>"
            )
        else:
            reply = gold["answer"]
        ids = tokenizer.encode(reply, add_special_tokens=False) + [151645]
        return web.json_response(
            {
                "request_id": f"SHORT32_CPU_{len(requests)}",
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
        "api_key_env": "SHORT32_CPU_KEY",
        "base_model": {"path": str(study.MODEL)},
        "adapter": None,
    }
    context = collect.model_context(endpoint, coordinate)
    before_path = os.environ.get("PATH", "")
    before_secret = os.environ.get(endpoint["api_key_env"])
    os.environ["PATH"] = str(study.RUNTIME_BIN) + os.pathsep + before_path
    os.environ[endpoint["api_key_env"]] = "cpu-fixture-not-a-service-secret"
    os.environ.setdefault("VERIFIERS_CACHE_DIR", "/project/alex_phd/cache/verifiers-prime")
    started = time.time()
    recorder = collect.v7_recorder()
    try:
        with recorder.native_checkpoints(
            OUTPUT / "native-calls", study.MODEL_ALIAS
        ) as native_rows:
            async with env.serving():
                episode = await asyncio.wait_for(
                    env.run_slot(RunSlot(task), context), timeout=300
                )
        raw = episode.to_record()
    finally:
        await runner.cleanup()
        os.environ["PATH"] = before_path
        if before_secret is None:
            os.environ.pop(endpoint["api_key_env"], None)
        else:
            os.environ[endpoint["api_key_env"]] = before_secret
    derived = collect.inspect_trace(raw, gold, native_rows)
    trace = raw["traces"][0]
    tool_results = [
        str((node.get("message") or {}).get("content") or "")
        for node in trace.get("nodes") or []
        if (node.get("message") or {}).get("role") == "tool"
    ]
    context_sha = task.data.document_sha256
    first_prompt = tokenizer.decode(requests[0]["token_ids"])
    proof = {
        "schema": "openai-mrcr-short32-base-cpu-smoke-v1",
        "elapsed_seconds": time.time() - started,
        "episode_ok": raw.get("ok"),
        "stop_condition": trace.get("stop_condition"),
        "provider_requests": len(requests) if False else len(requests),
        "native_returned": derived["native_returned"],
        "native_mapping_complete": derived["native_mapping_complete"],
        "root_actions_returned": derived["root_actions_returned"],
        "child_actions_returned": derived["child_actions_returned"],
        "six_total_root_child_cap_respected": derived[
            "six_total_root_child_cap_respected"
        ],
        "second_pending_turn_prefix_nodes": len(native_rows[1]["turn"]["prefix_node_ids"]),
        "second_pending_turn_path_len": native_rows[1]["turn"]["path_len"],
        "successful_exact_context_json_read": any(context_sha in value for value in tool_results),
        "official_reward": derived["reward"],
        "first_prompt_contains_exact_question": Path(
            next(row for row in study.selected() if row["id"] == coordinate["record_id"])[
                "final_question_path"
            ]
        ).read_text()
        in first_prompt,
        "first_prompt_contains_host_answer": gold["answer"] in first_prompt,
        "heldout_records_read": 0,
        "gpu_calls": 0,
        "weighted_model_calls": 0,
        "synthetic_provider_logprobs": True,
    }
    proof["passed"] = bool(
        proof["episode_ok"] is True
        and proof["stop_condition"] == "agent_completed"
        and proof["provider_requests"] == proof["native_returned"] == 2
        and proof["native_mapping_complete"]
        and proof["root_actions_returned"] == 2
        and proof["child_actions_returned"] == 0
        and proof["six_total_root_child_cap_respected"]
        and proof["second_pending_turn_prefix_nodes"] > 0
        and proof["second_pending_turn_path_len"] > 0
        and proof["successful_exact_context_json_read"]
        and proof["official_reward"] == 1.0
        and proof["first_prompt_contains_exact_question"]
        and not proof["first_prompt_contains_host_answer"]
    )
    study.write_x(OUTPUT / "EPISODE.json", raw)
    study.write_x(OUTPUT / "PROVIDER_REQUESTS.json", requests)
    study.write_x(study.ROOT / "CPU_SMOKE.json", proof)
    if not proof["passed"]:
        raise ValueError("short32 CPU smoke failed")
    print(json.dumps(proof, sort_keys=True))


if __name__ == "__main__":
    asyncio.run(smoke())
