"""CPU prepare/bind and parent-launched native leaf collection; never owns a service."""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib.metadata
import json
import os
import subprocess
import sys
import time
from copy import deepcopy
from pathlib import Path

import httpx
import study as s

ROOT = s.ROOT
INDEXED = s.SIDE / "leaf-indexed-sft-v1"
INDEXED_ID = "204bc845987825514afe0f5a395917d933871e78b097de39db6736b72b5d23ca"
INDEXED_MANIFEST_SHA = "792446b86c9247bb5b933eade2a35bc628d35dd7df524085ab85a321f580e811"
BASE = {"path": str(s.anchor.corr.BASE), "revision": "cdbee75f17c01a7cc42f958dc650907174af0554",
        "manifest_sha256": "19619b44b0bd30bf5debe0960e6dfd6acc5be8287c581727456aa5d17699c18f"}


def typed_prompt_ids(tokenizer, body):
    from vllm.entrypoints.openai.chat_completion.protocol import ChatCompletionRequest
    parsed = ChatCompletionRequest.model_validate(deepcopy(body))
    return tokenizer.apply_chat_template(body["messages"], tools=[t.model_dump() for t in parsed.tools],
        add_generation_prompt=True, tokenize=True, return_dict=False)


def wire_hook(spec, output):
    by_hash = {h: key for key, h in spec["request_sha256"].items()}
    if len(by_hash) != len(spec["request_sha256"]):
        raise ValueError("duplicate request identity")

    async def capture(request):
        if request.method != "POST" or not request.url.path.endswith("/chat/completions"):
            return
        key = by_hash[s.digest(json.loads(request.content))]
        if request.content != s.serialize(spec["requests"][key]).encode():
            raise ValueError("actual serialized field ordering differs from frozen request")
        s.write_once(output / "wire" / (key + ".json"), {"coordinate_id": key, "route": request.url.path,
            "body_utf8": request.content.decode(), "body_sha256": hashlib.sha256(request.content).hexdigest(),
            "credentials_recorded": False})
    return capture


def qualify(design, requests):
    import xgrammar as xgr
    from transformers import AutoTokenizer
    hf = AutoTokenizer.from_pretrained(BASE["path"], local_files_only=True, trust_remote_code=False)
    compiler = xgr.GrammarCompiler(xgr.TokenizerInfo.from_huggingface(hf), max_threads=1)
    prompts, schemas = {}, set()
    grouped = {}
    for row in design["plan"]:
        body = requests[row["id"]]
        original = s.serialize(body)
        ids = typed_prompt_ids(hf, body)
        if not ids or any(type(x) is not int for x in ids) or len(ids) + 3072 > 8192:
            raise ValueError("invalid typed prompt or prompt+cap exceeds8192")
        if "structured_outputs" in body:
            schema = s.serialize(body["structured_outputs"]["json"])
            if schema not in schemas:
                compiler.compile_json_schema(schema)
                schemas.add(schema)
        if original != s.serialize(body):
            raise ValueError("typed rendering changed the frozen request")
        prompts[row["id"]] = {"tokens": len(ids), "typed_token_ids_sha256": s.digest(ids),
            "physical_source": "vLLM typed tool.model_dump then pinned native HF template"}
        key = (row["context_index"], row["arm"], row["seed"])
        if key in grouped and grouped[key] != s.digest(ids):
            raise ValueError("weight/grammar pair does not have identical physical input")
        grouped[key] = s.digest(ids)
    return {"requests": len(requests), "schemas_compiled": len(schemas), "rendered_prompts": prompts,
        "weight_grammar_physical_pair_groups": len(grouped), "max_prompt_tokens": max(x["tokens"] for x in prompts.values()),
        "versions": {x: importlib.metadata.version(x) for x in ["vllm", "transformers", "httpx", "xgrammar", "pyarrow"]},
        "gpu_calls": 0, "model_calls": 0}


def check_final_identity(result, selection, state, checkpoint):
    if (result.get("identity") != INDEXED_ID or result.get("optimizer_steps") != 204
            or result.get("selected") != selection.get("selected") or result["selected"].get("epoch") != 2
            or selection.get("identity") != INDEXED_ID or selection.get("post_training_test_inspected") is not False
            or Path(result["selected"]["checkpoint"]) != checkpoint or checkpoint.name != "checkpoint-0204"
            or state.get("identity") != INDEXED_ID or state.get("epoch") != 2
            or state.get("step") != 204 or state.get("cursor") != 0):
        raise ValueError("requires authenticated fixed final epoch2/step204; no outcome-selected substitute")


def authenticate_weights():
    manifest_path = INDEXED / "prepared/MANIFEST.json"
    if s.file_hash(manifest_path) != INDEXED_MANIFEST_SHA:
        raise ValueError("prospective indexed manifest changed")
    manifest = s.read(manifest_path)
    if manifest["identity"] != INDEXED_ID or s.digest({k: v for k, v in manifest.items() if k != "identity"}) != INDEXED_ID:
        raise ValueError("indexed curriculum identity changed")
    attempt = INDEXED / "outputs/attempt-001"
    result, selection = s.read(attempt / "RESULT.json"), s.read(attempt / "SELECTION.json")
    checkpoint = Path(result["selected"]["checkpoint"])
    if checkpoint.parent != attempt:
        raise ValueError("indexed checkpoint outside frozen attempt")
    state_path = checkpoint / "state.json"
    state = s.read(state_path)
    check_final_identity(result, selection, state, checkpoint)
    required = {"adapter_model.safetensors", "adapter_config.json", "optimizer.pt", "rng_state.pt"}
    if not required <= state["files_sha256"].keys() or any(Path(x).name != x for x in state["files_sha256"]):
        raise ValueError("checkpoint member closure is incomplete or nonlocal")
    sources = {str(manifest_path): INDEXED_MANIFEST_SHA,
        str(INDEXED / "prepared/RECIPE.json"): manifest["recipe_sha256"],
        str(INDEXED / "prepared/data.json"): manifest["data_sha256"],
        **{str(checkpoint / n): h for n, h in state["files_sha256"].items()},
        **s.read(INDEXED / "prepared/RECIPE.json")["source_hashes"]}
    for p in [attempt / "RESULT.json", attempt / "SELECTION.json", state_path]:
        sources[str(p)] = s.file_hash(p)
    old = {"path": str(s.anchor.corr.ADAPTER), "model_sha256": s.anchor.corr.SELECTED_SHA,
           "config_sha256": s.anchor.corr.CONFIG_SHA}
    s.anchor.sst.authenticate_weight("old_sft", {"adapter": old, "base_model": BASE}, sources)
    s.anchor.sst.verify_hashes(sources)
    return {"indexed_prepared_identity": INDEXED_ID, "fixed_final_epoch": 2, "fixed_final_step": 204,
        "models": {"old_sft": old, "indexed_final": {"path": str(checkpoint),
            "model_sha256": state["files_sha256"]["adapter_model.safetensors"],
            "config_sha256": state["files_sha256"]["adapter_config.json"]}},
        "base_model": BASE, "source_sha256": sources,
        "outcome_metric_used_to_select_weights": False, "gpu_calls": 0}


def validate_descriptor(weight, endpoint, weights):
    if endpoint.get("adapter") != weights["models"][weight] or endpoint.get("base_model") != BASE:
        raise ValueError("actual endpoint does not bind the required semantic weight")
    s.anchor.corr.leaf.verify_weights(endpoint)
    if (not endpoint.get("inference_only") or endpoint["host"] != "127.0.0.1"
            or endpoint.get("vllm", {}).get("version") != "0.28.0"
            or endpoint["vllm"].get("max_model_len", 0) < 8192 or not isinstance(endpoint["port"], int)):
        raise ValueError("requires qualified native local inference endpoint")


def validate_live_models(endpoints, response):
    cards = {row["id"]: row for row in response["data"]}
    for endpoint in endpoints.values():
        card = cards.get(endpoint["model_alias"], {})
        if card.get("root") != endpoint["adapter"]["path"] or card.get("parent") != BASE["path"]:
            raise ValueError("live alias path/base differs from frozen weight")
    if cards.get(BASE["path"], {}).get("max_model_len", 0) < 8192:
        raise ValueError("live model length insufficient")


def verify(spec):
    if s.digest({k: v for k, v in spec.items() if k != "spec_id"}) != spec["spec_id"]:
        raise ValueError("outer spec identity changed")
    s.anchor.sst.verify_hashes(spec["source_sha256"])
    expected = s.build_design(s.read(ROOT / "DATA.json"))
    expected["rendered_prompts"] = s.read(ROOT / "CPU_QUALIFICATION.json")["rendered_prompts"]
    if "endpoint_binding" in spec:
        binding = spec["endpoint_binding"]
        weights = s.read(ROOT / "WEIGHTS.json")
        if binding["weights_sha256"] != s.file_hash(ROOT / "WEIGHTS.json") or weights != authenticate_weights():
            raise ValueError("fixed final weight closure changed")
        for weight, item in binding["endpoints"].items():
            if s.file_hash(item["path"]) != item["sha256"] or s.read(item["path"]) != item["descriptor"]:
                raise ValueError("actual endpoint descriptor changed")
            validate_descriptor(weight, item["descriptor"], weights)
            expected["model_aliases"][weight] = item["descriptor"]["model_alias"]
    if expected != spec["design"] or len(expected["plan"]) != 160:
        raise ValueError("frozen data/coordinate design changed")
    for row in expected["plan"]:
        body = s.make_request(expected, row)
        if s.serialize(body) != s.serialize(spec["requests"][row["id"]]) or s.digest(body) != spec["request_sha256"][row["id"]]:
            raise ValueError("frozen request or serialization changed")


def prepare():
    if (ROOT / "SPEC.json").exists() or (ROOT / "PREPARED.json").exists():
        raise ValueError("already frozen; never overwrite prepared inputs")
    seeds = subprocess.run(["rg", "-n", r"\b(981263401|981263402)\b", str(s.SIDE),
        "-g", "*SPEC*.json", "-g", "*READY*.json", "-g", "*RECIPE*.json", "-g", "*PLAN*.json",
        "-g", "!**/outputs/**", "-g", "!**/exports/**", "-g", "!**/leaf-indexed-grammar-transfer-v1/**"],
        capture_output=True, text=True, timeout=30)
    if seeds.returncode != 1 or seeds.stdout:
        raise ValueError("seed namespace collision or collision audit failed")
    s.write_once(ROOT / "SEED_AUDIT.json", {"args": seeds.args, "exit_code": seeds.returncode,
        "matches": seeds.stdout, "sampling_seeds": s.SEEDS, "scope": "Existing non-output ready/spec/recipe/plan JSON; not all historical logs"})
    data = s.load_data()
    s.write_once(ROOT / "DATA.json", data)
    design = s.build_design(data)
    requests = {row["id"]: s.make_request(design, row) for row in design["plan"]}
    qualified = qualify(design, requests)
    design["rendered_prompts"] = qualified["rendered_prompts"]
    s.write_once(ROOT / "CPU_QUALIFICATION.json", qualified)
    s.write_once(ROOT / "REQUESTS.json", requests)
    tests = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(ROOT / "test_study.py")],
        capture_output=True, text=True, timeout=90, env={**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"})
    s.write_once(ROOT / "CPU_TESTS.json", {"returncode": tests.returncode, "stdout": tests.stdout,
        "stderr": tests.stderr, "gpu_calls": 0, "fake_http_calls": 8, "prior_red": "Five tests failed because new study/driver did not exist"})
    if tests.returncode:
        raise ValueError("focused CPU checks failed: " + tests.stdout[-2500:])
    upstream = s.read(s.ANCHOR / "SPEC.json")
    sources = dict(upstream["source_sha256"])
    sources.update(s.INPUT_HASHES)
    paths = [*ROOT.glob("*.py"), *ROOT.glob("*.md"), *ROOT.glob("*.json"),
             s.ANCHOR / "study.py", s.ANCHOR / "driver.py", s.ANCHOR / "SPEC.json",
             INDEXED / "prepared/MANIFEST.json", INDEXED / "prepared/RECIPE.json"]
    sources.update({str(p): s.file_hash(p) for p in paths})
    spec = {"schema": ROOT.name, "design": design, "requests": requests,
        "request_sha256": {k: s.digest(v) for k, v in requests.items()}, "cpu_qualification": qualified,
        "source_sha256": sources, "weight_rule": {"old": s.anchor.corr.SELECTED_SHA, "indexed_prepared_identity": INDEXED_ID,
            "checkpoint": "fixed final epoch2/step204; requires RESULT/SELECTION/state", "outcome_selection": False},
        "budget": {"calls": 160, "collection_seconds": 1800, "overall_seconds": 2700, "workers": 4, "output_cap": 3072}}
    spec["spec_id"] = s.digest(spec)
    s.write_once(ROOT / "SPEC.json", spec)
    verify(s.read(ROOT / "SPEC.json"))
    s.write_once(ROOT / "PREPARED.json", {"status": "CPU_FROZEN_WAITING_FIXED_FINAL_AUTHENTICATION",
        "driver": str(Path(__file__).resolve()), "driver_sha256": s.file_hash(__file__),
        "spec": str(ROOT / "SPEC.json"), "spec_id": spec["spec_id"], "spec_sha256": s.file_hash(ROOT / "SPEC.json"),
        "calls": 160, "schemas_compiled": qualified["schemas_compiled"], "max_prompt_tokens": qualified["max_prompt_tokens"],
        "gpu_calls": 0, "fresh_sst_groups": 256})
    print(s.serialize(s.read(ROOT / "PREPARED.json")), flush=True)


def accept_weights():
    verify(s.read(ROOT / "SPEC.json"))
    weights = authenticate_weights()
    s.write_once(ROOT / "WEIGHTS.json", weights)
    s.write_once(ROOT / "READY.json", {"status": "READY_REQUIRES_ACTUAL_DUAL_ENDPOINT_BINDING",
        "driver": str(Path(__file__).resolve()), "driver_sha256": s.file_hash(__file__),
        "spec_path": str(ROOT / "SPEC.json"), "spec_sha256": s.file_hash(ROOT / "SPEC.json"),
        "weights_path": str(ROOT / "WEIGHTS.json"), "weights_sha256": s.file_hash(ROOT / "WEIGHTS.json"),
        "models": weights["models"], "calls": 160, "collection_seconds": 1800, "overall_seconds": 2700,
        "source_hash_verified": True, "gpu_calls": 0, "service_owner": "parent"})
    print(s.serialize(s.read(ROOT / "READY.json")), flush=True)


def bind(old_path, indexed_path, destination):
    if not (ROOT / "READY.json").exists():
        raise ValueError("fixed-final acceptance required before endpoint binding")
    spec = s.read(ROOT / "SPEC.json")
    verify(spec)
    weights = s.read(ROOT / "WEIGHTS.json")
    endpoints = {w: {"path": str(p), "sha256": s.file_hash(p), "descriptor": s.read(p)}
                 for w, p in [("old_sft", old_path), ("indexed_final", indexed_path)]}
    a, b = [x["descriptor"] for x in endpoints.values()]
    if any(a[k] != b[k] for k in ["host", "port", "api_key_env", "base_model", "vllm", "serving_adapter_dtype"]):
        raise ValueError("requires two truthful aliases on one unchanged qualified service")
    if a["model_alias"] == b["model_alias"]:
        raise ValueError("two distinct semantic weight aliases required")
    for weight, item in endpoints.items():
        validate_descriptor(weight, item["descriptor"], weights)
        spec["design"]["model_aliases"][weight] = item["descriptor"]["model_alias"]
    spec["requests"] = {r["id"]: s.make_request(spec["design"], r) for r in spec["design"]["plan"]}
    spec["request_sha256"] = {k: s.digest(v) for k, v in spec["requests"].items()}
    spec["endpoint_binding"] = {"endpoints": endpoints, "weights_sha256": s.file_hash(ROOT / "WEIGHTS.json"), "contacted_at_binding": False}
    spec.pop("spec_id")
    spec["spec_id"] = s.digest(spec)
    verify(spec)
    s.write_once(destination, spec)
    print(s.serialize({"bound": str(destination), "sha256": s.file_hash(destination), "gpu_calls": 0}), flush=True)


def collection_budget(launch, now):
    remaining = launch + 2700 - now
    if remaining <= 0:
        raise TimeoutError("overall deadline expired; no new dispatch")
    return min(1800, remaining)


async def run(spec_path, output, overall_start_epoch=None):
    entry = time.time()
    launch = entry if overall_start_epoch is None else overall_start_epoch
    if launch > entry + 1:
        raise ValueError("overall launch epoch cannot be in the future")
    overall_deadline = launch + 2700
    spec = s.read(spec_path)
    verify(spec)
    endpoints = {w: item["descriptor"] for w, item in spec["endpoint_binding"]["endpoints"].items()}
    if output.parent != ROOT / "outputs":
        raise ValueError("owned sidecar output directory required")
    output.mkdir(parents=True, exist_ok=False)
    s.write_once(output / "SPEC.json", spec)
    s.write_once(output / "ATTEMPT.json", {"entered_epoch": entry, "overall_started_epoch": launch,
        "overall_deadline_epoch": overall_deadline, "parent_startup_included": overall_start_epoch is not None,
        "source_spec_sha256": s.file_hash(spec_path), "weights_sha256": s.file_hash(ROOT / "WEIGHTS.json"),
        "service_owned_by_parent": True, "gpu_process_owned": False})
    endpoint = endpoints["old_sft"]
    url = f"http://{endpoint['host']}:{endpoint['port']}/v1"
    reason = None
    collection_started = None
    try:
        collection_budget(launch, time.time())
        async with asyncio.timeout(max(.001, overall_deadline - time.time())):
            async with httpx.AsyncClient(headers={"Authorization": "Bearer " + os.environ[endpoint["api_key_env"]]},
                    trust_env=False, timeout=120, event_hooks={"request": [wire_hook(spec, output)]}) as client:
                response = await client.get(url.removesuffix("/v1") + "/version")
                response.raise_for_status()
                s.write_once(output / "VERSION_PREFLIGHT.json", response.json())
                if response.json().get("version") != "0.28.0":
                    raise ValueError("live vLLM version is unqualified")
                response = await client.get(url + "/models")
                response.raise_for_status()
                validate_live_models(endpoints, response.json())
                s.write_once(output / "MODELS_PREFLIGHT.json", response.json())
                collection_started = time.time()
                deadline = time.monotonic() + collection_budget(launch, collection_started)
                _, reason = await s.collect_calls(client, url, spec, output, deadline)
    except TimeoutError:
        reason = "overall_wall_time_cap"
    except Exception as error:
        reason = "preflight_or_runtime_error:" + type(error).__name__
        s.write_once(output / "ERROR.json", {"type": type(error).__name__, "message": str(error)[:1200]})
    finally:
        records = [s.read(p) for p in sorted((output / "calls").glob("*.json"))]
        analysis = s.summarize(spec["design"], records)
        s.write_once(output / "analysis.json", analysis)
        physical = [p for c in analysis["coordinates"] for p in c["physical_prompts"]]
        if any(p["typed_template_equal"] is not True or p["reported_usage_length_equal"] is not True for p in physical):
            reason = reason or "physical_prompt_identity_unverified"
        seen = {r["coordinate"]["id"] for r in records}
        s.write_once(output / "STATUS.json", {"planned": 160, "recorded": len(records), "stop_reason": reason,
            "actual_typed_prompt_matches": sum(p["typed_template_equal"] is True for p in physical),
            "collection_seconds": time.time() - collection_started if collection_started is not None else None,
            "driver_wall_seconds": time.time() - entry, "overall_elapsed_seconds": time.time() - launch,
            "unrun": [r["id"] for r in spec["design"]["plan"] if r["id"] not in seen]})
    return 0 if reason is None and len(records) == 160 else 2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["prepare", "verify", "accept-weights", "bind", "run"])
    parser.add_argument("--spec-path", type=Path, default=ROOT / "SPEC.json")
    parser.add_argument("--old-endpoint", type=Path)
    parser.add_argument("--indexed-endpoint", type=Path)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs/attempt-001")
    parser.add_argument("--overall-start-epoch", type=float)
    args = parser.parse_args()
    if args.command == "prepare":
        prepare()
    elif args.command == "verify":
        verify(s.read(args.spec_path))
        print("verified", flush=True)
    elif args.command == "accept-weights":
        accept_weights()
    elif args.command == "bind":
        if not args.old_endpoint or not args.indexed_endpoint or args.spec_path == ROOT / "SPEC.json":
            parser.error("both actual endpoint descriptors and a NEW bound spec path required")
        bind(args.old_endpoint.resolve(), args.indexed_endpoint.resolve(), args.spec_path.resolve())
    else:
        raise SystemExit(asyncio.run(run(args.spec_path.resolve(), args.output_dir.resolve(), args.overall_start_epoch)))


if __name__ == "__main__":
    main()
