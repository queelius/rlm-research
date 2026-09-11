"""CPU freeze and one-shot128 native collection using qualified private helpers."""
from __future__ import annotations

import argparse
import asyncio
import importlib.util
import os
import subprocess
import sys
import time
from pathlib import Path

import httpx
import study as s

ROOT = s.ROOT
loader = importlib.util.spec_from_file_location("padding_private_grammar_http", s.GRAMMAR / "driver.py")
qualified_http = importlib.util.module_from_spec(loader)
loader.loader.exec_module(qualified_http)
BASE = qualified_http.BASE
typed_prompt_ids = qualified_http.typed_prompt_ids
wire_hook = qualified_http.wire_hook


def weights():
    old = {"path": str(s.anchor.corr.ADAPTER), "model_sha256": s.anchor.corr.SELECTED_SHA,
           "config_sha256": s.anchor.corr.CONFIG_SHA}
    sources = {}
    s.anchor.sst.authenticate_weight("old_sft", {"adapter": old, "base_model": BASE}, sources)
    return {"models": {"old_sft": old}, "base_model": BASE, "source_sha256": sources,
            "selection": "Existing validation-selected c32de old child only; no outcome-based weight choice"}


def qualify(design, requests):
    from transformers import AutoTokenizer
    result = qualified_http.qualify(design, requests)
    hf = AutoTokenizer.from_pretrained(BASE["path"], local_files_only=True, trust_remote_code=False)
    records = design["contexts"][0]["records"]
    tags = ["q0000"] + [r["id"] for r in records]
    result["tag_token_audit"] = [{"tag": tag, "tokens": hf.encode(tag, add_special_tokens=False),
        "length": len(hf.encode(tag, add_special_tokens=False))} for tag in tags]
    synthetic = []
    for dataset, labels in design["task_labels"].items():
        for label in labels:
            for arm in s.ARMS:
                value = s.synthetic_output(records, arm, label)
                for spacing, text in [("compact", s.serialize(value)), ("standard", __import__("json").dumps(value))]:
                    ids = hf.encode(text, add_special_tokens=False)
                    synthetic.append({"dataset": dataset, "label": label, "arm": arm,
                        "serialization": spacing, "tokens": len(ids), "token_ids_sha256": s.digest(ids)})
    result["synthetic_output_audit"] = synthetic
    result["tag_output_length_differences"] = [{"dataset": dataset, "label": label, "serialization": spacing,
        "meaningful_minus_placeholder": next(x["tokens"] for x in synthetic if (x["dataset"], x["label"], x["arm"], x["serialization"]) == (dataset, label, "meaningful_tag", spacing)) - next(x["tokens"] for x in synthetic if (x["dataset"], x["label"], x["arm"], x["serialization"]) == (dataset, label, "placeholder_tag", spacing))}
        for dataset, labels in design["task_labels"].items() for label in labels for spacing in ["compact", "standard"]]
    result["remaining_confound"] = "Prompt instructions differ truthfully; output labels, serialization and free generation can differ. Synthetic equal lengths are not equal actual compute or perfectly neutral padding."
    return result


def verify(spec):
    if s.digest({k: v for k, v in spec.items() if k != "spec_id"}) != spec["spec_id"]:
        raise ValueError("spec identity changed")
    s.anchor.sst.verify_hashes(spec["source_sha256"])
    expected = s.build_design(s.read(ROOT / "DATA.json"))
    expected["rendered_prompts"] = s.read(ROOT / "CPU_QUALIFICATION.json")["rendered_prompts"]
    if expected != spec["design"] or len(expected["plan"]) != 128:
        raise ValueError("frozen design changed")
    for row in expected["plan"]:
        body = s.make_request(expected, row)
        if s.serialize(body) != s.serialize(spec["requests"][row["id"]]) or s.digest(body) != spec["request_sha256"][row["id"]]:
            raise ValueError("frozen request changed")


def prepare():
    if any((ROOT / name).exists() for name in ["SPEC.json", "READY.json", "DATA.json"]):
        raise ValueError("inputs already frozen; no overwrite or retry")
    audit = subprocess.run(["rg", "-n", r"\b(981264101|981264102)\b", str(s.SIDE),
        "-g", "*SPEC*.json", "-g", "*READY*.json", "-g", "*RECIPE*.json", "-g", "*PLAN*.json",
        "-g", "!**/outputs/**", "-g", "!**/leaf-anchor-padding-control-v1/**"], capture_output=True, text=True, timeout=30)
    if audit.returncode != 1 or audit.stdout:
        raise ValueError("seed collision or audit failure")
    tests = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
        str(ROOT / "test_study.py"), str(ROOT / "test_owned.py")], capture_output=True, text=True,
        timeout=90, env={**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"})
    if tests.returncode:
        raise ValueError("focused tests failed: " + tests.stdout[-4000:])
    data = s.load_data()
    design = s.build_design(data)
    requests = {r["id"]: s.make_request(design, r) for r in design["plan"]}
    qualification = qualify(design, requests)
    design["rendered_prompts"] = qualification["rendered_prompts"]
    weight = weights()
    s.write_once(ROOT / "DATA.json", data)
    s.write_once(ROOT / "REQUESTS.json", requests)
    s.write_once(ROOT / "CPU_QUALIFICATION.json", qualification)
    s.write_once(ROOT / "WEIGHTS.json", weight)
    s.write_once(ROOT / "SEED_AUDIT.json", {"argv": audit.args, "exit_code": audit.returncode, "stdout": audit.stdout,
        "scope": "Non-output SPEC/READY/RECIPE/PLAN JSON; not all historical logs"})
    s.write_once(ROOT / "CPU_TESTS.json", {"returncode": tests.returncode, "stdout": tests.stdout, "stderr": tests.stderr,
        "test_first_red": "Six focused tests failed because study.py was absent; owned tests failed because owned.py was absent",
        "gpu_calls": 0, "model_calls": 0, "fake_http_calls": 8})
    sources = dict(s.read(s.grammar.ANCHOR / "SPEC.json")["source_sha256"])
    sources.update({str(k): v for k, v in s.PINS.items()})
    sources.update(weight["source_sha256"])
    paths = [*ROOT.glob("*.py"), *ROOT.glob("*.md"), *ROOT.glob("*.json")]
    sources.update({str(p): s.file_hash(p) for p in paths})
    spec = {"schema": ROOT.name, "design": design, "requests": requests,
        "request_sha256": {k: s.digest(v) for k, v in requests.items()}, "source_sha256": sources,
        "weight": weight, "budget": {"calls": 128, "collection_seconds": 900,
            "owned_overall_seconds": 1800, "workers": 4, "call_timeout_seconds": 120,
            "output_cap": 3072, "context_window": 8192, "retries": 0},
        "frozen_before_outcomes": True, "checkpoint_policy": "None; evaluation only, persist each completed/failed call"}
    spec["spec_id"] = s.digest(spec)
    s.write_once(ROOT / "SPEC.json", spec)
    verify(spec)
    import owned
    suite = owned.load_suite()
    closure = {str(p): expected for p, expected in owned.PINNED.items()}
    closure.update({str(ROOT / n): s.file_hash(ROOT / n) for n in ["study.py", "driver.py", "owned.py", "SPEC.json", "WEIGHTS.json"]})
    s.write_once(ROOT / "READY.json", {"status": "CPU_READY_128_FROZEN_SINGLE_OLD_ADAPTER_OWNED_LIFECYCLE_IMPORTED_NOT_LAUNCHED",
        "spec_path": str(ROOT / "SPEC.json"), "spec_sha256": s.file_hash(ROOT / "SPEC.json"), "spec_id": spec["spec_id"],
        "driver": str(ROOT / "driver.py"), "driver_sha256": s.file_hash(ROOT / "driver.py"),
        "owned": str(ROOT / "owned.py"), "owned_sha256": s.file_hash(ROOT / "owned.py"),
        "source_sha256": closure, "budget": spec["budget"], "schemas_compiled": qualification["schemas_compiled"],
        "max_prompt_tokens": qualification["max_prompt_tokens"], "gpu_calls": 0, "model_calls": 0,
        "service_contacted": False, "lifecycle_manifest_verified": True,
        "launch_requirement": "Main assigns exclusively reserved idle GPU and integrates exact owned argv; actual native endpoint checked at run"})
    print(s.serialize(s.read(ROOT / "READY.json")), flush=True)


async def run(endpoint_path, output, overall_start_epoch):
    started = time.time()
    launch = started if overall_start_epoch is None else overall_start_epoch
    if launch > started + 1:
        raise ValueError("future launch epoch")
    spec = s.read(ROOT / "SPEC.json")
    verify(spec)
    endpoint = s.read(endpoint_path)
    qualified_http.validate_descriptor("old_sft", endpoint, spec["weight"])
    if endpoint["model_alias"] != s.ALIAS:
        raise ValueError("endpoint alias differs from all128 frozen requests")
    if output.parent != ROOT / "outputs":
        raise ValueError("output must be direct child of this namespace outputs")
    output.mkdir(parents=True, exist_ok=False)
    s.write_once(output / "SPEC.json", spec)
    s.write_once(output / "ATTEMPT.json", {"entered_epoch": started, "overall_start_epoch": launch,
        "overall_deadline_epoch": launch + 1800, "endpoint_path": str(endpoint_path),
        "endpoint_sha256": s.file_hash(endpoint_path), "endpoint": endpoint,
        "spec_sha256": s.file_hash(ROOT / "SPEC.json"), "service_owner": "owned wrapper"})
    reason, collection_started = None, None
    try:
        async with asyncio.timeout(max(.001, launch + 1680 - time.time())):
            url = f"http://{endpoint['host']}:{endpoint['port']}/v1"
            async with httpx.AsyncClient(headers={"Authorization": "Bearer " + os.environ[endpoint["api_key_env"]]},
                    trust_env=False, timeout=120, event_hooks={"request": [wire_hook(spec, output)]}) as client:
                response = await client.get(url.removesuffix("/v1") + "/version")
                response.raise_for_status()
                s.write_once(output / "VERSION_PREFLIGHT.json", response.json())
                if response.json().get("version") != "0.28.0":
                    raise ValueError("unqualified live vLLM version")
                response = await client.get(url + "/models")
                response.raise_for_status()
                qualified_http.validate_live_models({"old_sft": endpoint}, response.json())
                s.write_once(output / "MODELS_PREFLIGHT.json", response.json())
                collection_started = time.time()
                left = min(900, launch + 1680 - collection_started)
                if left <= 0:
                    raise TimeoutError("no collection time remains")
                _, reason = await s.collect_calls(client, url, spec, output, time.monotonic() + left)
    except TimeoutError:
        reason = "owned_work_deadline"
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
        s.write_once(output / "STATUS.json", {"planned": 128, "recorded": len(records), "stop_reason": reason,
            "actual_typed_prompt_matches": sum(p["typed_template_equal"] is True for p in physical),
            "collection_seconds": time.time() - collection_started if collection_started else None,
            "overall_elapsed_seconds": time.time() - launch,
            "unrun": [r["id"] for r in spec["design"]["plan"] if r["id"] not in seen]})
    return 0 if reason is None and len(records) == 128 else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["prepare", "verify", "run"])
    parser.add_argument("--endpoint", type=Path)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs/attempt-001")
    parser.add_argument("--overall-start-epoch", type=float)
    args = parser.parse_args()
    if args.command == "prepare":
        prepare()
    elif args.command == "verify":
        verify(s.read(ROOT / "SPEC.json"))
        print("verified", flush=True)
    else:
        if args.endpoint is None:
            parser.error("actual endpoint descriptor required")
        raise SystemExit(asyncio.run(run(args.endpoint.resolve(), args.output_dir.resolve(), args.overall_start_epoch)))


if __name__ == "__main__":
    main()
