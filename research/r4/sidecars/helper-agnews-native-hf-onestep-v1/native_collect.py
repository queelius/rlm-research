"""Exact decoded native responses, with explicit4-key/128-call accounting."""

import ast
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import Request, urlopen

import ag_study as study

base = study.load("ag_native_v2_decoder", study.QUAL2 / "collect.py", {"study": study})
source = (study.QUAL / "collect.py").read_text()
for old, new in (
    ("len(prediction) != 16", "len(prediction) != 4"),
    ('"reward": correct / 16', '"reward": correct / 4'),
):
    if source.count(old) != 1:
        raise ValueError("sealed response normalization seam differs")
    source = source.replace(old, new)
tree = ast.parse(source)
function = next(
    node
    for node in tree.body
    if isinstance(node, ast.FunctionDef) and node.name == "response_record"
)
exec(
    compile(ast.Module(body=[function], type_ignores=[]), str(study.QUAL / "collect.py"), "exec"),
    base.base.__dict__,
)
base.base.study = study
tokenizer = base.tokenizer
response_record = base.response_record
persist_raw_and_normalize = base.persist_raw_and_normalize


def send(endpoint, row, gold, directory, decoder, deadline):
    credential = os.environ.get("STRICT_RLM_CALIBRATION_API_KEY")
    if not credential:
        raise ValueError("inherited private credential required")
    started = time.time()
    remaining = deadline - started
    if remaining <= 0:
        raise TimeoutError("native phase deadline before request")
    payload = json.dumps(row["body"], separators=(",", ":")).encode()
    request = Request(
        endpoint,
        data=payload,
        method="POST",
        headers={"content-type": "application/json", "authorization": "Bearer " + credential},
    )
    with urlopen(request, timeout=min(180, remaining)) as response:
        raw = response.read()
    return persist_raw_and_normalize(
        row,
        json.loads(raw),
        started,
        time.time(),
        gold,
        directory,
        decoder,
        request_payload=payload,
        response_payload=raw,
    )


def collect(endpoint, rows, output, deadline):
    decoder = tokenizer()
    gold = study.read(study.HOST_GOLD)
    completed, errors = [], []
    for start in range(0, len(rows), 4):
        if time.time() >= deadline:
            errors.append({"stage": "native", "error": "native phase deadline before next wave"})
            break
        wave = rows[start : start + 4]
        # Existing native send persists exact request/response bytes before validation.
        with ThreadPoolExecutor(max_workers=4) as pool:
            jobs = {
                pool.submit(send, endpoint, row, gold, output / "native", decoder, deadline): row
                for row in wave
            }
            for future in as_completed(jobs):
                row = jobs[future]
                try:
                    record = future.result()
                    study.write_x(output / "calls" / f"{row['coordinate_id']}.json", record)
                    completed.append(record)
                except BaseException as error:
                    request_path = output / "native" / f"{row['coordinate_id']}-REQUEST.json"
                    if not request_path.exists():
                        base.base.write_raw_x(
                            request_path, json.dumps(row["body"], separators=(",", ":")).encode()
                        )
                    failure = {
                        "coordinate_id": row["coordinate_id"],
                        "context_id": row["context_id"],
                        "repeat": row["repeat"],
                        "error_type": type(error).__name__,
                        "error": str(error),
                        "body_sha256": study.digest(row["body"]),
                        "cost_if_no_response_usage": "unknown",
                    }
                    study.write_x(output / "calls" / f"{row['coordinate_id']}-ERROR.json", failure)
                    errors.append(failure)
        if errors:
            break
    order = {row["coordinate_id"]: index for index, row in enumerate(rows)}
    completed.sort(key=lambda row: order[row["coordinate_id"]])
    result = {
        "schema": "agnews-native-hf-collection-v1",
        "planned_actions": 128,
        "fresh_actions": len(completed),
        "historical_actions_or_logprobs_used": False,
        "temperature": 0.5,
        "concurrency": 4,
        "records": completed,
        "errors": errors,
        "unavailable_actions": 128 - len(completed),
        "tokenizer": base.tokenizer_receipt(),
        "schedule_sha256": study.digest(rows),
        "cost": {
            "scope": "successful-call observed subtotal; errors may have additional raw usage",
            "prompt_tokens": sum(row["prompt_tokens"] for row in completed),
            "completion_tokens": sum(row["completion_tokens"] for row in completed),
            "failed_or_deadline_entries": len(errors),
            "error_usage_not_in_subtotal": len(errors),
        },
    }
    study.write_x(output / "COLLECTION.json", result)
    if errors or len(completed) != 128 or len({row["request_id"] for row in completed}) != 128:
        raise ValueError("native128 inventory incomplete; no subset/retry/update")
    return result


def lifecycle():
    value = study.load(
        "ag_native_frozen_lifecycle",
        study.QUAL / "owner.py",
        {"study": study, "collect": sys.modules[__name__]},
    )
    value.study = study
    return value
