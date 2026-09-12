"""Thin real RunSlot collector using the accepted native QS6/runtime interface."""

import argparse
import asyncio
import copy
import os
from pathlib import Path
import time

import live_helper
import metrics
import study


def frozen_task(context, coordinate):
    gold = study.data()[1][context["id"]]["answers"][coordinate["operator"]]
    task = study.make_task(context, coordinate, gold)
    if task.hash != study.read(study.INPUTS / "PREFIXES.json")[coordinate["id"]]["task_hash"]:
        raise ValueError("actual modified task hash differs before model call")
    return task


async def run(arm, endpoint_path, binding_path, output, deadline):
    import httpx
    from transformers import AutoTokenizer
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv, SingleAgentEnvConfig
    study.verify()
    output.mkdir(parents=True, exist_ok=False)
    descriptor = study.read(endpoint_path)
    binding = study.read(binding_path)
    expected_binding = study.read(study.INPUTS / ("BINDING_" + ("rl_step8" if arm == "rl_step8" else "c32") + ".json"))
    if binding != expected_binding:
        raise ValueError("actual service binding differs from frozen full endpoint")
    plan = study.plan(arm)
    root_alias = binding["role_map"]["root"]
    if descriptor["model_alias"] != root_alias:
        raise ValueError("endpoint does not describe fixed QS6 root")
    config = study.environment_config(arm)
    study.write_x(output / "SPEC.json", {"arm": arm, "plan": plan, "binding": binding,
        "binding_sha256": study.sha(binding_path), "descriptor": descriptor, "environment": config,
        "ready_sha256": study.sha(study.ROOT / "READY.json"), "deadline": deadline})
    url = f"http://{descriptor['host']}:{descriptor['port']}/v1"
    async with httpx.AsyncClient(trust_env=False, timeout=15,
            headers={"Authorization": "Bearer " + os.environ[descriptor["api_key_env"]]}) as client:
        response = await client.get(url + "/models")
        response.raise_for_status()
        cards = {row["id"]: row for row in response.json()["data"]}
    for alias, value in binding["models"].items():
        if cards.get(alias, {}).get("root") != value["path"] or cards[alias].get("parent") != descriptor["base_model"]["path"]:
            raise ValueError("live model card does not bind exact root/helper/base")
    study.write_x(output / "LIVE_MODELS.json", cards)
    endpoint = {"url": url, "model": root_alias, "renderer_model": descriptor["base_model"]["path"], "api_key_env": descriptor["api_key_env"]}
    native_endpoint = f"http://{descriptor['host']}:{descriptor['port']}/inference/v1/generate"
    public, gold = study.data()
    public = {row["id"]: row for row in public}
    terminal = study.sources()[1]
    interface = __import__("terminal_collect").native.interface(output)
    tokenizer = AutoTokenizer.from_pretrained(study.sources()[2].MODEL, local_files_only=True)
    interface = live_helper.adapt(interface, binding, output, plan, public,
        study.read(study.INPUTS / "HELPER_REQUESTS.json"), tokenizer, native_endpoint, deadline)
    queue, records = asyncio.Queue(), []
    for row in plan:
        queue.put_nowait(row)
    roots = None

    async def one(coordinate):
        context = public[coordinate["context_id"]]
        slot = RunSlot(frozen_task(context, coordinate))
        started = time.time()
        censored = False
        try:
            raw = (await asyncio.wait_for(env.run_slot(slot, interface.e.make_context(endpoint, coordinate)),
                max(.001, min(180, deadline - time.time())))).to_record()
        except BaseException as error:
            censored = isinstance(error, (asyncio.CancelledError, TimeoutError))
            raw = {"ok": False, "errors": [{"type": type(error).__name__, "message": str(error)}],
                   "traces": [trace.to_record() for trace in slot.traces]}
        wrappers = [study.read(path) for path in (output / "helper-wrappers").glob("*.json")]
        record = {"coordinate": coordinate, "episode": raw, "episode_sha256": study.digest(raw),
            "timing": {"started": started, "ended": time.time()},
            "derived": metrics.inspect(raw, coordinate, context, gold[context["id"]], roots, wrappers, censored)}
        study.write_x(output / "episodes" / (coordinate["id"] + ".json"), record)
        records.append(record)
        print({"arm": arm, "completed": len(records), "status": record["derived"]["status"]}, flush=True)

    async def worker():
        while time.time() < deadline:
            try:
                row = queue.get_nowait()
            except asyncio.QueueEmpty:
                return
            try:
                await one(row)
            finally:
                queue.task_done()

    with interface.installed(binding, output, plan, public) as root_records:
        roots = root_records
        env = SingleAgentEnv(SingleAgentEnvConfig.model_validate(config))
        async with env.serving():
            workers = [asyncio.create_task(worker()) for _ in range(4)]
            try:
                await asyncio.wait_for(asyncio.gather(*workers), max(.001, deadline - time.time()))
            except TimeoutError:
                for worker_task in workers:
                    worker_task.cancel()
                await asyncio.gather(*workers, return_exceptions=True)
    study.write_x(output / "STATUS.json", {"planned": 16, "recorded": len(records),
        "not_started": [row["id"] for row in plan if row["id"] not in {record["coordinate"]["id"] for record in records}],
        "physical_root_attempts": len(roots), "physical_helper_attempts": len(list((output / "helper-calls").glob("*.json")))})
    return 0 if len(records) == 16 else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=study.ARMS, required=True)
    parser.add_argument("--endpoint", type=Path, required=True)
    parser.add_argument("--binding", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--deadline", type=float, required=True)
    args = parser.parse_args()
    raise SystemExit(asyncio.run(run(args.arm, args.endpoint, args.binding, args.output, args.deadline)))
