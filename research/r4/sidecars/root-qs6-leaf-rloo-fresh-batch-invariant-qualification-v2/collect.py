"""V2 native normalization from exact token IDs using the pinned tokenizer."""

from concurrent.futures import ThreadPoolExecutor, as_completed
import copy
import functools
import hashlib
import importlib.util
import json
from pathlib import Path
import threading

import study


_spec = importlib.util.spec_from_file_location("fresh_helper_qualification_v1_collect", study.V1_ROOT / "collect.py")
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)
base.study = study


@functools.lru_cache(maxsize=1)
def tokenizer():
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(study.BASE_MODEL, local_files_only=True)


def tokenizer_receipt():
    files = {str(path): study.sha(path) for path in study.TOKENIZER_FILES}
    return {
        "path": str(study.BASE_MODEL),
        "files_sha256": files,
        "identity_sha256": study.digest(files),
        "decode": "AutoTokenizer.decode(action_ids, skip_special_tokens=True)",
    }


def response_record(row, response, decoder, started, ended, gold):
    choices = response.get("choices")
    if not isinstance(choices, list) or len(choices) != 1:
        raise ValueError("native response must contain exactly one choice")
    action_ids = choices[0].get("token_ids")
    if not isinstance(action_ids, list) or not action_ids:
        raise ValueError("native response has no action token IDs")
    decoded = decoder.decode(action_ids, skip_special_tokens=True)
    patched = copy.deepcopy(response)
    patched["choices"][0]["text"] = decoded
    record = base.response_record(row, patched, started, ended, gold)
    prediction = json.loads(decoded)
    receipt = tokenizer_receipt()
    record.update(
        prediction=prediction,
        decoded_text=decoded,
        decoded_text_sha256=hashlib.sha256(decoded.encode()).hexdigest(),
        decoded_from_exact_action_ids=True,
        tokenizer_path=receipt["path"],
        tokenizer_identity_sha256=receipt["identity_sha256"],
    )
    return record


def persist_raw_and_normalize(row, response, started, ended, gold, raw_dir, decoder, *, request_payload, response_payload):
    request_path = Path(raw_dir) / f"{row['coordinate_id']}-REQUEST.json"
    response_path = Path(raw_dir) / f"{row['coordinate_id']}-RESPONSE.json"
    base.write_raw_x(request_path, request_payload)
    base.write_raw_x(response_path, response_payload)
    if json.loads(request_payload) != row["body"] or json.loads(response_payload) != response:
        raise ValueError("persisted native bytes differ from parsed request/response")
    record = response_record(row, response, decoder, started, ended, gold)
    record.update(
        raw_request_path=str(request_path),
        raw_request_sha256=hashlib.sha256(request_payload).hexdigest(),
        raw_response_path=str(response_path),
        raw_response_sha256=hashlib.sha256(response_payload).hexdigest(),
    )
    return record


def send(endpoint, row, gold, raw_dir, decoder, barrier=None):
    import os
    import time
    from urllib.request import Request, urlopen

    if barrier is not None:
        barrier.wait(timeout=15)
    credential = os.environ.get("STRICT_RLM_CALIBRATION_API_KEY")
    if not credential:
        raise ValueError("inherited private credential required")
    started = time.time()
    payload = json.dumps(row["body"], separators=(",", ":")).encode()
    request = Request(
        endpoint,
        data=payload,
        headers={"content-type": "application/json", "authorization": "Bearer " + credential},
        method="POST",
    )
    with urlopen(request, timeout=180) as reply:
        raw_response = reply.read()
    response = json.loads(raw_response)
    return persist_raw_and_normalize(
        row,
        response,
        started,
        time.time(),
        gold,
        raw_dir,
        decoder,
        request_payload=payload,
        response_payload=raw_response,
    )


def collect(endpoint, rows, output):
    gold = study.read(study.HOST_GOLD)
    decoder = tokenizer()
    results = []
    for start in range(0, len(rows), 4):
        wave = rows[start : start + 4]
        barrier = threading.Barrier(len(wave))
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = [
                pool.submit(send, endpoint, row, gold, output / "native", decoder, barrier)
                for row in wave
            ]
            for future in as_completed(futures):
                record = future.result()
                study.write_x(output / "calls" / f"{record['coordinate_id']}.json", record)
                results.append(record)
    results.sort(key=lambda row: (row["context_id"], row["repeat"]))
    if len(results) != 48 or sorted(sum(row["context_id"] == context for row in results) for context in study.CONTEXTS) != [24, 24]:
        raise ValueError("fresh collection inventory is incomplete")
    if len({row["request_id"] for row in results}) != 48:
        raise ValueError("native provider request IDs are not unique across 48 actions")
    study.write_x(
        output / "COLLECTION.json",
        {
            "schema": "fresh-batch-invariant-helper-collection-v2-token-decoded",
            "fresh_actions": 48,
            "historical_actions_or_logprobs_used": False,
            "concurrency": 4,
            "temperature": 0.5,
            "tokenizer": tokenizer_receipt(),
            "records": results,
        },
    )
    return results
