"""CPU proof of one real prepared free row through task, bundle, env, and fake transports."""

import asyncio
import json
import os
from pathlib import Path
import time

from aiohttp import web

import study as s


class Memory:
    def __init__(self):
        self.files = {}

    async def write(self, name, data):
        self.files[name] = data


async def qualify(output):
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv, SingleAgentEnvConfig

    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    started = time.time()
    plan = s.read(s.ROOT / "inputs/FREE_PLAN.json")
    row = next(
        item
        for item in plan
        if item["policy"] == "sft6"
        and item["harness_arm"] == "cumulative_4096b"
        and item["size"] == 256
    )
    contexts = {item["id"]: item for item in s.read(s.ROOT / "inputs/PUBLIC.json")}
    context = contexts[row["context_id"]]
    host = s.read(s.ROOT / "inputs/HOST_GOLD.json")[context["id"]]
    gold = host["answers"]["J1"]
    task = s.make_task(context, row, gold)
    native = s.base.base.qnative()
    expected_prefix = s.read(s.ROOT / "inputs/PROMPTS_ACCURATE.json")[row["id"]]["token_ids"]
    if native.first_prefix(task) != expected_prefix:
        raise ValueError("prepared real-row native prefix changed")
    memory = Memory()
    await task.setup(None, memory)
    if set(memory.files) != {
        "records.json",
        "context.txt",
        "query.txt",
        "batch_contract.py",
        ".observation_view.json",
    }:
        raise ValueError("full bundle setup files changed")
    view = json.loads(memory.files[".observation_view.json"])
    if view != {"schema": "bounded-observation-view-config-v1", "max_bytes": 4096}:
        raise ValueError("qualified 4096-byte view changed")
    if b"_CUMULATIVE = True" not in memory.files["batch_contract.py"]:
        raise ValueError("cumulative return helper not installed")

    binding = s.binding("sft6")
    root_alias = binding["role_map"]["root"]
    child_alias = binding["fixed_child"]
    renderer = native.stack().native.renderer()
    labels = host["labels"]
    label_json = json.dumps(labels, sort_keys=True)
    code = (
        "import json\n"
        "from rlm.api import run as rlm\n"
        "from batch_contract import request_for, strict_map\n"
        "records = json.load(open('records.json'))\n"
        "child = await rlm(request_for(records))\n"
        "observed_labels = strict_map(child.answer, [record['id'] for record in records])\n"
        "print(json.dumps(observed_labels, sort_keys=True))"
    )
    calls = []
    counts = {"root": 0, "child": 0}
    second_root_saw_clip_marker = False

    def payload(reply, request_id):
        token_ids = renderer._tokenizer.encode(reply, add_special_tokens=False) + [151645]
        return {
            "request_id": request_id,
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": len(token_ids),
                "total_tokens": len(token_ids),
            },
            "choices": [
                {
                    "token_ids": token_ids,
                    "finish_reason": "stop",
                    "logprobs": {
                        "content": [
                            {"token": f"token_id:{value}", "logprob": -0.5} for value in token_ids
                        ]
                    },
                }
            ],
        }

    async def provider(request):
        nonlocal second_root_saw_clip_marker
        body = await request.json()
        calls.append(body)
        if body["model"] == child_alias:
            counts["child"] += 1
            return web.json_response(payload(label_json, "SCALE_RECOVERY_CPU_CHILD"))
        if body["model"] != root_alias:
            raise ValueError("unexpected model alias in CPU qualification")
        counts["root"] += 1
        if counts["root"] == 1:
            if body["token_ids"] != expected_prefix:
                raise ValueError("first root transport prefix changed")
            reply = native.stack().native.tool_action(code)
        elif counts["root"] == 2:
            decoded = renderer._tokenizer.decode(body["token_ids"], skip_special_tokens=False)
            second_root_saw_clip_marker = "bytes truncated" in decoded
            reply = "Answer: " + str(gold)
        else:
            raise ValueError("unexpected extra root request")
        return web.json_response(payload(reply, f"SCALE_RECOVERY_CPU_ROOT_{counts['root']}"))

    app = web.Application()
    app.router.add_post("/inference/v1/generate", provider)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)
    await site.start()
    endpoint = {
        **native.stack().native.e.old.planned_endpoint(binding),
        "url": f"http://127.0.0.1:{site._server.sockets[0].getsockname()[1]}/v1",
        "api_key_env": "SCALE_HARNESS_RECOVERY_CPU_KEY",
    }
    previous = {
        key: os.environ.get(key)
        for key in ("STRICT_RLM_CALIBRATION_API_KEY", "SCALE_HARNESS_RECOVERY_CPU_KEY")
    }
    os.environ["STRICT_RLM_CALIBRATION_API_KEY"] = "cpu-fixture-not-credential"
    os.environ["SCALE_HARNESS_RECOVERY_CPU_KEY"] = "cpu-fixture-not-credential"
    try:
        interface = s.interface(output)
        # Match od_collect.episode exactly: readout mode is free, while the native
        # Responses transport intentionally uses the qualified train-client path.
        coordinate = {**row, "arm": "typed", "client_path": "train", "temperature": 0.5}
        with interface.installed(binding, output, [coordinate], {context["id"]: context}):
            env = SingleAgentEnv(SingleAgentEnvConfig.model_validate(interface.e.environment_config()))
            async with env.serving():
                raw = (
                    await asyncio.wait_for(
                        env.run_slot(RunSlot(task), interface.e.make_context(endpoint, coordinate)), 180
                    )
                ).to_record()
        trace = raw["traces"][0]
        s.write(output / "EPISODE_DEBUG.json", raw)
        observation = trace["info"]["scale_harness_observations"]
        bounded = [
            item
            for item in json.loads(observation["raw"])
            if item.get("type") == "bounded_observation_view" and item.get("clipped")
        ]
        if not bounded or not second_root_saw_clip_marker:
            raise ValueError("actual 4096-byte head/tail clipping was not visible to next root request")
        if trace["root_reply"] != "Answer: " + str(gold):
            raise ValueError("scalar terminal path changed")
        s.write(output / "EPISODE.json", raw)
        result = {
            "status": "PASS",
            "mode": "free",
            "coordinate_id": row["id"],
            "prepared_size": row["size"],
            "harness_arm": row["harness_arm"],
            "root_calls": counts["root"],
            "child_calls": counts["child"],
            "actual_model_calls": 0,
            "gpu_calls": 0,
            "root_reply": trace["root_reply"],
            "strict_scalar_correct": trace["root_reply"] == "Answer: " + str(gold),
            "setup_files": sorted(memory.files),
            "view_cap_bytes": view["max_bytes"],
            "bounded_view_clipped": True,
            "bounded_view_raw_bytes": max(item["raw_bytes"] for item in bounded),
            "second_root_saw_clip_marker": second_root_saw_clip_marker,
            "elapsed_seconds": time.time() - started,
        }
        s.write(output / "RESULT.json", result)
        s.write(output / "PROVIDER_REQUESTS.json", calls)
        return result
    finally:
        await runner.cleanup()
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


if __name__ == "__main__":
    print(asyncio.run(qualify(s.ROOT / "qualification-transport-attempt-001")))
