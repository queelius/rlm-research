"""Durable four-worker native collector and balanced-class summaries."""

import argparse
import asyncio
import hashlib
import json
import os
import time
from pathlib import Path

import httpx

import protocol
import study as s

QSTUDY = s.load(
    "trec_followup_query_study",
    s.QUERY / "study.py",
    "962b9e5e7fb32f8f3e89caca1fa0a5b9de72e1bb58490648c5c706a29e79335f",
)


def unavailable(coordinate):
    return protocol.score(
        None, coordinate["ids"], {}, coordinate["pair"], coordinate["interface"], False
    )


def summarize(rows):
    cells = {}
    for row in rows:
        coordinate, score = row["coordinate"], row["score"]
        key = (coordinate["panel"], coordinate["model_policy"], coordinate["interface"])
        cell = cells.setdefault(
            key,
            {
                "planned_labels": 0,
                "strict_correct": 0,
                "null_labels": 0,
                "exact_batches": 0,
                "planned_batches": 0,
                "support": {label: 0 for label in protocol.PROJECTED},
                "null_support": {label: 0 for label in protocol.PROJECTED},
                "confusion": {label: {"tp": 0, "fp": 0, "fn": 0} for label in protocol.PROJECTED},
            },
        )
        cell["planned_batches"] += 1
        cell["planned_labels"] += coordinate["n"]
        cell["strict_correct"] += score["strict_correct"] or 0
        cell["null_labels"] += 0 if score["available"] else coordinate["n"]
        cell["exact_batches"] += bool(score["exact_batch"])
        for label in protocol.PROJECTED:
            cell["support"][label] += coordinate["target_support"][label]
            if not score["available"]:
                cell["null_support"][label] += coordinate["target_support"][label]
            for metric in ("tp", "fp", "fn"):
                cell["confusion"][label][metric] += (
                    (score.get("confusion") or {}).get(label, {}).get(metric, 0)
                )
    result = []
    for key, cell in sorted(cells.items()):
        lower_recalls = [
            cell["confusion"][label]["tp"] / support
            for label, support in cell["support"].items()
            if support
        ]
        upper_recalls = [
            (cell["confusion"][label]["tp"] + cell["null_support"][label]) / support
            for label, support in cell["support"].items()
            if support
        ]
        lower = sum(lower_recalls) / len(lower_recalls) if lower_recalls else None
        upper = sum(upper_recalls) / len(upper_recalls) if upper_recalls else None
        exact = not any(cell["null_support"].values())
        result.append(
            {
                "panel": key[0],
                "model_policy": key[1],
                "interface": key[2],
                "strict_bounds": [
                    cell["strict_correct"],
                    cell["strict_correct"] + cell["null_labels"],
                ],
                "balanced_accuracy": lower if exact else None,
                "balanced_accuracy_bounds": [lower, upper],
                **cell,
            }
        )
    return result


def harvest(output, plan):
    rows, pins = [], {}
    known = {"input": 0, "output": 0, "cached": 0}
    unknown = {"input": 0, "output": 0, "cached": 0}
    for coordinate in plan:
        path = Path(output) / "calls" / coordinate["id"] / "RESULT.json"
        row = (
            s.read(path)
            if path.exists()
            else {
                "coordinate": coordinate,
                "score": unavailable(coordinate),
                "error": "missing RESULT",
            }
        )
        if row["coordinate"] != coordinate:
            raise ValueError("coordinate identity")
        rows.append(row)
    attempted = responses = choices = 0
    for directory in sorted((Path(output) / "calls").glob("*")):
        if not directory.is_dir():
            continue
        request = directory / "REQUEST.json"
        response = directory / "RESPONSE.json"
        for path in directory.glob("*.json"):
            pins[str(path)] = s.sha(path)
        if not request.exists():
            continue
        attempted += 1
        raw = s.read(response).get("raw") if response.exists() else None
        responses += response.exists()
        choices += isinstance(raw, dict) and bool(raw.get("choices"))
        usage = raw.get("usage", {}) if isinstance(raw, dict) else {}
        for name, value in {
            "input": usage.get("prompt_tokens"),
            "output": usage.get("completion_tokens"),
            "cached": (usage.get("prompt_tokens_details") or {}).get("cached_tokens"),
        }.items():
            if type(value) is int and value >= 0:
                known[name] += value
            else:
                unknown[name] += 1
    return {
        "rows": rows,
        "cost": {
            "attempted": attempted,
            "responses": responses,
            "choice_bearing_completions": choices,
            "usage_known": known,
            "usage_unknown": unknown,
            "billing": None,
        },
        "files_sha256": pins,
    }


async def run(endpoint_path, output, deadline, policies, transport=None):
    ready = s.verify()
    all_plan = s.read(s.PREPARED / "EVAL_PLAN.json")
    plan = [row for row in all_plan if row["model_policy"] in policies]
    bodies = s.read(s.PREPARED / "REQUESTS.json")
    gold = s.read(s.PREPARED / "HOST_GOLD.json")["labels"]
    renderer, _ = QSTUDY.renderer()
    endpoint = s.read(endpoint_path)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    call_deadline = deadline - 30
    s.write(
        output / "RUN.json",
        {
            "identity": ready["identity"],
            "policies": sorted(policies),
            "planned": len(plan),
            "deadline": deadline,
            "workers": 4,
            "no_retry": True,
        },
    )
    queue = asyncio.Queue()
    for coordinate in plan:
        queue.put_nowait(coordinate)
    headers = {"Authorization": "Bearer " + os.environ[endpoint["api_key_env"]]}

    async def dispatched(request):
        info = request.extensions["science"]
        s.write(
            info["directory"] / "REQUEST.json",
            {
                "body": json.loads(request.content),
                "body_sha256": hashlib.sha256(request.content).hexdigest(),
                "coordinate": info["coordinate"],
                "dispatch_epoch": time.time(),
            },
        )

    async with httpx.AsyncClient(
        headers=headers,
        trust_env=False,
        timeout=90,
        transport=transport,
        event_hooks={"request": [dispatched]},
    ) as client:

        async def worker():
            while not queue.empty() and time.time() < call_deadline:
                coordinate = queue.get_nowait()
                directory = output / "calls" / coordinate["id"]
                directory.mkdir(parents=True)
                body = bodies[coordinate["id"]]
                result = {"coordinate": coordinate, "score": unavailable(coordinate), "error": None}
                try:
                    request = client.build_request(
                        "POST",
                        f"http://{endpoint['host']}:{endpoint['port']}/inference/v1/generate",
                        json=body,
                    )
                    request.extensions["science"] = {
                        "directory": directory,
                        "coordinate": coordinate,
                    }
                    response = await asyncio.wait_for(
                        client.send(request),
                        timeout=min(90, max(0.001, call_deadline - time.time())),
                    )
                    try:
                        raw = response.json()
                    except ValueError:
                        raw = None
                    s.write(
                        directory / "RESPONSE.json",
                        {
                            "status": response.status_code,
                            "body": response.text,
                            "raw": raw,
                            "received_epoch": time.time(),
                        },
                    )
                    response.raise_for_status()
                    native = protocol.native(raw, body, renderer)
                    result.update(
                        native=native,
                        score=protocol.score(
                            native["content"],
                            coordinate["ids"],
                            gold,
                            coordinate["pair"],
                            coordinate["interface"],
                            True,
                            native["tool_calls"],
                        ),
                    )
                except BaseException as error:
                    result["error"] = {"type": type(error).__name__, "message": str(error)}
                    if isinstance(error, asyncio.CancelledError):
                        raise
                finally:
                    s.write(directory / "RESULT.json", result)
                    queue.task_done()

        tasks = [asyncio.create_task(worker()) for _ in range(4)]
        await asyncio.wait_for(
            asyncio.gather(*tasks), timeout=max(0.001, call_deadline - time.time())
        )
    ledger = harvest(output, plan)
    s.write(output / "ROWS.json", ledger["rows"])
    s.write(output / "SUMMARY.json", summarize(ledger["rows"]))
    s.write(output / "COST.json", {key: value for key, value in ledger.items() if key != "rows"})
    return ledger


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--deadline", type=float, required=True)
    parser.add_argument("--policies", required=True)
    args = parser.parse_args()
    asyncio.run(run(args.endpoint, args.output, args.deadline, set(args.policies.split(","))))
