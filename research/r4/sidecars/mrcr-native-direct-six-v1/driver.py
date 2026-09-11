"""Frozen six-request native TrainClient direct MRCR control. No tools or generated-code execution."""

from __future__ import annotations

import argparse
import asyncio
import copy
import difflib
import hashlib
import importlib.metadata
import json
import math
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OLD = ROOT.parent / "mrcr-direct-six-v1/outputs/attempt-001"
PILOT = ROOT.parent / "mrcr-rootless-document-baseline-v2/outputs/attempt-001"
SPEC = ROOT / "SPEC.json"
DIRECT_SPEC_ID = "e5ce8d5e8e46821148b6bd1497f1ef8c72cf6708aa0adf4da71362a6e27b8932"


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def file_hash(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write_once(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def request_for_alias(original, alias):
    return {**copy.deepcopy(original), "model": alias}


def validate_binding_identity(endpoint, frozen):
    for section, keys in (("base_model", ("revision", "manifest_sha256")), ("adapter", ("model_sha256", "config_sha256"))):
        for key in keys:
            if endpoint[section][key] != frozen[section][key]:
                raise ValueError(f"endpoint does not identify original frozen {section}.{key}")
    if endpoint["host"] != "127.0.0.1" or not 0 < int(endpoint["port"]) < 65536:
        raise ValueError("only an explicitly assigned local endpoint is allowed")
    if not endpoint.get("model_alias") or not endpoint.get("api_key_env"):
        raise ValueError("endpoint alias and API-key environment name required")


def validate_token_evidence(tokens):
    prompt, completion, values = tokens["prompt_ids"], tokens["completion_ids"], tokens["completion_logprobs"]
    if not prompt or not completion or any(type(x) is not int or x < 0 for x in prompt + completion):
        raise ValueError("missing/invalid native token IDs")
    if len(completion) != len(values) or any(type(x) not in (int, float) or not math.isfinite(x) or x == -9999 for x in values):
        raise ValueError("missing/invalid native sampled-token evidence")
    return len(prompt), len(completion)


def renderer_for(base):
    from renderers import Qwen3RendererConfig, create_renderer
    from renderers.base import load_tokenizer
    return create_renderer(load_tokenizer(base), Qwen3RendererConfig(enable_thinking=True))


def make_client(endpoint):
    from verifiers.v1.clients.train import TrainClient
    from verifiers.v1.configs.client import TrainClientConfig
    return TrainClient(TrainClientConfig(
        base_url=f"http://{endpoint['host']}:{endpoint['port']}/v1",
        api_key_var=endpoint["api_key_env"], renderer={"name": "qwen3", "enable_thinking": True},
        renderer_model_name=endpoint["base_model"]["path"],
    ))


async def native_call(client, body):
    from verifiers.v1.dialects.chat import ChatDialect
    from verifiers.v1.types import SamplingConfig
    sampling = SamplingConfig(**{k: v for k, v in body.items() if k not in ("model", "messages")})
    return await client.get_response(ChatDialect(), body, sampling)


def prepare():
    old = read(OLD / "SPEC.json")
    if old["spec_id"] != DIRECT_SPEC_ID or digest({k: v for k, v in old.items() if k != "spec_id"}) != DIRECT_SPEC_ID:
        raise ValueError("frozen Chat-direct spec changed")
    for path, expected in old["source_sha256"].items():
        if file_hash(path) != expected:
            raise ValueError(f"frozen source/input changed: {path}")
    base = old["endpoint"]["base_model"]["path"]
    renderer = renderer_for(base)
    items = copy.deepcopy(old["requests"])
    for item in items:
        body = item["request"]
        assert set(body) == {"model", "messages", "temperature", "top_p", "top_k", "min_p", "max_tokens", "seed"}
        rendered = renderer.render(body["messages"], tools=None, add_generation_prompt=True)
        item["prompt_ids"] = rendered.token_ids
        item["prompt_ids_sha256"] = digest(rendered.token_ids)
        item["original_request_sha256"] = digest(body)
        tail = renderer._tokenizer.decode(rendered.token_ids[-20:])
        if not tail.endswith("<|im_start|>assistant\n"):
            raise ValueError("renderer unexpectedly adds empty thinking or other prefill")
        item["rendered_tail"] = tail
    gold = read(PILOT / "host-scoring.json")
    write_once(ROOT / "inputs/requests.json", items)
    write_once(ROOT / "inputs/gold.json", gold)
    import renderers.base
    import renderers.client
    import renderers.configs
    import renderers.qwen3
    import verifiers.v1.clients.base
    import verifiers.v1.clients.train
    import verifiers.v1.configs.client
    import verifiers.v1.dialects.chat
    import verifiers.v1.types
    paths = [Path(__file__), ROOT / "test_driver.py", ROOT / "cpu_probe.py", OLD / "SPEC.json",
             ROOT / "inputs/requests.json", ROOT / "inputs/gold.json"]
    paths += [Path(module.__file__) for module in (renderers.base, renderers.client, renderers.configs,
        renderers.qwen3, verifiers.v1.clients.base, verifiers.v1.clients.train,
        verifiers.v1.configs.client, verifiers.v1.dialects.chat, verifiers.v1.types)]
    spec = {
        "schema": "mrcr-native-direct-six-v1", "question": "Does native TrainClient change full-context direct retrieval relative to Chat direct?",
        "original_identity": {key: old["endpoint"][key] for key in ("base_model", "adapter")},
        "source_direct_spec_id": DIRECT_SPEC_ID,
        "source_sha256": {str(path): file_hash(path) for path in paths},
        "upstream_source_sha256": old["source_sha256"],
        "renderer": {"name": "qwen3", "enable_thinking": True, "empty_think_prefill": False},
        "tools": None, "additional_instructions": None, "truncate": False, "retries": 0,
        "episodes": 6, "concurrency": 4, "per_call_seconds": 120, "wall_seconds": 300,
        "sampling": {"temperature": 0, "top_p": 1, "top_k": -1, "min_p": 0, "max_tokens": 2048},
        "endpoint_binding": "Runtime descriptor required; original adapter bytes plus live advertised alias/root/parent checked. Old stopped endpoint is not proof.",
        "logprob_interpretation": "Preserve engine-returned native sampled logprobs exactly. No claim of precise probabilities, entropy, or calibrated likelihood at temperature0.",
        "usage": "Logical full prompt/completion token-ID counts. Cached and uncached counts unknown.",
        "terminal_policy": "Nonempty content, finish_reason stop, no tool calls. Length/error/invalid token capture retained with null score; no fallback or retry.",
        "scope": "Mechanistic six cached short-document replay, not fresh confirmation, pure decomposition or long-context generalization.",
        "python": sys.version,
        "packages": {name: importlib.metadata.version(name) for name in ("verifiers", "renderers", "transformers", "openai", "httpx")},
    }
    spec["spec_id"] = digest(spec)
    write_once(SPEC, spec)
    for path in (SPEC, ROOT / "inputs/requests.json", ROOT / "inputs/gold.json"):
        path.chmod(0o444)
    return {"spec_id": spec["spec_id"], "prompt_lengths": [len(x["prompt_ids"]) for x in items], "gpu_launched": False}


def verify_spec():
    spec = read(SPEC)
    if digest({k: v for k, v in spec.items() if k != "spec_id"}) != spec["spec_id"]:
        raise ValueError("spec changed")
    for path, expected in {**spec["source_sha256"], **spec["upstream_source_sha256"]}.items():
        if file_hash(path) != expected:
            raise ValueError(f"pinned source/input changed: {path}")
    return spec


async def run(endpoint_path, output):
    spec = verify_spec()
    endpoint = read(endpoint_path)
    validate_binding_identity(endpoint, spec["original_identity"])
    for path, expected in {
        Path(endpoint["adapter"]["path"]) / "adapter_model.safetensors": endpoint["adapter"]["model_sha256"],
        Path(endpoint["adapter"]["path"]) / "adapter_config.json": endpoint["adapter"]["config_sha256"],
        Path(endpoint["base_model"]["path"]) / "local-research-manifest.json": endpoint["base_model"]["manifest_sha256"],
    }.items():
        if file_hash(path) != expected:
            raise ValueError("actual descriptor weight identity changed")
    if not os.environ.get(endpoint["api_key_env"]):
        raise ValueError("assigned endpoint API key environment variable is unset")
    output.mkdir(parents=True, exist_ok=False)
    items = read(ROOT / "inputs/requests.json")
    by_seed = {x["request"]["seed"]: x for x in items}
    gold = read(ROOT / "inputs/gold.json")
    wire_requests, wire_responses = {}, {}
    rows = {}
    started = time.time()
    client = make_client(endpoint)

    async def capture_request(request):
        if request.url.path != "/inference/v1/generate":
            return
        body = json.loads(request.content)
        seed = body["sampling_params"]["seed"]
        if seed in wire_requests or seed not in by_seed:
            raise ValueError("unexpected or repeated native request")
        if body["token_ids"] != by_seed[seed]["prompt_ids"] or body["model"] != endpoint["model_alias"]:
            raise ValueError("actual native prompt/alias differs from frozen request")
        for key, value in spec["sampling"].items():
            if body["sampling_params"][key] != value:
                raise ValueError(f"actual native sampling changed: {key}")
        wire_requests[seed] = {"url": str(request.url), "body": body}

    async def capture_response(response):
        if response.request.url.path != "/inference/v1/generate":
            return
        seed = json.loads(response.request.content)["sampling_params"]["seed"]
        await response.aread()
        wire_responses[seed] = {"http_status": response.status_code, "body": response.text}

    client.client._client.event_hooks["request"].append(capture_request)
    client.client._client.event_hooks["response"].append(capture_response)
    try:
        advertised = await asyncio.wait_for(client.client.get("/models", cast_to=dict), timeout=15)
        cards = {card["id"]: card for card in advertised["data"]}
        card = cards.get(endpoint["model_alias"], {})
        if Path(card.get("root", "")).resolve() != Path(endpoint["adapter"]["path"]).resolve() or card.get("parent") != endpoint["base_model"]["path"]:
            raise ValueError("live API does not bind original alias to verified adapter/base")
        write_once(output / "BINDING.json", {"endpoint_path": str(endpoint_path), "endpoint_sha256": file_hash(endpoint_path), "endpoint": endpoint, "advertised": advertised,
                   "verification_scope": "Adapter disk bytes + base manifest + live alias/root; not live-memory tensor attestation."})
        semaphore = asyncio.Semaphore(spec["concurrency"])

        async def one(item):
            coordinate = item["coordinate"]
            seed = item["request"]["seed"]
            async with semaphore:
                begin = time.time()
                body = request_for_alias(item["request"], endpoint["model_alias"])
                row = {"coordinate": coordinate, "spec_id": spec["spec_id"], "original_request_sha256": item["original_request_sha256"], "actual_request": body, "actual_request_sha256": digest(body), "complete": False, "score": None}
                try:
                    response = await asyncio.wait_for(native_call(client, body), timeout=spec["per_call_seconds"])
                    payload = response.model_dump(mode="json")
                    row["native_response"] = payload
                    row["serialized_completion"] = response.raw
                    prompt_n, output_n = validate_token_evidence(payload["tokens"])
                    if payload["tokens"]["prompt_ids"] != item["prompt_ids"]:
                        raise ValueError("returned prompt IDs differ from complete frozen prompt")
                    prediction = response.message.content
                    complete = response.finish_reason == "stop" and not response.message.tool_calls and isinstance(prediction, str) and bool(prediction.strip())
                    row.update(complete=complete, prediction=prediction, finish_reason=response.finish_reason,
                               logical_input_tokens=prompt_n, completion_tokens=output_n,
                               cached_input_tokens=None, uncached_input_tokens=None, error=None)
                    if complete:
                        target = gold[coordinate["row_id"]].strip()
                        pos = prediction.strip().rfind(target[:12])
                        value = difflib.SequenceMatcher(a=target[12:].strip(), b=prediction.strip()[pos + 12:].strip()).ratio() if pos >= 0 else 0.0
                        row["score"] = {"valid": True, "exact": prediction.strip() == target, "official_score": value}
                except (Exception, asyncio.CancelledError) as error:
                    row["error"] = {"type": type(error).__name__, "message": str(error)}
                finally:
                    row.update(native_wire_request=wire_requests.get(seed), native_wire_response=wire_responses.get(seed), wall_seconds=time.time() - begin)
                    write_once(output / f"{coordinate['row_id']}.json", row)
                    rows[coordinate["row_id"]] = row
                    print(json.dumps({"recorded": len(rows), "complete": row["complete"], "score": row["score"], "error": row.get("error")}), flush=True)

        jobs = [asyncio.create_task(one(item)) for item in items]
        try:
            await asyncio.wait_for(asyncio.gather(*jobs), timeout=spec["wall_seconds"])
        except TimeoutError:
            await asyncio.gather(*jobs, return_exceptions=True)
        for item in items:
            key = item["coordinate"]["row_id"]
            if key not in rows:
                row = {"coordinate": item["coordinate"], "spec_id": spec["spec_id"], "complete": False, "score": None, "error": {"type": "BatchDeadlineBeforeDispatch", "message": "not dispatched before fixed batch deadline"}}
                write_once(output / f"{key}.json", row)
                rows[key] = row
        write_once(output / "STATUS.json", {"planned": 6, "recorded": len(rows), "complete": sum(r["complete"] for r in rows.values()), "errors": sum(r.get("error") is not None for r in rows.values()), "wall_seconds": time.time() - started})
    except BaseException as error:
        write_once(output / "FAILURE.json", {"type": type(error).__name__, "message": str(error)})
        raise
    finally:
        await client.close()


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("prepare")
    sub.add_parser("verify")
    run_parser = sub.add_parser("run")
    run_parser.add_argument("--endpoint", type=Path, required=True)
    run_parser.add_argument("--output", type=Path, default=ROOT / "outputs/attempt-001")
    args = parser.parse_args()
    if args.command == "prepare":
        print(json.dumps(prepare(), indent=2))
    elif args.command == "verify":
        print(json.dumps({"verified_spec_id": verify_spec()["spec_id"]}))
    else:
        asyncio.run(run(args.endpoint.resolve(), args.output.resolve()))


if __name__ == "__main__":
    main()
