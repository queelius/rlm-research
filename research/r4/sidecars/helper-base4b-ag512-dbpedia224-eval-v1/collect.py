"""Exact two-label-space decoder and raw request/response persistence."""

import json
import os
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import study


def unique_object(pairs):
    value = dict(pairs)
    if len(value) != len(pairs):
        raise ValueError("duplicate JSON keys")
    return value


def decode(row, response, tokenizer, started, ended):
    usage = (response.get("usage") or {}) if isinstance(response, dict) else {}
    result = {
        "call_id": row["call_id"],
        "dataset": row["dataset"],
        "start": row["start"],
        "ids": row["ids"],
        "seed": row["body"]["sampling_params"]["seed"],
        "request_body_sha256": study.digest(row["body"]),
        "status": "invalid_response",
        "prediction": {},
        "started_epoch": started,
        "ended_epoch": ended,
        "wall_seconds": ended - started,
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"),
        "cached_prompt_tokens": (usage.get("prompt_tokens_details") or {}).get("cached_tokens"),
        "raw_response_sha256": study.digest(response),
    }
    try:
        choices = response["choices"]
        if len(choices) != 1:
            raise ValueError("exactly one native choice required")
        choice = choices[0]
        tokens = choice["token_ids"]
        text = tokenizer.decode(tokens, skip_special_tokens=True)
        result.update(
            request_id=response.get("request_id"),
            model=response.get("model"),
            finish_reason=choice.get("finish_reason"),
            completion_ids=tokens,
            decoded_text=text,
        )
        if (
            not tokens
            or any(type(token) is not int or not 0 <= token < 151936 for token in tokens)
            or choice.get("finish_reason") != "stop"
            or tokens[-1] not in (151645, 151643)
            or not isinstance(response.get("request_id"), str)
            or not response["request_id"]
            or response.get("model") != study.BASE_ALIAS
            or usage.get("prompt_tokens") != len(row["body"]["token_ids"])
            or usage.get("completion_tokens") != len(tokens)
            or len(tokens) > 1024
        ):
            raise ValueError("native base token/finish/usage inventory differs")
        parsed = json.loads(text, object_pairs_hook=unique_object)
        if not isinstance(parsed, dict) or list(parsed) != row["ids"] or set(parsed) != set(row["ids"]):
            raise ValueError("prediction does not contain exact requested IDs in order")
        if any(value not in study.LABELS[row["dataset"]] for value in parsed.values()):
            raise ValueError("prediction contains a non-canonical panel label")
        result.update(
            status="returned_valid",
            prediction=parsed,
            returned_logprob_entries=len((choice.get("logprobs") or {}).get("content", [])),
        )
    except Exception as error:
        result.update(
            status="invalid_response",
            prediction={},
            validation_error={"type": type(error).__name__, "message": str(error)},
        )
    return result


def headers():
    credential = os.environ.get("STRICT_RLM_CALIBRATION_API_KEY", "")
    if not credential:
        raise ValueError("missing inherited private endpoint credential")
    return {"content-type": "application/json", "authorization": "Bearer " + credential}


def write_bytes(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(payload)


def send(endpoint, row, tokenizer, output, deadline):
    started = time.time()
    request_path = output / "native" / (row["call_id"] + "-REQUEST.json")
    response_path = output / "native" / (row["call_id"] + "-RESPONSE.json")
    payload = json.dumps(row["body"], separators=(",", ":")).encode()
    write_bytes(request_path, payload)
    result = {
        "call_id": row["call_id"],
        "dataset": row["dataset"],
        "start": row["start"],
        "ids": row["ids"],
        "status": "request_error",
        "started_epoch": started,
    }
    try:
        remaining = deadline - started
        if remaining <= 0:
            raise TimeoutError("owner deadline reached before native request")
        request = Request(endpoint, data=payload, headers=headers(), method="POST")
        try:
            with urlopen(request, timeout=min(180, remaining)) as response:
                raw, status = response.read(), response.status
        except HTTPError as error:
            raw, status = error.read(), error.code
        write_bytes(response_path, raw)
        result = decode(row, json.loads(raw), tokenizer, started, time.time())
        if status != 200:
            result.update(status="invalid_response", prediction={}, validation_error="HTTP non-200")
        result.update(
            http_status=status,
            raw_response_path=str(response_path),
            raw_response_bytes_sha256=study.sha(response_path),
        )
    except Exception as error:
        result.update(
            error={"type": type(error).__name__, "message": str(error)},
            ended_epoch=time.time(),
            wall_seconds=time.time() - started,
        )
        if response_path.exists():
            result.update(
                raw_response_path=str(response_path),
                raw_response_bytes_sha256=study.sha(response_path),
            )
    result.update(
        raw_request_path=str(request_path),
        raw_request_bytes_sha256=study.sha(request_path),
        request_body_sha256=study.digest(row["body"]),
        requested_prompt_tokens=len(row["body"]["token_ids"]),
        requested_seed=row["body"]["sampling_params"]["seed"],
        credentials_persisted=False,
    )
    return result

