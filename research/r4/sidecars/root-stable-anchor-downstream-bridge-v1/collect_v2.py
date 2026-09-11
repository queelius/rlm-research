"""V2 collector: 24 base leaf calls, then 96 QS6 root episodes."""

import argparse
import asyncio
import hashlib
import json
import os
from pathlib import Path
import time
from types import SimpleNamespace

import httpx
import protocol_v2 as p
import study_v2 as s
import collect as old


def root_implementation():
    original = s.load("downstream_v2_recovery_collect", s.SCALE / "collect.py",
        "3074eb6cf05f20c07f7d9eef7a6be859f02a9d38afbfd2af6cd46ade595a67df", {"study": s})
    proxy = SimpleNamespace(**vars(s)); proxy.ROOT = s.RUNTIME_ROOT
    module = original.implementation(); module.s = proxy; module.p = s.protocol(); module.b = proxy
    module._downstream_proxy = proxy
    return module


async def acquire(endpoint, output, deadline, transport=None):
    requests = s.read(s.INPUTS / "LEAF_REQUESTS.json"); prompts = s.read(s.INPUTS / "LEAF_PROMPT_IDS.json")
    full = {c["id"]: c for c in s.read(s.INPUTS / "DATA.json")["contexts"]}; descriptor = s.read(endpoint)
    base = f'http://{descriptor["host"]}:{descriptor["port"]}'; headers = {"Authorization": "Bearer " + os.environ[descriptor["api_key_env"]], "Content-Type": "application/json"}
    target = Path(output) / "leaf"; target.mkdir(parents=True); maps = {e: {} for e in p.ENCODINGS}; rows = []; queue = asyncio.Queue()
    for encoding in p.ENCODINGS:
        for context_id in sorted(requests[encoding]): queue.put_nowait((encoding, context_id))
    async with httpx.AsyncClient(headers=headers, trust_env=False, transport=transport, timeout=90) as client:
        async def worker():
            while not queue.empty():
                encoding, context_id = queue.get_nowait(); directory = target / encoding / context_id; directory.mkdir(parents=True)
                body = requests[encoding][context_id]; wire = json.dumps(body, separators=(",", ":"), ensure_ascii=False).encode()
                result = {"encoding": encoding, "context_id": context_id, "available": False, "observed_invalid": False, "physical_request_attempt": False}
                s.write(directory / "REQUEST.json", {"body": body, "wire_sha256": hashlib.sha256(wire).hexdigest(),
                    "expected_model": s.BASE_ALIAS, "expected_prompt_ids": prompts[encoding][context_id], "recorded_before_send_epoch": time.time()})
                try:
                    result["physical_request_attempt"] = True
                    response = await asyncio.wait_for(client.post(base + "/v1/chat/completions", content=wire), min(90, max(.001, deadline - time.time())))
                    raw = response.json(); s.write(directory / "RESPONSE.json", {"status": response.status_code, "raw": raw, "received_epoch": time.time()})
                    response.raise_for_status()
                    if raw.get("model") != s.BASE_ALIAS: raise ValueError("raw leaf model differs from released base alias")
                    if raw.get("prompt_token_ids") != prompts[encoding][context_id]: raise ValueError("raw leaf prompt IDs differ")
                    content, usage = old.decode_native(raw, prompts[encoding][context_id])
                    result.update(available=True, usage=usage, model=raw["model"], finish_reason=raw["choices"][0]["finish_reason"],
                        raw_prompt_ids_equal=True)
                    maps[encoding][context_id] = p.broker(content, full[context_id], encoding)
                except Exception as error:
                    result.update(error={"type": type(error).__name__, "message": str(error)}, observed_invalid=result["available"])
                s.write(directory / "RESULT.json", result); rows.append(result); queue.task_done()
        await asyncio.gather(*(worker() for _ in range(4)))
    s.write(target / "ROWS.json", rows)
    if len(rows) != 24 or any(not row["available"] or row["observed_invalid"] for row in rows): return None
    s.write(Path(output) / "PREDICTED_MAPS.json", maps); return maps


async def run(args, transport=None):
    s.verify(); binding = s.read(args.binding)
    if binding != s.binding(): raise ValueError("actual V2 binding changed")
    args.output.mkdir(parents=True, exist_ok=False)
    maps = await acquire(args.endpoint, args.output, args.deadline - 120, transport)
    if maps is None:
        s.write(args.output / "STATUS.json", {"complete": False, "reason": "leaf invalid/unavailable"}); return 1
    s.ACTIVE_MAPS = maps; module = root_implementation()
    root_args = SimpleNamespace(mode="free", plan="FREE_PLAN.json", binding=args.binding,
        endpoint=args.endpoint, output=args.output / "root", start=0, stop=96, deadline=args.deadline)
    with s.aliases({"od_study": module._downstream_proxy, "od_protocol": s.protocol(), "od_binding": module._downstream_proxy}): await module.run(root_args)
    recorded = len(list((args.output / "root").glob("*/RESULT.json"))); complete = recorded == 96
    s.write(args.output / "STATUS.json", {"complete": complete, "leaf": 24, "root_recorded": recorded, "root_planned": 96, "no_retry": True})
    return 0 if complete else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--binding", type=Path, required=True); parser.add_argument("--endpoint", type=Path, required=True); parser.add_argument("--output", type=Path, required=True); parser.add_argument("--deadline", type=float, required=True); args = parser.parse_args()
    raise SystemExit(asyncio.run(run(args)))
