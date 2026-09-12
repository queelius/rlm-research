"""Qualified native token decoder plus new exact raw request/response persistence."""

import json
import sys
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import study

source = study.rl.load_bound(
    "fresh512_qualified_native_decoder",
    study.SIDE / "helper-unseen-generalization-c32-baseline-v1/owner.py",
    {"unseen_panel_study": sys.modules[study.__name__]},
)


def unique_object(pairs):
    value = dict(pairs)
    if len(value) != len(pairs):
        raise ValueError("duplicate JSON keys")
    return value


def decode(row, response, tokenizer, started, ended):
    usage = (response.get("usage") or {}) if isinstance(response, dict) else {}
    result = {
        "call_id": row["call_id"],
        "dataset": "ag_news",
        "start": row["start"],
        "ids": row["ids"],
        "status": "invalid_response",
        "prediction": {},
        "started_epoch": started,
        "ended_epoch": ended,
        "wall_seconds": ended - started,
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "cached_prompt_tokens": (usage.get("prompt_tokens_details") or {}).get("cached_tokens"),
    }
    try:
        choices = response["choices"]
        if len(choices) != 1:
            raise ValueError("exactly one native choice required")
        choice = choices[0]
        tokens = choice["token_ids"]
        result.update(
            request_id=response.get("request_id"),
            model=response.get("model"),
            completion_ids=tokens,
            finish_reason=choice.get("finish_reason"),
            decoded_text=tokenizer.decode(tokens, skip_special_tokens=True),
        )
        if (
            not tokens
            or any(type(token) is not int or not 0 <= token < 151936 for token in tokens)
            or choice.get("finish_reason") != "stop"
            or tokens[-1] not in (151645, 151643)
            or not isinstance(response.get("request_id"), str)
            or not response["request_id"]
            or response.get("model") != study.CHILD_ALIAS
            or usage.get("prompt_tokens") != len(row["body"]["token_ids"])
            or usage.get("completion_tokens") != len(tokens)
            or len(tokens) > 1024
        ):
            raise ValueError("native token/finish/usage inventory differs")
        result.update(source.response_record(row, response, tokenizer, started, ended))
        parsed = json.loads(result["decoded_text"], object_pairs_hook=unique_object)
        source.validate_prediction(parsed, row["ids"], "ag_news")
        if result["status"] != "returned_valid":
            raise ValueError("qualified decoder rejected prediction")
        result["returned_logprob_entries"] = len((choice.get("logprobs") or {}).get("content", []))
    except Exception as error:
        result.update(
            status="invalid_response",
            prediction={},
            validation_error={"type": type(error).__name__, "message": str(error)},
        )
    return result


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
        "dataset": "ag_news",
        "start": row["start"],
        "ids": row["ids"],
        "status": "request_error",
        "started_epoch": started,
    }
    try:
        remaining = deadline - started
        if remaining <= 0:
            raise TimeoutError("per-arm deadline reached before native request")
        request = Request(endpoint, data=payload, headers=source.headers(), method="POST")
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
        schema_ordered_sha256=study.rl.original.hashlib.sha256(
            row["schema_ordered_json"].encode()
        ).hexdigest(),
        credentials_persisted=False,
    )
    return result
