"""CPU-only native rendering, grammar qualification, transitive pins and READY freeze."""

import hashlib
import importlib.metadata
import os
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import driver
import lifecycle
import study as s


def typed_ids(tokenizer, body):
    from vllm.entrypoints.openai.chat_completion.protocol import ChatCompletionRequest

    parsed = ChatCompletionRequest.model_validate(deepcopy(body))
    tools = [tool.model_dump() for tool in parsed.tools] if parsed.tools else None
    return tokenizer.apply_chat_template(body["messages"], tools=tools,
        add_generation_prompt=True, tokenize=True, return_dict=False,
        **parsed.chat_template_kwargs)


def synthetic(gold, label):
    if gold["arm"] == "plain":
        return [label] * 64
    return [{"tag": record["id"] if gold["arm"] == "matching" else "p0000",
             "label": label} for record in gold["records"]]


def qualify(design, requests):
    import xgrammar as xg
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(s.MODEL["path"], local_files_only=True,
                                               trust_remote_code=False)
    config = s.read(Path(s.MODEL["path"]) / "config.json")
    vocab_size = config.get("text_config", config)["vocab_size"]
    compiler = xg.GrammarCompiler(xg.TokenizerInfo.from_huggingface(tokenizer,
        vocab_size=vocab_size), max_threads=2, cache_enabled=True)
    rendered = {}
    prompt_ids = {}
    schema_seen = set()
    negative = 0
    for row in design["plan"]:
        body = requests[row["id"]]
        if row["decoder"] == "exact":
            schema = body["structured_outputs"]["json"]
            schema_hash = s.digest(schema)
            if schema_hash not in schema_seen:
                compiled = compiler.compile_json_schema(s.serialize(schema), any_whitespace=True)
                gold = design["batches"][row["batch_id"]]["gold"]
                legal = synthetic(gold, gold["labels"][0])
                matcher = xg.GrammarMatcher(compiled)
                if not matcher.accept_string(s.serialize(legal).encode()) or not matcher.is_completed():
                    raise ValueError("legal schema fixture rejected")
                for bad in (legal[:-1], legal + [legal[-1]]):
                    matcher = xg.GrammarMatcher(compiled)
                    if matcher.accept_string(s.serialize(bad).encode()) and matcher.is_completed():
                        raise ValueError("invalid cardinality accepted")
                    negative += 1
                schema_seen.add(schema_hash)
        tokens = typed_ids(tokenizer, body)
        if len(tokens) + 3072 > 8192:
            raise ValueError("prompt plus output allowance exceeds context")
        tail = tokenizer.decode(tokens[-16:])
        if not tail.endswith("<|im_start|>assistant\n"):
            raise ValueError("native Qwen3 assistant prefix changed")
        prompt_ids[row["id"]] = tokens
        rendered[row["id"]] = {"tokens": len(tokens),
            "typed_token_ids_sha256": s.digest(tokens), "tail": tail,
            "system_role": row["system_role"], "tools": row["tools"]}
    return {"requests": 96, "rendered_prompts": rendered,
            "max_input_plus_output": max(len(tokens) for tokens in prompt_ids.values()) + 3072,
            "negative_grammar_cases": negative,
            "versions": {name: importlib.metadata.version(name)
                         for name in ("vllm", "transformers", "xgrammar", "httpx")},
            "gpu_calls": 0, "model_calls": 0,
            "qualification": "CPU native typed rendering and exact grammar fixtures; no service"}, prompt_ids


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("CPU preparation must hide GPUs")
    for name in ("SPEC.json", "READY.json", "REQUESTS.json", "PROMPT_IDS.json",
                 "CPU_QUALIFICATION.json", "CPU_TESTS.json", "WEIGHTS.json", "DISPATCH.json"):
        if (s.ROOT / name).exists():
            raise FileExistsError("fresh preparation requires absent " + name)

    seed_paths = []
    for child in s.SIDE.iterdir():
        if child.is_dir() and child != s.ROOT:
            for pattern in ("*SPEC*.json", "*READY*.json", "*SEED*.json", "*RECIPE*.json"):
                seed_paths.extend(path for path in child.glob(pattern) if path.is_file())
    seed_scan = subprocess.run(["rg", "-n", rf"\b({s.MASTER_SEED}|{s.SAMPLE_SEED})\b",
                                *map(str, sorted(set(seed_paths)))], capture_output=True, text=True,
                               timeout=60)
    if seed_scan.returncode != 1:
        raise ValueError("seed collision or scan failure: " + seed_scan.stdout[:1000])
    s.write_once(s.ROOT / "SEED_AUDIT.json", {"master": s.MASTER_SEED,
        "sampling": s.SAMPLE_SEED, "returncode": seed_scan.returncode,
        "scope": "Sibling top-level SPEC/READY/SEED/RECIPE files; own namespace excluded."})

    data = s.build_data()
    design = s.build_design(data)
    requests = {row["id"]: s.make_request(design, row) for row in design["plan"]}
    for context in design["contexts"]:
        rows = [row for row in design["plan"] if row["context_index"] == context["index"]]
        for role in s.ROLES:
            for tools in s.TOOLS:
                for arm in s.ARMS:
                    pair = [requests[row["id"]] for row in rows if
                            (row["system_role"], row["tools"], row["arm"]) == (role, tools, arm)]
                    free = next(body for row, body in zip(
                        [r for r in rows if (r["system_role"], r["tools"], r["arm"]) ==
                         (role, tools, arm)], pair, strict=True) if row["decoder"] == "free")
                    exact = next(body for row, body in zip(
                        [r for r in rows if (r["system_role"], r["tools"], r["arm"]) ==
                         (role, tools, arm)], pair, strict=True) if row["decoder"] == "exact")
                    if {key: value for key, value in exact.items() if key != "structured_outputs"} != free:
                        raise ValueError("free/exact pairing changed")
    qualification, prompt_ids = qualify(design, requests)
    design["rendered_prompts"] = qualification["rendered_prompts"]

    model_root = Path(s.MODEL["path"])
    manifest_path = model_root / "local-research-manifest.json"
    if s.sha(manifest_path) != s.MODEL["manifest_sha256"]:
        raise ValueError("model manifest changed")
    manifest = s.read(manifest_path)
    if manifest["huggingface_revision"] != s.MODEL["revision"]:
        raise ValueError("model revision changed")
    sources = dict(data["source_provenance"]["source_sha256"])
    sources[str(manifest_path)] = s.MODEL["manifest_sha256"]
    stats = {}
    files = {}
    for name, expected in manifest["files"].items():
        path = model_root / name
        files[str(path)] = expected
        if name.endswith(".safetensors"):
            stat = path.stat()
            stats[str(path)] = [stat.st_size, stat.st_mtime_ns, stat.st_ino]
        elif s.sha(path) != expected:
            raise ValueError("model auxiliary file changed: " + str(path))
        else:
            sources[str(path)] = expected
    for name in ("LICENSE", "README.md"):
        sources[str(model_root / name)] = s.sha(model_root / name)
    if sources[str(model_root / "LICENSE")] != manifest["license_sha256"]:
        raise ValueError("model license changed")
    weights = {"schema": "released-qwen3-4b-no-adapter-binding-v1", "model": s.MODEL,
               "adapter": None, "files_sha256": files, "weight_stat_identity": stats,
               "license": manifest["license"], "full_tensor_hashes": "reused from authenticated local manifest"}

    inherited_ready_path = s.SOURCE / "READY_RECOVERY3.json"
    inherited_ready = s.read(inherited_ready_path)
    sources[str(inherited_ready_path)] = s.sha(inherited_ready_path)
    for path, expected in inherited_ready["source_sha256"].items():
        if s.sha(path) != expected:
            raise ValueError("inherited qualified closure changed: " + path)
        sources[path] = expected
    for path in (s.ROOT / "study.py", s.ROOT / "driver.py", s.ROOT / "service.py",
                 s.ROOT / "lifecycle.py", s.ROOT / "owner.py", s.ROOT / "select_data.py",
                 s.ROOT / "test_contract.py", s.ROOT / "prepare.py", s.ROOT / "DESIGN.md",
                 s.ROOT / "RUNBOOK.md", s.ROOT / "DATA.json", s.ROOT / "SELECTION_PROVENANCE.json",
                 s.SIDE.parent / "ideas/2026-09-09-learned-correspondence-sft-design.md"):
        sources[str(path)] = s.sha(path)

    for name, value in (("REQUESTS.json", requests), ("PROMPT_IDS.json", prompt_ids),
                        ("CPU_QUALIFICATION.json", qualification), ("WEIGHTS.json", weights),
                        ("DISPATCH.json", {"workers": 4, "order": design["plan"],
                                           "pairing": "Free/exact adjacent with alternating order."})):
        s.write_once(s.ROOT / name, value)
        sources[str(s.ROOT / name)] = s.sha(s.ROOT / name)

    tests = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                            "test_contract.py"], cwd=s.ROOT, env={**os.environ,
                            "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"},
                           capture_output=True, text=True, timeout=120)
    s.write_once(s.ROOT / "CPU_TESTS.json", {"argv": tests.args, "returncode": tests.returncode,
        "stdout": tests.stdout, "stderr": tests.stderr, "gpu_calls": 0, "model_calls": 0,
        "red": "Initial five tests failed because study/driver were absent; collector test then failed because run was absent."})
    if tests.returncode:
        raise ValueError("focused CPU tests failed")
    sources[str(s.ROOT / "CPU_TESTS.json")] = s.sha(s.ROOT / "CPU_TESTS.json")

    spec = {"schema": "leaf-role-tool-contract-spec-v1",
        "question": "Does the coding-agent role or IPython advertisement cause free long-batch output failure?",
        "design": design, "requests": requests,
        "request_sha256": {key: s.digest(value) for key, value in requests.items()},
        "ordered_request_sha256": {key: hashlib.sha256(s.serialize(value).encode()).hexdigest()
                                   for key, value in requests.items()},
        "source_sha256": sources, "weight_stat_identity": stats, "model": s.MODEL,
        "frozen_before_inference": True,
        "budget": {"real_calls": 96, "workers": 4, "max_tokens_per_call": 3072,
                   "collector_seconds": 1500, "shared_work_seconds": 1680,
                   "owned_seconds": 1770, "outer_seconds": 1800},
        "scoring": {"primary": "Free-decoder full-contract-valid strict positional labels on planned denominator.",
                    "completed_invalid": "Observed zero, including capped, malformed, code, wrapper and tool-call output.",
                    "infrastructure_missing": "NULL with per-call [0,64] bounds.",
                    "forbidden": ["tool execution", "ID reordering", "answer repair", "prefix rescue"]},
        "causal_scope": "System replacement is a package contrast; tools present/absent is factorial within system. Two contexts/task and one seed are exploratory."}
    spec["spec_id"] = s.digest(spec)
    s.write_once(s.ROOT / "SPEC.json", spec)
    driver.verify(spec)

    import owner
    owner.load_suite()
    ready_sources = {**sources, str(s.ROOT / "SPEC.json"): s.sha(s.ROOT / "SPEC.json")}
    ready = {"status": "CPU_READY_FOR_MAIN_ACCEPTANCE_NOT_LAUNCHED",
        "schema": "leaf-role-tool-contract-ready-v1", "spec_sha256": s.sha(s.ROOT / "SPEC.json"),
        "source_sha256": ready_sources, "output": str(s.ROOT / "outputs/attempt-001"),
        "launch_argv": [str(owner.NATIVE), str(s.ROOT / "owner.py"), "run", "--output",
                        str(s.ROOT / "outputs/attempt-001")],
        "verify_argv": [str(owner.NATIVE), str(s.ROOT / "owner.py"), "verify"],
        "budget": spec["budget"], "credential": "MAIN privately exports nonempty STRICT_RLM_CALIBRATION_API_KEY before verify/run; value is never serialized.",
        "qualified_service_wrapper": str(lifecycle.SERVICE), "gpu_calls": 0, "model_calls": 0,
        "main_owns_gpu_lock_acceptance_and_launch": True,
        "max_input_plus_output": qualification["max_input_plus_output"]}
    ready["identity"] = s.digest(ready)
    s.write_once(s.ROOT / "READY.json", ready)
    print(s.serialize({"ready_sha256": s.sha(s.ROOT / "READY.json"),
                       "identity": ready["identity"], "tests": tests.stdout.strip(),
                       "max_input_plus_output": qualification["max_input_plus_output"]}))


if __name__ == "__main__":
    main()
