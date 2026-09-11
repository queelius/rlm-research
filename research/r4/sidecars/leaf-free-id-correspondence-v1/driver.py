"""Bounded native HTTP collector for the approved 96-call factorial."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import time
from copy import deepcopy
from pathlib import Path

import httpx

import service
import study as s


def verify(spec):
    if s.digest({k: v for k, v in spec.items() if k != "spec_id"}) != spec["spec_id"]:
        raise ValueError("spec identity changed")
    for path, expected in spec["source_sha256"].items():
        if s.sha(path) != expected:
            raise ValueError("source changed: " + path)
    design = s.build_design(s.build_data())
    design["rendered_prompts"] = spec["design"]["rendered_prompts"]
    if design != spec["design"]:
        raise ValueError("frozen design changed")
    for row in design["plan"]:
        body = s.make_request(design, row)
        if s.serialize(body) != s.serialize(spec["requests"][row["id"]]):
            raise ValueError("request changed: " + row["id"])
    for path, identity in spec["weight_stat_identity"].items():
        stat = Path(path).stat()
        if [stat.st_size, stat.st_mtime_ns, stat.st_ino] != identity:
            raise ValueError("previously byte-hashed model shard stat changed")


def wire_hook(spec, output):
    by_hash = {value: key for key, value in spec["ordered_request_sha256"].items()}

    async def capture(request):
        if request.method != "POST" or not request.url.path.endswith("/chat/completions"):
            return
        digest = hashlib.sha256(request.content).hexdigest()
        key = by_hash[digest]
        expected = s.serialize(spec["requests"][key]).encode()
        if request.content != expected:
            raise ValueError("actual ordered HTTP body differs")
        s.write_once(output / "wire" / f"{key}.json", {
            "coordinate_id": key,
            "body_sha256": digest,
            "body_utf8": request.content.decode(),
            "captured_epoch": time.time(),
            "credentials_recorded": False,
        })

    return capture


async def collect(client, url, spec, output, deadline):
    pending = iter(spec["design"]["plan"])
    records = []
    stop = asyncio.Event()

    async def worker():
        while not stop.is_set():
            row = next(pending, None)
            if row is None:
                return
            body = s.make_request(spec["design"], row)
            record = {"coordinate": row, "request_sha256": s.digest(body), "started": time.time(),
                      "model_called": False, "model_completed": False, "score": None, "usage": {}}
            try:
                record["model_called"] = True
                response = await client.post(url + "/chat/completions", json=body)
                record["http_status"] = response.status_code
                record["raw_response_text"] = response.text
                response.raise_for_status()
                raw = response.json()
                record["raw_response"] = raw
                if raw.get("model") != body["model"]:
                    raise ValueError("response model differs from bound alias")
                choice = raw["choices"][0]
                message = choice["message"]
                record["model_completed"] = True
                record["finish_reason"] = choice.get("finish_reason")
                record["tool_call_response"] = bool(message.get("tool_calls"))
                gold = spec["design"]["batches"][row["batch_id"]]["gold"]
                content = None if record["tool_call_response"] else message.get("content")
                record["score"] = s.score_content(content, gold)
                record["usage"] = raw.get("usage") or {}
                record["capture"] = {
                    "prompt_token_ids": isinstance(raw.get("prompt_token_ids"), list),
                    "output_token_ids": isinstance(choice.get("token_ids"), list),
                    "tools_executed": False,
                }
                expected = spec["design"]["rendered_prompts"][row["id"]]
                ids = raw.get("prompt_token_ids")
                if not isinstance(ids, list) or s.digest(ids) != expected["typed_token_ids_sha256"]:
                    raise ValueError("provider prompt IDs differ from frozen native renderer")
                if len(ids) != record["usage"].get("prompt_tokens"):
                    raise ValueError("provider prompt usage differs from prompt ID count")
            except asyncio.CancelledError:
                record["error"] = {"type": "CancelledError", "cost_unknown": True}
                raise
            except Exception as error:
                record["error"] = {"type": type(error).__name__, "message": str(error)[:1200]}
                stop.set()
            finally:
                record["ended"] = time.time()
                s.write_once(output / "calls" / f"{row['id']}.json", record)
                records.append(record)
                if len(records) % 12 == 0 or record.get("error"):
                    print(json.dumps({"recorded": len(records), "planned": 96,
                                      "error": record.get("error")}), flush=True)

    reason = None
    try:
        async with asyncio.timeout(max(0.001, deadline - time.time())):
            await asyncio.gather(*(worker() for _ in range(4)))
    except TimeoutError:
        reason = "collection_deadline"
    return records, reason or ("request_error" if stop.is_set() else None)


async def run(endpoint_path, output, deadline):
    spec = s.read(s.ROOT / "SPEC.json")
    verify(spec)
    endpoint = s.read(endpoint_path)
    service.validate_descriptor(endpoint, s.MODELS[s.MODEL])
    if output.resolve() != s.ROOT / "outputs/attempt-001/rollout":
        raise ValueError("only exact owned output namespace allowed")
    output.mkdir(parents=True, exist_ok=False)
    s.write_once(output / "SPEC.json", spec)
    s.write_once(output / "ENDPOINT.json", endpoint)
    started = time.time()
    reason = None
    records = []
    try:
        async with asyncio.timeout(max(0.001, deadline - time.time())):
            url = f"http://{endpoint['host']}:{endpoint['port']}/v1"
            headers = {"Authorization": "Bearer " + os.environ[endpoint["api_key_env"]]}
            async with httpx.AsyncClient(headers=headers, timeout=120, trust_env=False,
                                         event_hooks={"request": [wire_hook(spec, output)]}) as client:
                response = await client.get(url.removesuffix("/v1") + "/version")
                response.raise_for_status()
                if response.json().get("version") != "0.28.0":
                    raise ValueError("wrong vLLM version")
                response = await client.get(url + "/models")
                response.raise_for_status()
                service.validate_models(response.json(), s.MODELS[s.MODEL])
                records, reason = await collect(client, url, spec, output, deadline)
    except TimeoutError:
        reason = "collection_deadline"
    except BaseException as error:
        reason = type(error).__name__
        s.write_once(output / "ERROR.json", {"type": reason, "message": str(error)[:1200]})
    finally:
        records = [s.read(path) for path in sorted((output / "calls").glob("*.json"))]
        analysis = s.summarize(spec["design"], records)
        s.write_once(output / "analysis.json", analysis)
        seen = {r["coordinate"]["id"] for r in records}
        s.write_once(output / "STATUS.json", {
            "planned": 96,
            "recorded": len(records),
            "model_completed": sum(r.get("model_completed", False) for r in records),
            "stop_reason": reason,
            "elapsed_seconds": time.time() - started,
            "unrun": [r["id"] for r in spec["design"]["plan"] if r["id"] not in seen],
        })
    return 0 if reason is None and len(records) == 96 else 2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--endpoint", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--deadline", type=float)
    args = parser.parse_args()
    if args.command == "verify":
        verify(s.read(s.ROOT / "SPEC.json"))
        print("verified 96-call factorial; no model calls")
    else:
        raise SystemExit(asyncio.run(run(args.endpoint, args.output, args.deadline)))


if __name__ == "__main__":
    main()

