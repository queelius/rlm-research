"""Four-worker collector with durable native request/response checkpoints."""

import argparse
import asyncio
import hashlib
import json
import os
from pathlib import Path
import time

import httpx

import protocol as p
import study as s


def unavailable(coordinate):
    return p.score(None, coordinate["ids"], {}, coordinate["pair"], coordinate["interface"], False)


def harvest(output, plan):
    output = Path(output)
    rows, pins, physical = [], {}, []
    known = {"input": 0, "output": 0, "cached": 0}
    unknown = {"input": 0, "output": 0, "cached": 0}
    for coordinate in plan:
        path = output / "calls" / coordinate["id"] / "RESULT.json"
        if path.exists():
            row = s.read(path)
            if row["coordinate"] != coordinate:
                raise ValueError("result coordinate identity")
        else:
            row = {"coordinate": coordinate, "score": unavailable(coordinate), "error": "missing RESULT"}
        rows.append(row)
    attempted = responses = returned = 0
    for directory in sorted((output / "calls").glob("*")):
        if not directory.is_dir():
            continue
        request_path, response_path = directory / "REQUEST.json", directory / "RESPONSE.json"
        request = s.read(request_path) if request_path.exists() else None
        response = s.read(response_path) if response_path.exists() else None
        for path in directory.glob("*.json"):
            pins[str(path)] = s.sha(path)
        if request is None:
            continue
        attempted += 1
        responses += response is not None
        raw = (response or {}).get("raw")
        choice_bearing = isinstance(raw, dict) and isinstance(raw.get("choices"), list) and bool(raw["choices"])
        returned += choice_bearing
        usage = raw.get("usage", {}) if isinstance(raw, dict) else {}
        values = {
            "input": usage.get("prompt_tokens"),
            "output": usage.get("completion_tokens"),
            "cached": (usage.get("prompt_tokens_details") or {}).get("cached_tokens"),
        }
        for key, value in values.items():
            if type(value) is int and value >= 0:
                known[key] += value
            else:
                unknown[key] += 1
        physical.append({"id": directory.name, "status": (response or {}).get("status"), "choice_bearing": choice_bearing})
    return {
        "rows": rows,
        "cost": {"attempted": attempted, "responses": responses, "choice_bearing_completions": returned, "usage_known": known, "usage_unknown": unknown, "billing": None},
        "physical": physical,
        "files_sha256": pins,
    }


def summarize(rows):
    cells = {}
    for row in rows:
        coordinate = row["coordinate"]
        key = (coordinate["model_policy"], coordinate["interface"])
        cell = cells.setdefault(key, {"planned_labels": 0, "strict_correct": 0, "null_labels": 0, "exact_batches": 0, "planned_batches": 0, "confusion": {label: {"tp": 0, "fp": 0, "fn": 0} for label in p.PROJECTED}})
        cell["planned_batches"] += 1
        cell["planned_labels"] += coordinate["n"]
        score = row["score"]
        cell["strict_correct"] += score["strict_correct"] or 0
        cell["null_labels"] += 0 if score["available"] else coordinate["n"]
        cell["exact_batches"] += bool(score["exact_batch"])
        for label, counts in (score.get("confusion") or {}).items():
            for name, value in counts.items():
                cell["confusion"][label][name] += value
    return [dict(model_policy=key[0], interface=key[1], strict_bounds=[value["strict_correct"], value["strict_correct"] + value["null_labels"]], **value) for key, value in sorted(cells.items())]


async def run(endpoint_path, output, deadline, transport=None):
    ready = s.verify()
    plan = s.read(s.ROOT / "inputs/PLAN.json")
    bodies = s.read(s.ROOT / "inputs/REQUESTS.json")
    gold = s.read(s.ROOT / "inputs/HOST_GOLD.json")["labels"]
    renderer, _ = s.renderer()
    endpoint = s.read(endpoint_path)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    started, call_deadline = time.time(), deadline - 30
    s.write(output / "PLANNED.json", plan)
    s.write(output / "RUN.json", {"identity": ready["identity"], "started_epoch": started, "work_deadline": deadline, "call_deadline": call_deadline, "workers": 4, "per_call_cap": 90, "no_retry": True})
    queue = asyncio.Queue()
    for coordinate in plan:
        queue.put_nowait(coordinate)
    headers = {"Authorization": "Bearer " + os.environ[endpoint["api_key_env"]]}

    async def dispatched(request):
        info = request.extensions["science"]
        s.write(info["directory"] / "REQUEST.json", {"body": json.loads(request.content), "body_sha256": hashlib.sha256(request.content).hexdigest(), "dispatch_epoch": time.time(), "prepared_epoch": info["prepared"], "coordinate": info["coordinate"]})

    async with httpx.AsyncClient(headers=headers, trust_env=False, timeout=90, transport=transport, event_hooks={"request": [dispatched]}) as client:
        async def worker():
            while not queue.empty() and time.time() < call_deadline:
                coordinate = queue.get_nowait()
                directory = output / "calls" / coordinate["id"]
                directory.mkdir(parents=True)
                prepared = time.time()
                body = bodies[coordinate["id"]]
                result = {"coordinate": coordinate, "score": unavailable(coordinate), "prepared_epoch": prepared, "error": None}
                s.write(directory / "PREPARED.json", {"coordinate": coordinate, "body": body, "prepared_epoch": prepared})
                try:
                    request = client.build_request("POST", f'http://{endpoint["host"]}:{endpoint["port"]}/inference/v1/generate', json=body, headers={"x-science-call": coordinate["id"]})
                    request.extensions["science"] = {"directory": directory, "prepared": prepared, "coordinate": coordinate}
                    response = await asyncio.wait_for(client.send(request), timeout=min(90, max(0.001, call_deadline - time.time())))
                    try:
                        raw = response.json()
                    except ValueError:
                        raw = None
                    s.write(directory / "RESPONSE.json", {"status": response.status_code, "body": response.text, "raw": raw, "received_epoch": time.time()})
                    response.raise_for_status()
                    native = p.native(raw, body, renderer)
                    result.update(native=native, score=p.score(native["content"], coordinate["ids"], gold, coordinate["pair"], coordinate["interface"], True, native["tool_calls"]))
                except BaseException as error:
                    result["error"] = {"type": type(error).__name__, "message": str(error)}
                    if isinstance(error, asyncio.CancelledError):
                        raise
                finally:
                    result.update(ended_epoch=time.time(), elapsed_seconds=time.time() - prepared)
                    s.write(directory / "RESULT.json", result)
                    queue.task_done()

        tasks = [asyncio.create_task(worker()) for _ in range(4)]
        orchestrator_error = None
        try:
            await asyncio.wait_for(asyncio.gather(*tasks), timeout=max(0.001, call_deadline - time.time()))
        except BaseException as error:
            orchestrator_error = {"type": type(error).__name__, "message": str(error)}
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
    result = harvest(output, plan)
    s.write(output / "ROWS.json", result["rows"])
    s.write(output / "COST.json", {key: value for key, value in result.items() if key != "rows"})
    s.write(output / "SUMMARY.json", summarize(result["rows"]))
    s.write(output / "STATUS.json", {"planned": len(plan), "elapsed_seconds": time.time() - started, "physical": result["cost"], "orchestrator_complete": orchestrator_error is None, "orchestrator_error": orchestrator_error})
    return result


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--deadline", type=float, required=True)
    return parser.parse_args(argv)


def main():
    args = parse_args()
    asyncio.run(run(args.endpoint, args.output, args.deadline))


if __name__ == "__main__":
    main()
