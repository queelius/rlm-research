"""Bounded native HTTP collector for the role/tool/output-contract screen."""

import argparse
import asyncio
import hashlib
import json
import os
import time
from pathlib import Path

import httpx

import study as s

AUTHORIZED_OUTPUT = s.ROOT / "outputs/attempt-001/rollout"


def validate_output(output):
    if Path(output).resolve() != AUTHORIZED_OUTPUT.resolve():
        raise ValueError("only exact leaf-role-tool-contract attempt-001 rollout is authorized")


def validate_endpoint(endpoint):
    if endpoint.get("adapter") is not None or endpoint.get("base_model") != s.MODEL:
        raise ValueError("not the frozen released base")
    if endpoint.get("model_alias") != s.MODEL["alias"] or endpoint.get("max_model_len") != 8192:
        raise ValueError("endpoint model or context differs")
    if endpoint.get("vllm_version") != "0.28.0":
        raise ValueError("endpoint runtime differs")


def verify(spec):
    if s.digest({key: value for key, value in spec.items() if key != "spec_id"}) != spec["spec_id"]:
        raise ValueError("spec identity changed")
    for path, expected in spec["source_sha256"].items():
        if s.sha(path) != expected:
            raise ValueError("source changed: " + path)
    rebuilt = s.build_design(s.build_data())
    rebuilt["rendered_prompts"] = spec["design"]["rendered_prompts"]
    if rebuilt != spec["design"]:
        raise ValueError("design changed")
    for row in rebuilt["plan"]:
        body = s.make_request(rebuilt, row)
        if s.serialize(body) != s.serialize(spec["requests"][row["id"]]):
            raise ValueError("request changed: " + row["id"])
    for path, identity in spec["weight_stat_identity"].items():
        stat = Path(path).stat()
        if [stat.st_size, stat.st_mtime_ns, stat.st_ino] != identity:
            raise ValueError("previously byte-hashed shard stat changed")


def wire_hook(spec, output):
    by_hash = {value: key for key, value in spec["ordered_request_sha256"].items()}

    async def capture(request):
        if request.method != "POST" or not request.url.path.endswith("/chat/completions"):
            return
        body_hash = hashlib.sha256(request.content).hexdigest()
        request_id = by_hash[body_hash]
        if request.content != s.serialize(spec["requests"][request_id]).encode():
            raise ValueError("actual ordered HTTP body differs")
        s.write_once(output / "wire" / f"{request_id}.json", {
            "coordinate_id": request_id, "body_sha256": body_hash,
            "body_utf8": request.content.decode(), "captured_epoch": time.time(),
            "credentials_recorded": False})

    return capture


async def run(endpoint, spec, output, deadline):
    validate_output(output)
    validate_endpoint(endpoint)
    output.mkdir(parents=True, exist_ok=False)
    s.write_once(output / "SPEC.json", spec)
    s.write_once(output / "ENDPOINT.json", endpoint)
    records = []
    pending = iter(spec["design"]["plan"])
    stop = asyncio.Event()

    async def worker(client, url):
        while not stop.is_set():
            row = next(pending, None)
            if row is None:
                return
            body = s.make_request(spec["design"], row)
            record = {"coordinate": row, "request_sha256": s.digest(body),
                      "started": time.time(), "model_called": False,
                      "model_completed": False, "score": None, "usage": {},
                      "tools_executed": False}
            try:
                record["model_called"] = True
                response = await client.post(url + "/chat/completions", json=body)
                record["http_status"] = response.status_code
                record["raw_response_text"] = response.text
                record["response_headers"] = {key: response.headers[key] for key in
                                               ("x-request-id", "x-ratelimit-remaining-requests")
                                               if key in response.headers}
                response.raise_for_status()
                raw = response.json()
                record["raw_response"] = raw
                record["provider_response_id"] = raw.get("id")
                if raw.get("model") != body["model"]:
                    raise ValueError("response model differs")
                choice = raw["choices"][0]
                message = choice["message"]
                record["model_completed"] = True
                record["finish_reason"] = choice.get("finish_reason")
                record["score"] = s.score_message(message, spec["design"]["batches"]
                                                  [row["batch_id"]]["gold"],
                                                  choice.get("finish_reason"))
                record["usage"] = raw.get("usage") or {}
                expected = spec["design"]["rendered_prompts"][row["id"]]
                prompt_ids = raw.get("prompt_token_ids")
                if not isinstance(prompt_ids, list) or s.digest(prompt_ids) != expected["typed_token_ids_sha256"]:
                    raise ValueError("provider prompt IDs differ from frozen renderer")
                if len(prompt_ids) != record["usage"].get("prompt_tokens"):
                    raise ValueError("prompt usage differs from prompt ID count")
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

    started = time.time()
    reason = None
    try:
        async with asyncio.timeout(max(0.001, deadline - time.time())):
            url = f"http://{endpoint['host']}:{endpoint['port']}/v1"
            headers = {"Authorization": "Bearer " + os.environ[endpoint["api_key_env"]]}
            async with httpx.AsyncClient(headers=headers, timeout=120, trust_env=False,
                                         event_hooks={"request": [wire_hook(spec, output)]}) as client:
                version = await client.get(url.removesuffix("/v1") + "/version")
                version.raise_for_status()
                if version.json().get("version") != "0.28.0":
                    raise ValueError("wrong vLLM version")
                models = await client.get(url + "/models")
                models.raise_for_status()
                cards = models.json().get("data", [])
                if len(cards) != 1 or cards[0].get("id") != s.MODEL["alias"] or \
                        cards[0].get("root") != s.MODEL["path"] or cards[0].get("parent") is not None:
                    raise ValueError("live model differs")
                await asyncio.gather(*(worker(client, url) for _ in range(4)))
    except TimeoutError:
        reason = "collection_deadline"
    except BaseException as error:
        reason = type(error).__name__
        s.write_once(output / "ERROR.json", {"type": reason, "message": str(error)[:1200]})
    finally:
        retained = [s.read(path) for path in sorted((output / "calls").glob("*.json"))]
        s.write_once(output / "analysis.json", s.summarize(spec["design"], retained))
        seen = {record["coordinate"]["id"] for record in retained}
        s.write_once(output / "STATUS.json", {"planned": len(spec["design"]["plan"]),
            "recorded": len(retained), "model_completed": sum(r.get("model_completed", False) for r in retained),
            "stop_reason": reason or ("request_error" if stop.is_set() else None),
            "elapsed_seconds": time.time() - started,
            "unrun": [row["id"] for row in spec["design"]["plan"] if row["id"] not in seen]})
    return 0 if reason is None and not stop.is_set() and len(records) == len(spec["design"]["plan"]) else 2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--endpoint", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--deadline", type=float)
    args = parser.parse_args()
    spec = s.read(s.ROOT / "SPEC.json")
    if args.command == "verify":
        verify(spec)
        print("verified 96-call role/tool screen; no model calls")
    else:
        verify(spec)
        endpoint = s.read(args.endpoint)
        raise SystemExit(asyncio.run(run(endpoint, spec, args.output, args.deadline)))


if __name__ == "__main__":
    main()
