"""Sixteen fixed leaf acquisitions followed by 64 root episodes."""

import argparse
import asyncio
import json
import os
from pathlib import Path
import time
from types import SimpleNamespace

import httpx
import protocol as p
import study as s


def root_implementation():
    original = s.load("downstream_recovery_collect", s.SCALE / "collect.py",
        "3074eb6cf05f20c07f7d9eef7a6be859f02a9d38afbfd2af6cd46ade595a67df", {"study": s})
    module = original.implementation(); module.s = s; module.p = s.protocol(); module.b = s
    return module


def decode_native(raw, prompt_ids):
    if len(raw.get("choices", [])) != 1: raise ValueError("native choice identity")
    choice = raw["choices"][0]; ids = choice.get("token_ids")
    if not isinstance(ids, list) or not ids: raise ValueError("missing completion ids")
    usage = raw.get("usage", {})
    if usage.get("prompt_tokens") != len(prompt_ids) or usage.get("completion_tokens") != len(ids):
        raise ValueError("native usage identity")
    # Native responses end with the tokenizer EOS; parse the authoritative assistant message.
    renderer = s.qnative.stack().native.renderer()
    message = renderer.parse_response(ids)
    if message.tool_calls or choice.get("finish_reason") not in ("stop", "length"):
        raise ValueError("leaf wrong route")
    return message.content, {"prompt_tokens": usage["prompt_tokens"], "completion_tokens": usage["completion_tokens"]}


async def acquire(endpoint, output, deadline, transport=None):
    requests = s.read(s.INPUTS / "LEAF_REQUESTS.json")
    prompts = s.read(s.INPUTS / "LEAF_PROMPT_IDS.json")
    full = {c["id"]: c for c in s.read(s.INPUTS / "DATA.json")["contexts"]}
    descriptor = s.read(endpoint); base = f'http://{descriptor["host"]}:{descriptor["port"]}'
    headers = {"Authorization": "Bearer " + os.environ[descriptor["api_key_env"]], "Content-Type": "application/json"}
    target = Path(output) / "leaf"; target.mkdir(parents=True); maps = {e: {} for e in p.ENCODINGS}; rows = []
    queue = asyncio.Queue()
    for encoding in p.ENCODINGS:
        for context_id in sorted(requests[encoding]): queue.put_nowait((encoding, context_id))
    async with httpx.AsyncClient(headers=headers, trust_env=False, transport=transport, timeout=90) as client:
        async def worker():
            while not queue.empty():
                encoding, context_id = queue.get_nowait(); directory = target / encoding / context_id; directory.mkdir(parents=True)
                result = {"encoding": encoding, "context_id": context_id, "available": False, "observed_invalid": False}
                try:
                    body = requests[encoding][context_id]
                    response = await asyncio.wait_for(client.post(base + "/v1/chat/completions", json=body), min(90, max(.001, deadline - time.time())))
                    s.write(directory / "RESPONSE.json", {"status": response.status_code, "body": response.text})
                    response.raise_for_status(); raw = response.json()
                    content, usage = decode_native(raw, prompts[encoding][context_id])
                    result.update(available=True, usage=usage, finish_reason=raw["choices"][0]["finish_reason"])
                    maps[encoding][context_id] = p.broker(content, full[context_id], encoding)
                except Exception as error:
                    result.update(error={"type": type(error).__name__, "message": str(error)}, observed_invalid=result["available"])
                s.write(directory / "RESULT.json", result); rows.append(result); queue.task_done()
        await asyncio.gather(*(worker() for _ in range(4)))
    s.write(target / "ROWS.json", rows)
    if len(rows) != 16 or any(not row["available"] or row["observed_invalid"] for row in rows):
        return None
    s.write(Path(output) / "PREDICTED_MAPS.json", maps)
    return maps


async def run(args, transport=None):
    s.verify(); binding = s.read(args.binding)
    if binding != s.binding(): raise ValueError("actual binding changed")
    args.output.mkdir(parents=True, exist_ok=False)
    maps = await acquire(args.endpoint, args.output, args.deadline - 120, transport)
    if maps is None:
        s.write(args.output / "STATUS.json", {"complete": False, "reason": "leaf acquisition invalid or unavailable"}); return 1
    s.ACTIVE_MAPS = maps
    module = root_implementation()
    root_args = SimpleNamespace(mode="free", plan="FREE_PLAN.json", binding=args.binding,
        endpoint=args.endpoint, output=args.output / "root", start=0, stop=64, deadline=args.deadline)
    with s.aliases({"od_study": s, "od_protocol": s.protocol(), "od_binding": s}):
        await module.run(root_args)
    recorded = len(list((args.output / "root").glob("*/RESULT.json")))
    complete = recorded == 64
    s.write(args.output / "STATUS.json", {"complete": complete, "leaf": 16, "root_recorded": recorded, "root_planned": 64, "no_retry": True})
    return 0 if complete else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--binding", type=Path, required=True)
    parser.add_argument("--endpoint", type=Path, required=True); parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--deadline", type=float, required=True); args = parser.parse_args()
    raise SystemExit(asyncio.run(run(args)))
