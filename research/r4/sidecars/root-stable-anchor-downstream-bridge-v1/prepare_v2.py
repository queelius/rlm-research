"""Materialize and seal V2 from the exact V1 panel; CPU only."""

import copy
import json
import os
from pathlib import Path
import subprocess
import time

import protocol_v2 as p
import study_v2 as s


def typed(tokenizer, body):
    from vllm.entrypoints.openai.chat_completion.protocol import ChatCompletionRequest
    value = ChatCompletionRequest.model_validate(copy.deepcopy(body))
    return tokenizer.apply_chat_template(body["messages"], tools=None, add_generation_prompt=True,
        tokenize=True, return_dict=False, **value.chat_template_kwargs)


def inputs():
    source = s.ROOT / "inputs"
    public = s.read(source / "PUBLIC.json"); data = s.read(source / "DATA.json")
    gold = s.read(source / "HOST_GOLD.json"); panel = s.read(source / "SELECTION_AUDIT.json")
    if p.digest(data["contexts"]) != panel["panel_sha256"]: raise ValueError("exact V1 panel changed")
    preflight_path = s.SCALE / "outputs/attempt-002/service-sft6/SUITE_PREFLIGHT.json"
    if s.sha(preflight_path) != "e42acb046d695b696c206dd597404c3e9b2030dc83dced2dccbea081e569cda7": raise ValueError("service evidence changed")
    preflight = s.read(preflight_path); cards = preflight.get("models", preflight.get("live_models", preflight))
    serialized = json.dumps(cards, sort_keys=True)
    if s.BASE_ALIAS not in serialized: raise ValueError("released base alias not observed in qualified QS6 service")
    contexts = data["contexts"]; plan = p.root_plan(public)
    leaf = {encoding: {c["id"]: p.leaf_request(c, encoding, s.BASE_ALIAS) for c in contexts} for encoding in p.ENCODINGS}
    tokenizer = s.stable.tokenizer(); leaf_prompts = {e: {cid: typed(tokenizer, body) for cid, body in vals.items()} for e, vals in leaf.items()}
    dummy = {row["id"]: "neutral" for row in public[0]["records"]}; prompts = {}
    for row in plan:
        context = next(c for c in public if c["id"] == row["context_id"])
        task = s.make_task(context, row, gold[context["id"]]["answers"][str(row["query_index"])], dummy)
        prompts[row["id"]] = {"prompt": task.data.prompt, "token_ids": s.qnative.first_prefix(task)}
    artifacts = {"DATA.json": data, "PUBLIC.json": public, "HOST_GOLD.json": gold,
        "ROOT_PLAN.json": plan, "FREE_PLAN.json": plan,
        "LEAF_REQUESTS.json": leaf, "LEAF_PROMPT_IDS.json": leaf_prompts,
        "PROMPTS_ACCURATE.json": prompts, "NATIVE_TEMPLATE.json": s.read(source / "NATIVE_TEMPLATE.json"),
        "SELECTION_AUDIT.json": panel, "DATASET_MANIFEST.json": s.read(source / "DATASET_MANIFEST.json"),
        "BASE_ALIAS_SUPPORT.json": {"base_alias": s.BASE_ALIAS, "observed_in_qualified_service": True,
            "source": str(preflight_path), "source_sha256": s.sha(preflight_path)},
        "PLANNED_NULL_ENDPOINTS.json": {"leaf": 24, "root": 96}}
    s.INPUTS.mkdir()
    for name, value in artifacts.items(): s.write(s.INPUTS / name, value)
    if not s.RUNTIME_ROOT.exists(): s.RUNTIME_ROOT.mkdir()
    if not (s.RUNTIME_ROOT / "inputs").exists():
        (s.RUNTIME_ROOT / "inputs").symlink_to(s.INPUTS, target_is_directory=True)


def qualify():
    command = [str(s.NATIVE), "-m", "pytest", "-q", "test_v2.py"]
    started = time.time(); result = subprocess.run(command, cwd=s.ROOT, capture_output=True, text=True, timeout=300,
        env={**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"})
    s.write(s.ROOT / "CPU_TESTS_V2.json", {"argv": command, "returncode": result.returncode, "stdout": result.stdout,
        "stderr": result.stderr, "elapsed_seconds": time.time() - started,
        "source_sha256": {str(path): s.sha(path) for path in (s.ROOT / "protocol_v2.py", s.ROOT / "study_v2.py", s.ROOT / "collect_v2.py", s.ROOT / "owner_v2.py", s.ROOT / "prepare_v2.py", s.ROOT / "test_v2.py")},
        "gpu_calls": 0, "service_calls": 0}); print(result.stdout); print(result.stderr)
    if result.returncode: raise SystemExit(result.returncode)


def seal():
    tests = s.read(s.ROOT / "CPU_TESTS_V2.json")
    if tests["returncode"] != 0: raise ValueError("V2 qualification failed")
    for path, pin in tests["source_sha256"].items():
        if s.sha(path) != pin: raise ValueError("V2 source changed after test: " + path)
    inputs = {str(path): s.sha(path) for path in sorted(s.INPUTS.glob("*.json"))}
    source_names = ("MODEL_ARM_AMENDMENT_V2.md", "protocol_v2.py", "study_v2.py", "collect_v2.py", "owner_v2.py", "prepare_v2.py", "test_v2.py", "CPU_TESTS_V2.json")
    sources = {str(s.ROOT / name): s.sha(s.ROOT / name) for name in source_names}
    sources[str(s.ROOT / "READY.json")] = s.sha(s.ROOT / "READY.json")
    ready = {"schema": "root-stable-anchor-downstream-bridge-ready-v3",
        "status": "CPU_READY_FOR_MAIN_ACCEPTANCE", "supersedes_unlaunched_ready_v1": s.sha(s.ROOT / "READY.json"),
        "supersedes_failed_owner_import_ready_v2": s.sha(s.ROOT / "READY_V2.json"),
        "admitted_encoding": "opaque", "leaf_encodings": list(p.ENCODINGS), "leaf_model": s.BASE_ALIAS,
        "root_model": s.binding()["role_map"]["root"], "planned_model_episodes_minimum": 120,
        "leaf_acquisitions": 24, "root_episodes": 96, "contexts": 8, "clustered_units": 8,
        "panel_sha256": s.read(s.INPUTS / "SELECTION_AUDIT.json")["panel_sha256"],
        "same_panel_queries_seeds_as_v1": True, "model_arm_amendment_pre_output": True,
        "base_alias_support": s.read(s.INPUTS / "BASE_ALIAS_SUPPORT.json"),
        "workers": 4, "request_seconds": 90, "leaf_output_tokens": 3072, "root_output_tokens": 2048,
        "outer_seconds": 2400, "owned_seconds": 2370, "work_seconds": 2250,
        "no_retry_refill_fallback": True, "argv": [str(s.NATIVE), str(s.ROOT / "owner_v2.py"), "run", "--output", str(s.ATTEMPT)],
        "source_sha256": sources, "input_sha256": inputs, "gpu_calls": 0, "service_calls": 0,
        "prepared_epoch": time.time()}
    ready["identity"] = s.digest(ready); s.write(s.ROOT / "READY_V3.json", ready); s.verify()
    print(json.dumps({"ready_sha256": s.sha(s.ROOT / "READY_V3.json"), "identity": ready["identity"]}, sort_keys=True))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("inputs", "qualify", "seal")); args = parser.parse_args()
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "": raise ValueError("CPU only")
    globals()[args.command]()
