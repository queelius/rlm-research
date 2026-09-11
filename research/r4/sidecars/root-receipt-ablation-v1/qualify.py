"""Three real pinned rootless/native CPU fixture episodes; never model inference."""
import argparse
import asyncio
import json
import os
from pathlib import Path
from aiohttp import web
import experiment as e

c, capture = e.c, e.capture


async def qualify(output):
    from renderers import Qwen3RendererConfig, create_renderer
    from renderers.base import load_tokenizer
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv, SingleAgentEnvConfig
    if output.exists():
        raise ValueError("unused immutable CPU qualification path required")
    output.mkdir(parents=True)
    renderer = create_renderer(load_tokenizer(c.pilot_recipe()["base_model"]), Qwen3RendererConfig(enable_thinking=True))
    tokenizer = renderer._tokenizer
    policy = c.read(e.PRIOR / "SPEC.json")["policies"]["step8"]
    binding = e.binding_for(policy)
    root, child = binding["role_map"]["root"], binding["fixed_child"]
    tasks = e.make_tasks()
    coordinate = e.build_plan(tasks)[0]
    calls, current = [], {}
    helper_reply = '{"q0001":"yes"}'

    async def provider(request):
        body = await request.json()
        calls.append({"arm": current["arm"], "body": body})
        text = tokenizer.decode(body["token_ids"])
        if body["model"] == child:
            assert "CPU receipt fixture" in text
            completion = '["entity"]' if current["arm"] == "unchanged" else helper_reply
        elif not current["root_calls"]:
            assert ("Optional source-bound helper" in text) == (current["arm"] != "unchanged")
            current["root_calls"] += 1
            if current["arm"] == "unchanged":
                code = 'child = await rlm("CPU receipt fixture: return JSON array entity")\nprint(child.answer)'
            else:
                code = ('from receipt_api import rlm_records\n'
                    'child = await rlm_records(["q0001"], "CPU receipt fixture: always yes", ["yes", "no"])\n'
                    'print(child.answer)\nprint("RECEIPT_AVAILABLE", hasattr(child, "receipt"))\n')
                if current["arm"] == "receipt":
                    code += 'receipt = child.receipt()\nassert receipt["valid"]\nprint("RECEIPT_VALID", receipt["labels_by_id"])\n'
                code += ('from rlm.broker import result_to_payload, result_from_payload\n'
                    'wire = result_to_payload(child.native_result)\n'
                    'assert set(wire) == {"answer", "session_dir", "usage", "turns"}\n'
                    'assert result_from_payload(wire).answer == child.answer\nprint("BROKER_ROUNDTRIP_OK")')
            completion = '<tool_call>\n' + json.dumps({"name":"ipython", "arguments":{"code":code}}) + '\n</tool_call>'
        else:
            if current["arm"] != "unchanged":
                assert "BROKER_ROUNDTRIP_OK" in text and "Traceback" not in text
                assert ("RECEIPT_AVAILABLE True" in text) == (current["arm"] == "receipt")
                if current["arm"] == "receipt":
                    assert "RECEIPT_VALID" in text
            completion = "Answer: 0"
        ids = tokenizer.encode(completion, add_special_tokens=False) + [151645]
        return web.json_response({"request_id":f"CPU_FIXTURE_{len(calls)}", "choices":[{
            "token_ids":ids, "finish_reason":"stop", "logprobs":{"content":[
                {"token":f"token_id:{token}", "logprob":-.5} for token in ids]}}]})

    async def models(request):
        return web.json_response({"data":[{"id":alias,"max_model_len":8192} for alias in (root,child)]})
    app = web.Application()
    app.router.add_post("/inference/v1/generate", provider)
    app.router.add_get("/v1/models", models)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner,"127.0.0.1",0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]
    endpoint = {**e.old.planned_endpoint(binding), "url":f"http://127.0.0.1:{port}/v1", "api_key_env":"RECEIPT_CPU_FIXTURE_KEY"}
    os.environ[endpoint["api_key_env"]] = "cpu-fixture-not-secret"
    os.environ["PATH"] = str(capture.q.ROOTLESS/"bin") + os.pathsep + os.environ.get("PATH","")
    os.environ.setdefault("VERIFIERS_CACHE_DIR", "/project/alex_phd/cache/verifiers-prime")
    results = []
    try:
        for arm in e.ARMS:
            current.update(arm=arm,root_calls=0)
            target = output/arm
            environment = SingleAgentEnv(SingleAgentEnvConfig.model_validate(c.read(c.PILOT/"SPEC.json")["environment"]))
            with capture.installed_hooks(binding,target):
                async with environment.serving():
                    task = e.with_prompt(tasks[coordinate["task_name"]],arm)
                    episode = await asyncio.wait_for(environment.run_slot(RunSlot(task),capture.make_context(endpoint,coordinate)),timeout=180)
                    raw = episode.to_record()
            c.write_once(target/"EPISODE.json",raw)
            roots, all_calls = e.native.exporter.episode_turns(raw,target,binding)
            if len(roots)!=2 or len(all_calls)!=3:
                raise ValueError("real native root-child-root proof failed")
            audit = [trace.get("info",{}).get("receipt_audit",{}) for trace in raw["traces"]]
            if arm != "unchanged" and not any(item.get("raw") and '"event": "helper_result"' in item["raw"] for item in audit):
                raise ValueError("task finalize did not preserve local receipt audit")
            results.append({"arm":arm,"root_calls":2,"child_calls":1,"broker_roundtrip":arm!="unchanged","audit":audit})
        c.write_once(output/"PROVIDER_REQUESTS.json",calls)
        proof = {"conditions":list(e.ARMS),"results":results,"provider_calls":len(calls),"gpu_calls":0,
            "actual_model_calls":0,"real_rootless_runtime":True,"real_native_client_renderer":True,
            "fixture_notice":"Provider tokens/logprobs are deterministic CPU fixtures, never model behavior or likelihood evidence."}
        c.write_once(output/"RESULT.json",proof)
        print(json.dumps({"provider_calls":len(calls),"gpu_calls":0,"conditions":list(e.ARMS)}),flush=True)
    finally:
        c.write_once(output/"ALL_RETAINED_PROVIDER_REQUESTS.json",calls)
        await runner.cleanup()


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,default=e.ROOT/"qualification-map-attempt-001")
    asyncio.run(qualify(parser.parse_args().output.resolve()))
