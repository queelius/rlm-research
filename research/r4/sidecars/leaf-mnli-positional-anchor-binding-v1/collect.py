"""Four-worker checkpointed collector for the fixed positional-anchor96."""

import argparse
import asyncio
import hashlib
import json
import os
import time
from pathlib import Path

import httpx

import owner
import protocol as p
import scoring
import study as s


def summarize(rows):
    result = scoring.summarize(rows)
    costs = [row for row in rows if row.get("physical_attempt")]
    known = [row for row in costs if row.get("usage_observed")]
    result["costs"] = {"physical_requests": len(costs), "requests_with_usage": len(known), "unknown_usage": len(costs) - len(known), "prompt_tokens": sum(row["usage_observed"]["prompt_tokens"] for row in known), "completion_tokens": sum(row["usage_observed"]["completion_tokens"] for row in known), "provider_billing": "unknown/not measured"}
    return result


async def run(endpoint_path, output, deadline, transport=None):
    ready = s.verify()
    contexts = p.contexts()
    plan = s.read(s.ROOT / "inputs/PLAN.json")
    bodies = s.read(s.ROOT / "inputs/REQUESTS.json")
    wires = s.read(s.ROOT / "inputs/ORDERED_REQUESTS.json")
    prompts = s.read(s.ROOT / "inputs/PROMPT_IDS.json")
    native = s.read(s.ROOT / "inputs/CPU_NATIVE.json")
    tokenizer = s.tokenizer()
    endpoint = s.read(endpoint_path)
    s.service.validate_descriptor(endpoint, s.MODEL)
    output.mkdir(parents=True, exist_ok=False)
    (output / "calls").mkdir()
    started = time.time()
    call_deadline = deadline - 30
    s.write(output / "PLANNED_NULL_ENDPOINTS.json", [p.null_row(row, "not yet attempted") for row in plan])
    s.write(output / "RUN.json", {"identity": ready["identity"], "started_epoch": started, "work_deadline": deadline, "call_deadline": call_deadline, "workers": 4, "request_seconds": 90, "no_tools_executed": True})
    results = {}
    queue = asyncio.Queue()
    for row in plan:
        queue.put_nowait(row)
    headers = {"Authorization": "Bearer " + os.environ[endpoint["api_key_env"]], "Content-Type": "application/json"}
    base = f"http://{endpoint['host']}:{endpoint['port']}"

    async def dispatched(request):
        info = request.extensions["science_checkpoint"]
        s.write(info["directory"] / "REQUEST.json", {"ordered_body": request.content.decode(), "body_sha256": hashlib.sha256(request.content).hexdigest(), "expected_native_prompt_ids": info["prompt"], "dispatch_epoch": time.time()})
        info["result"]["physical_attempt"] = True

    async with httpx.AsyncClient(headers=headers, trust_env=False, transport=transport, timeout=90, event_hooks={"request": [dispatched]}) as client:
        async def worker():
            while not queue.empty() and time.time() < call_deadline:
                row = queue.get_nowait()
                key = row["id"]
                context = contexts[row["context_index"]]
                result = {"coordinate": row, "score": scoring.missing(context), "physical_attempt": False, "native_verified": False, "usage_observed": None, "started_epoch": time.time(), "error": None}
                directory = output / "calls" / key
                directory.mkdir()
                wire = wires[key].encode()
                try:
                    if json.loads(wire) != bodies[key] or hashlib.sha256(wire).hexdigest() != native["request_wire_sha256"][key]:
                        raise ValueError("frozen request changed")
                    request = client.build_request("POST", base + "/v1/chat/completions", content=wire)
                    request.extensions["science_checkpoint"] = {"directory": directory, "prompt": prompts[key], "result": result}
                    response = await asyncio.wait_for(client.send(request), timeout=min(90, max(0.001, call_deadline - time.time())))
                    result["status_code"] = response.status_code
                    s.write(directory / "RESPONSE.json", {"status_code": response.status_code, "body": response.text, "received_epoch": time.time()})
                    raw = response.json()
                    result["raw"] = raw
                    usage = raw.get("usage") if isinstance(raw, dict) else None
                    if isinstance(usage, dict) and all(type(usage.get(name)) is int and usage[name] >= 0 for name in ("prompt_tokens", "completion_tokens")):
                        result["usage_observed"] = {name: usage[name] for name in ("prompt_tokens", "completion_tokens")}
                    response.raise_for_status()
                    message, finish, _ = scoring.verified_response(raw, prompts[key], tokenizer)
                    result.update(native_verified=True, finish_reason=finish, length_capped=finish == "length", score=scoring.score(message, context, row["arm"]))
                except BaseException as caught:
                    result["error"] = {"type": type(caught).__name__, "message": str(caught)}
                    if isinstance(caught, asyncio.CancelledError):
                        raise
                finally:
                    result["elapsed_seconds"] = time.time() - result["started_epoch"]
                    results[key] = result
                    s.write(directory / "RESULT.json", result)
                    queue.task_done()

        tasks = [asyncio.create_task(worker()) for _ in range(4)]
        failure = None
        try:
            await asyncio.wait_for(asyncio.gather(*tasks), timeout=max(0.001, call_deadline - time.time()))
        except BaseException as caught:
            failure = {"type": type(caught).__name__, "message": str(caught)}
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
    rows = [results.get(row["id"], {"coordinate": row, "score": scoring.missing(contexts[row["context_index"]]), "physical_attempt": False, "native_verified": False, "usage_observed": None, "error": {"type": "PlannedNULL", "message": "cap before dispatch"}}) for row in plan]
    s.write(output / "ROWS.json", rows)
    s.write(output / "SUMMARY.json", summarize(rows))
    status = {"planned": 96, "recorded": len(rows), "available": sum(row["score"]["available"] for row in rows), "physical_attempts": sum(row["physical_attempt"] for row in rows), "inventory_complete": len(rows) == 96, "all_native_finals_available": all(row["score"]["available"] for row in rows), "orchestrator_error": failure, "elapsed_seconds": time.time() - started}
    s.write(output / "STATUS.json", status)
    return status


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("run",))
    parser.add_argument("--endpoint", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--deadline", required=True, type=float)
    args = parser.parse_args()
    owner.validate_argv([str(s.NATIVE), str(s.ROOT / "collect.py"), "run", "--endpoint", str(args.endpoint), "--output", str(args.output), "--deadline", str(args.deadline)])
    print(asyncio.run(run(args.endpoint, args.output, args.deadline)))
