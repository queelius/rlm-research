"""Freeze fresh contexts and 192 exact positional-anchor requests on CPU."""

import copy
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re
import time

import protocol as p
import study as s


PARQUET = Path("/project/alex_phd/research-cache/datasets/multinli-correspondence-feasibility-20260909-da70db2/validation_matched.parquet")
PARQUET_SHA = "350c26950b55f460b50d36c76aef87d64b49c78812d7abf7bf97e5fede10f186"
CACHE = PARQUET.parent


def loader():
    return s.load("positional_anchor_new_context_loader", s.LOADER / "prepare.py", "7f0958b789af8969264d6fe8aa08b4f383c784a81232def78e5ae9a002fe575d", {"study": s, "protocol": p})


def named_ids():
    values, paths = set(), []
    pattern = re.compile(r'"(m[0-9a-f]{12})"')
    for directory in sorted(s.SIDE.glob("*mnli*")):
        if directory == s.ROOT:
            continue
        for path in sorted(directory.iterdir()):
            if path.is_file() and path.suffix == ".json" and path.name.startswith(("DATA", "PUBLIC", "ALIEN")):
                paths.append(path)
                values.update(pattern.findall(path.read_text(errors="replace")))
    return paths, values


def aliens(contexts, tokenizer, occupied):
    result = {}
    for context in contexts:
        values = []
        for position, target in enumerate(p.requested_tags(context)):
            wanted = len(tokenizer.encode(target, add_special_tokens=False))
            nonce = 0
            while True:
                candidate = "m" + hashlib.sha256(f"{s.ROOT.name}:{p.MASTER}:{context['index']}:{position}:{nonce}".encode()).hexdigest()[:12]
                if candidate not in occupied and len(tokenizer.encode(candidate, add_special_tokens=False)) == wanted:
                    break
                nonce += 1
            occupied.add(candidate)
            values.append(candidate)
        result[str(context["index"])] = values
    return result


def typed_prompt(tokenizer, body):
    from vllm.entrypoints.openai.chat_completion.protocol import ChatCompletionRequest

    value = ChatCompletionRequest.model_validate(copy.deepcopy(body))
    if value.tools:
        raise ValueError("tools prohibited")
    return tokenizer.apply_chat_template(body["messages"], tools=None, add_generation_prompt=True, tokenize=True, return_dict=False, **value.chat_template_kwargs)


def seed_scan():
    started = time.time()
    needles = {str(seed) for seed in p.SEEDS}
    matches = []
    paths = set(s.SIDE.glob("*/*.json")) | set(s.SIDE.glob("*/inputs/*.json"))
    for path in sorted(paths):
        if s.ROOT in path.parents:
            continue
        try:
            text = path.read_text(errors="replace")
        except FileNotFoundError:
            continue
        found = sorted(needles & set(re.findall(r"\b\d{9}\b", text)))
        if found:
            matches.append({"path": str(path), "seeds": found})
    return {"started_epoch": started, "ended_epoch": time.time(), "scope": "named non-output sidecar JSON files existing at scan time", "matches_outside_new_sidecar": matches}


def freeze(path, value):
    if path.exists():
        if s.read(path) != value:
            raise ValueError("partial preparation identity differs: " + str(path))
    else:
        s.write(path, value)


def main():
    import pyarrow.parquet as pq
    import xgrammar as xg

    if s.sha(PARQUET) != PARQUET_SHA:
        raise ValueError("source parquet changed")
    started = time.time()
    helper = loader()
    inventory_paths, excluded, prior_groups = helper.named_inventory()
    rows = pq.read_table(PARQUET).to_pylist()
    contexts, counts, conflicts, ranked = helper.select(rows, excluded)
    if contexts is None:
        s.write(s.ROOT / "INSUFFICIENT_POOL.json", {"eligible_by_genre": counts, "required_by_genre": 64, "preserved": True})
        raise ValueError("insufficient eligible pool")
    rotated = [{**row, "label": (row["label"] + 1) % 3 if row["label"] in (0, 1, 2) else row["label"]} for row in rows]
    changed, _, _, changed_ranked = helper.select(rotated, excluded)
    invariant = changed is not None and helper.public(changed) == helper.public(contexts) and ranked == changed_ranked
    selected_groups = {group for context in contexts for group in context["premise_groups"]}
    overlap = sorted(selected_groups & prior_groups)
    if not invariant or overlap or conflicts:
        raise ValueError("selection invariant")
    tokenizer = s.tokenizer()
    id_paths, occupied = named_ids()
    alien = aliens(contexts, tokenizer, occupied)
    freeze(s.ROOT / "DATA.json", {"contexts": contexts})
    freeze(s.ROOT / "PUBLIC.json", helper.public(contexts))
    freeze(s.ROOT / "ALIEN_DICTIONARIES.json", alien)
    plan = p.plan()
    requests = {row["id"]: p.request(contexts[row["context_index"]], row) for row in plan}
    wires = {key: s.serialize(value) for key, value in requests.items()}
    prompts = {key: typed_prompt(tokenizer, value) for key, value in requests.items()}
    config = s.read(Path(s.MODEL["path"]) / "config.json")
    vocabulary = config.get("text_config", config)["vocab_size"]
    compiler = xg.GrammarCompiler(xg.TokenizerInfo.from_huggingface(tokenizer, vocab_size=vocabulary), max_threads=2, cache_enabled=True)
    checks = []
    for row in plan:
        schema_text = s.serialize(requests[row["id"]]["structured_outputs"]["json"])
        grammar = compiler.compile_json_schema(schema_text, any_whitespace=True)
        matcher = xg.GrammarMatcher(grammar)
        context = contexts[row["context_index"]]
        if row["output"] == "labels_only":
            good = ["neutral"] * 48
        else:
            good = [{"row": index, "label": "neutral"} for index in range(48)]
        if not matcher.accept_string(s.serialize(good).encode()) or not matcher.is_completed():
            raise ValueError("grammar rejects canonical output")
        if len(prompts[row["id"]]) + 3072 > 8192:
            raise ValueError("native context overflow")
        checks.append({"id": row["id"], "prompt_tokens": len(prompts[row["id"]]), "canonical_contract_accepts": True})
    scan = seed_scan()
    if scan["matches_outside_new_sidecar"]:
        raise ValueError("seed collision")
    selection = {"master": p.MASTER, "source_rows": len(rows), "source_parquet_sha256": s.sha(PARQUET), "named_inventory_paths": [str(path) for path in inventory_paths], "named_inventory_sha256": {str(path): s.sha(path) for path in inventory_paths}, "named_id_paths": [str(path) for path in id_paths], "excluded_premise_groups": len(prior_groups), "excluded_normalized_text_hashes": len(excluded), "eligible_by_genre": counts, "selected_contexts": 16, "selected_premise_groups": 256, "prior_selected_overlap": overlap, "eligibility_uses_labels": True, "ranking_uses_labels": False, "label_mutation_ranking_invariant": invariant, "scope": "all named MNLI DATA/PUBLIC/GROUPS/PLAN inventories including latest field96; not global/pretraining unseen"}
    manifest = {"dataset": "nyu-mll/multi_nli", "revision": "da70db2af9d09693783c3320c4249840212ee221", "split": "validation_matched", "license": "Mixed OANC permissive terms / CC-BY-3.0 / CC-BY-SA-3.0 / public-domain fiction; see pinned card", "parquet_sha256": s.sha(PARQUET), "readme_sha256": s.sha(CACHE / "README.md"), "acquisition_sha256": s.sha(CACHE / "ACQUISITION.json"), "retrieved_utc": s.read(CACHE / "ACQUISITION.json")["retrieved_utc"]}
    artifacts = {"PLAN.json": plan, "REQUESTS.json": requests, "ORDERED_REQUESTS.json": wires, "PROMPT_IDS.json": prompts, "CPU_NATIVE.json": {"requests": 192, "schemas_compiled": 192, "checks": checks, "max_prompt_tokens": max(map(len, prompts.values())), "max_prompt_plus_output": max(map(len, prompts.values())) + 3072, "request_wire_sha256": {key: hashlib.sha256(value.encode()).hexdigest() for key, value in wires.items()}, "versions": {name: importlib.metadata.version(name) for name in ("vllm", "transformers", "xgrammar")}, "gpu_calls": 0, "service_calls": 0, "elapsed_seconds": time.time() - started}, "PLANNED_NULL_ENDPOINTS.json": [p.null_row(row, "not attempted") for row in plan], "SELECTION_AUDIT.json": selection, "SEED_SCAN.json": scan, "DATASET_MANIFEST.json": manifest}
    for name, value in artifacts.items():
        freeze(s.ROOT / name, value)
    print({"contexts": 16, "requests": len(plan), "eligible_by_genre": counts, "max_prompt": max(map(len, prompts.values()))})


if __name__ == "__main__":
    main()
