"""Six direct MRCR controls, full inputs, fixed2048 output cap, no truncation/retry/tools.

Exploratory follow-up selected after the paired rootless pilot. Same original4B
weights/documents/questions/seeds, but native Chat Completions direct serving,
not the pilot's native TrainClient. This is a whole-scaffold+client comparison,
not a clean estimate of decomposition alone. Record context-limit errors as null.
"""

from __future__ import annotations

import asyncio
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent
PILOT = ROOT.parent / "mrcr-rootless-document-baseline-v2/outputs/attempt-001"
ENDPOINT = ROOT.parents[1] / "operations/2026-09-08-resume/inference-frozen-contract-attempt-001/endpoint.json"
LEAF = ROOT.parent / "trec-leaf-contract-probe-v1/driver.py"
SCORING = ROOT.parent / "mrcr-context-sketch-v1/source/mrcr_context_sketch/scoring.py"


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def request_body(context, question, model, seed):
    return {
        "model": model,
        "messages": [{"role": "user", "content": context + "\n\n" + question}],
        "temperature": 0,
        "top_p": 1,
        "top_k": -1,
        "min_p": 0,
        "max_tokens": 2048,
        "seed": seed,
    }


async def main():
    helper, scoring = module("leaf_helpers", LEAF), module("mrcr_metric", SCORING)
    endpoint = json.loads(ENDPOINT.read_text())
    helper.verify_weights(endpoint)
    tasks = json.loads((PILOT / "tasks.json").read_text())
    source_spec = json.loads((PILOT / "SPEC.json").read_text())
    gold = json.loads((PILOT / "host-scoring.json").read_text())
    selected = [row for row in source_spec["plan"] if row["arm"] == "vanilla"]
    task_by_name = {task["name"]: task for task in tasks}
    assert len(selected) == len({r["document_sha256"] for r in selected}) == 6
    requests = []
    sources = [Path(__file__), LEAF, SCORING, ENDPOINT, PILOT / "SPEC.json",
               PILOT / "tasks.json", PILOT / "host-scoring.json"]
    for row in selected:
        path = PILOT / "contexts" / (row["document_sha256"] + ".txt")
        if helper.file_hash(path) != row["document_sha256"]:
            raise ValueError("context bytes changed")
        sources.append(path)
        question = task_by_name[row["task_name"]]["prompt"].split("\n\nQuestion:\n", 1)[1]
        body = request_body(path.read_text(), question, endpoint["model_alias"], row["seed"])
        requests.append({"coordinate": row, "request": body})
    attempt = ROOT / "outputs/attempt-001"
    attempt.mkdir(parents=True, exist_ok=False)
    spec = {
        "question": "How does direct full-input4B retrieval compare with the whole RLM scaffold?",
        "scope": __doc__, "requests": requests, "endpoint": endpoint,
        "source_sha256": {str(path): helper.file_hash(path) for path in sources},
        "concurrency": 4, "per_call_seconds": 120, "wall_cap_seconds": 300,
        "python": sys.version, "client": "httpx " + httpx.__version__,
    }
    spec["spec_id"] = helper.digest(spec)
    helper.write_once(attempt / "SPEC.json", spec)
    address = f"http://{endpoint['host']}:{endpoint['port']}"
    semaphore = asyncio.Semaphore(4)
    records = []
    started = time.time()
    async with httpx.AsyncClient(timeout=120, headers={
        "Authorization": "Bearer " + os.environ[endpoint["api_key_env"]]
    }) as client:
        advertised = await client.get(address + "/v1/models")
        advertised.raise_for_status()
        if endpoint["model_alias"] not in {r["id"] for r in advertised.json()["data"]}:
            raise ValueError("frozen alias is not loaded")
        helper.write_once(attempt / "SERVER.json", advertised.json())

        async def one(item):
            async with semaphore:
                begin = time.time()
                record = {"coordinate": item["coordinate"], "spec_id": spec["spec_id"],
                          "request_sha256": helper.digest(item["request"])}
                try:
                    response = await client.post(address + "/v1/chat/completions", json=item["request"])
                    record.update(http_status=response.status_code, raw_body=response.text)
                    response.raise_for_status()
                    raw = response.json()
                    choice = raw["choices"][0]
                    prediction = choice["message"].get("content")
                    finish = choice.get("finish_reason")
                    complete = finish == "stop" and not choice["message"].get("tool_calls")
                    record.update(response=raw, prediction=prediction, finish_reason=finish,
                                  error=None, complete=complete,
                                  score=scoring.score_terminal(prediction=prediction,
                                      target=gold[item["coordinate"]["row_id"]],
                                      status="completed" if complete else "invalid"))
                    if not complete:
                        record["score"] = None
                except (httpx.HTTPError, ValueError, KeyError, IndexError) as error:
                    record.update(error={"type": type(error).__name__, "message": str(error)},
                                  complete=False, score=None)
                record.update(started=begin, ended=time.time(), wall_seconds=time.time()-begin)
                helper.write_once(attempt / (item["coordinate"]["row_id"] + ".json"), record)
                records.append(record)
                print(json.dumps({"recorded": len(records), "complete": record["complete"],
                                  "score": record["score"], "error": record["error"]}), flush=True)

        await asyncio.wait_for(asyncio.gather(*(one(item) for item in requests)), timeout=300)
    helper.write_once(attempt / "STATUS.json", {
        "recorded": len(records), "planned": 6, "wall_seconds": time.time()-started,
        "complete": sum(r["complete"] for r in records),
        "errors": sum(r["error"] is not None for r in records),
    })


if __name__ == "__main__":
    asyncio.run(main())
