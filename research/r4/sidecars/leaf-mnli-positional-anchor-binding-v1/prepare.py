"""Freeze paired positional-anchor coordinates, native prompts, and grammars."""

import copy
import hashlib
import importlib.metadata
import time
from pathlib import Path

import protocol as p
import study as s


def scan_seeds():
    started = time.time()
    needles = tuple(str(seed) for seed in p.SEEDS)
    approved_proposal = s.SIDE.parent / "ideas/2026-09-10-mnli-positional-anchor-binding-design.md"
    matches = []
    root = s.SIDE.parent
    for path in root.rglob("*"):
        if not path.is_file() or s.ROOT in path.parents or path == approved_proposal or path.suffix not in {".json", ".md", ".py"}:
            continue
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        if any(needle in text for needle in needles):
            matches.append(str(path))
    return {"schema": "named-catalog-seed-scan-v1", "started_epoch": started, "ended_epoch": time.time(), "seeds": list(p.SEEDS), "excluded_path": str(s.ROOT), "excluded_approved_proposal": str(approved_proposal), "matches_outside_new_sidecar": sorted(matches), "outcomes_consulted": False}


def main():
    import xgrammar as xg
    from vllm.entrypoints.openai.chat_completion.protocol import ChatCompletionRequest

    started = time.time()
    tokenizer = s.tokenizer()
    contexts = p.contexts()
    rows = p.plan()
    requests = {row["id"]: p.request(contexts[row["context_index"]], row) for row in rows}
    wires = {key: s.serialize(value) for key, value in requests.items()}
    prompts = {}
    for key, body in requests.items():
        typed = ChatCompletionRequest.model_validate(copy.deepcopy(body))
        if typed.tools:
            raise ValueError("no tools allowed")
        prompts[key] = tokenizer.apply_chat_template(body["messages"], tools=None, add_generation_prompt=True, tokenize=True, return_dict=False, **typed.chat_template_kwargs)
    config = s.read(Path(s.MODEL["path"]) / "config.json")
    vocabulary = config.get("text_config", config)["vocab_size"]
    compiler = xg.GrammarCompiler(xg.TokenizerInfo.from_huggingface(tokenizer, vocab_size=vocabulary), max_threads=2, cache_enabled=True)
    checks = []
    for row in rows:
        body = requests[row["id"]]
        grammar = compiler.compile_json_schema(s.serialize(body["structured_outputs"]["json"]), any_whitespace=True)

        def accepts(value):
            matcher = xg.GrammarMatcher(grammar)
            return matcher.accept_string(s.serialize(value).encode()) and matcher.is_completed()

        labels = [p.LABELS[index % len(p.LABELS)] for index in range(48)]
        if row["output"] == "labels_only":
            good = labels
            bad = labels[:-1]
        else:
            good = [{"row": index, "label": label} for index, label in enumerate(labels)]
            bad = [dict(value) for value in good]
            bad[17]["row"] = 16
        if not accepts(good) or accepts(bad):
            raise ValueError("grammar qualification failed")
        if len(prompts[row["id"]]) + 3072 > 8192:
            raise ValueError("native context admission")
        checks.append({"id": row["id"], "arm": row["arm"], "prompt_tokens": len(prompts[row["id"]]), "good_accepted": True, "bad_rejected": True})
    seed_scan = scan_seeds()
    if seed_scan["matches_outside_new_sidecar"]:
        raise ValueError("seed collision")
    actual_context_source = p.prior.s.PRIOR
    source_paths = [s.PRIOR / "READY_v2.json", s.PRIOR / "protocol_v2.py", actual_context_source / "DATA.json", actual_context_source / "ALIEN_DICTIONARIES_v2.json"]
    input_receipt = {"created_epoch": time.time(), "context_count": 8, "records_per_context": 48, "planned": 96, "arm_counts": {arm: sum(row["arm"] == arm for row in rows) for arm in p.ARMS}, "source_sha256": {str(path): s.sha(path) for path in source_paths}, "all_original_record_fields_preserved": True, "row_field_is_only_input_mutation": True, "outcomes_consulted": False}
    native = {"requests": 96, "schemas_compiled": 96, "schema_checks": checks, "gpu_calls": 0, "service_calls": 0, "request_wire_sha256": {key: hashlib.sha256(value.encode()).hexdigest() for key, value in wires.items()}, "max_prompt_tokens": max(map(len, prompts.values())), "max_prompt_plus_output": max(map(len, prompts.values())) + 3072, "versions": {name: importlib.metadata.version(name) for name in ("vllm", "transformers", "xgrammar")}, "elapsed_seconds": time.time() - started}
    for name, value in {"PLAN.json": rows, "REQUESTS.json": requests, "ORDERED_REQUESTS.json": wires, "PROMPT_IDS.json": prompts, "CPU_NATIVE.json": native, "SEED_SCAN.json": seed_scan, "INPUT_RECEIPT.json": input_receipt, "PLANNED_NULL_ENDPOINTS.json": [p.null_row(row, "not attempted") for row in rows]}.items():
        s.write(s.ROOT / "inputs" / name, value)
    print({"planned": len(rows), "max_prompt_plus_output": native["max_prompt_plus_output"], "elapsed_seconds": native["elapsed_seconds"]})


if __name__ == "__main__":
    main()
