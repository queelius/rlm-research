"""Freeze an outcome-blind, locally unqueried official AG test panel."""

from collections import Counter, defaultdict
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import unicodedata

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
CACHE = Path("/project/alex_phd/research-cache/datasets/fancyzhx--ag_news--eb185aade064a813bc0b7f42de02595523103ca4")
PARQUET = CACHE / "test.parquet"
PARQUET_SHA = "71de87ec66bc5737752a2502204dfa6d7fe9856ade3ea444dc6317789a4f13fb"
REVISION = "eb185aade064a813bc0b7f42de02595523103ca4"
BUILDER = SIDE / "helper-unseen-generalization-panel-v1/build_panel.py"
BATCH_SOURCES = SIDE / "root-c32-helper-batchsize-v1/inputs/SOURCES.json"
MODEL = Path("/project/alex_phd/research-cache/models/Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554")
CHILD_ALIAS = "strict-rlm-qwen3-4b-role-sft-selected-v1"
NAMESPACE = "helper-agnews-official-test-fresh512-v1|20260912"
LABELS = {0: "World", 1: "Sports", 2: "Business", 3: "Sci/Tech"}


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def whitespace(text):
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def word(text):
    return " ".join(re.findall(r"\w+", unicodedata.normalize("NFKC", text).casefold()))


def extract(value, rows):
    if isinstance(value, dict):
        if value.get("dataset") == "ag_news" and isinstance(value.get("text"), str):
            rows.append(value)
        for item in value.values():
            extract(item, rows)
    elif isinstance(value, list):
        for item in value:
            extract(item, rows)


def exposure_inventory():
    listed = subprocess.run(
        ["rg", "-l", '"dataset": "ag_news"', str(SIDE), "--glob", "*.json"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    paths = sorted(
        Path(path)
        for path in listed
        if "/outputs/" not in path and not path.startswith(str(ROOT) + "/")
    )
    rows, by_path = [], {}
    for path in paths:
        found = []
        extract(read(path), found)
        if found:
            rows.extend(found)
            by_path[str(path)] = {
                "sha256": sha(path),
                "ag_news_text_rows": len(found),
                "source_ids": len({row.get("source_id") for row in found if row.get("source_id")}),
            }
    ids = {row["source_id"] for row in rows if isinstance(row.get("source_id"), str)}
    norms = {normalizer(row["text"]) for row in rows for normalizer in (whitespace, word)}
    return ids, norms, by_path


def load_builder():
    spec = importlib.util.spec_from_file_location("ag_test_standard_builder", BUILDER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_inputs():
    if sha(PARQUET) != PARQUET_SHA:
        raise ValueError("official AG test parquet changed")
    raw = pq.read_table(PARQUET, columns=["text", "label"]).to_pylist()
    if len(raw) != 7600:
        raise ValueError("official AG test inventory differs")
    exposed_ids, exposed_norms, exposure_files = exposure_inventory()
    groups = defaultdict(list)
    for index, row in enumerate(raw):
        groups[word(row["text"])].append(index)
    duplicate_indices = {index for values in groups.values() if len(values) > 1 for index in values}
    eligible = []
    for index, row in enumerate(raw):
        source_id = f"test:{index}"
        if (
            index in duplicate_indices
            or source_id in exposed_ids
            or whitespace(row["text"]) in exposed_norms
            or word(row["text"]) in exposed_norms
        ):
            continue
        eligible.append({"source_id": source_id, "source_row_0based": index, "text": row["text"], "label_id": int(row["label"])})
    selected = []
    for label_id in LABELS:
        candidates = sorted(
            (row for row in eligible if row["label_id"] == label_id),
            key=lambda row: hashlib.sha256(f"{NAMESPACE}|candidate|{row['source_id']}".encode()).hexdigest(),
        )
        if len(candidates) < 128:
            raise ValueError("insufficient untouched records")
        selected.extend(candidates[:128])
    selected.sort(key=lambda row: hashlib.sha256(f"{NAMESPACE}|order|{row['source_id']}".encode()).hexdigest())
    public_records, labels, provenance = [], {}, []
    for row in selected:
        identifier = "agte" + hashlib.sha256(f"{NAMESPACE}|id|{row['source_id']}".encode()).hexdigest()[:16]
        public_records.append({"dataset": "ag_news", "id": identifier, "source_id": row["source_id"], "text": row["text"]})
        labels[identifier] = LABELS[row["label_id"]]
        provenance.append({"id": identifier, "source_id": row["source_id"], "source_row_0based": row["source_row_0based"], "text_sha256": hashlib.sha256(row["text"].encode()).hexdigest(), "label_id": row["label_id"]})
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL, local_files_only=True)
    builder = load_builder()
    historical = read(BATCH_SOURCES)["contexts"]["question-sensitive-sft-train-05"]["partitions"]["4"]["0"]
    old_ids = tokenizer.encode(historical["request_text"], add_special_tokens=False)
    body = historical["body"]
    hits = [i for i in range(len(body["token_ids"]) - len(old_ids) + 1) if body["token_ids"][i:i + len(old_ids)] == old_ids]
    if len(hits) != 1:
        raise ValueError("historical prompt boundary differs")
    offset = hits[0]
    prefix, suffix = body["token_ids"][:offset], body["token_ids"][offset + len(old_ids):]
    requests = []
    for start in range(0, 512, 4):
        group = public_records[start:start + 4]
        request_text, allowed = builder.prompt("ag_news", group)
        ids = [row["id"] for row in group]
        schema = {"type": "object", "properties": {key: {"type": "string", "enum": allowed} for key in ids}, "required": ids, "additionalProperties": False}
        schema_text = json.dumps(schema, separators=(",", ":"), ensure_ascii=False)
        native = {
            "model": CHILD_ALIAS,
            "token_ids": prefix + tokenizer.encode(request_text, add_special_tokens=False) + suffix,
            "sampling_params": {**body["sampling_params"], "temperature": 0.0, "seed": 202609122800 + len(requests), "max_tokens": 1024, "structured_outputs": {"json": schema}},
            "cache_salt": "0",
        }
        requests.append({"request_id": hashlib.sha256(f"{NAMESPACE}|request|{start}".encode()).hexdigest(), "dataset": "ag_news", "start": start, "ids": ids, "request_text": request_text, "schema_ordered_json": schema_text, "body_template": native})
    selected_ids = {row["source_id"] for row in selected}
    selected_norms = {word(row["text"]) for row in selected}
    audit = {
        "source_rows": 7600,
        "eligible_after_all_exclusions": len(eligible),
        "eligible_per_label": dict(sorted(Counter(row["label_id"] for row in eligible).items())),
        "selected_per_label": dict(sorted(Counter(row["label_id"] for row in selected).items())),
        "selected_source_id_overlap": len(selected_ids & exposed_ids),
        "selected_normalized_overlap": len(selected_norms & exposed_norms),
        "within_test_word_duplicate_groups_rejected": sum(len(values) > 1 for values in groups.values()),
        "within_test_duplicate_rows_rejected": len(duplicate_indices),
        "selected_duplicate_group_members": sum(row["source_row_0based"] in duplicate_indices for row in selected),
        "exposure_files": exposure_files,
        "selection_used_model_outcomes": False,
        "planned_calls": 128,
        "planned_records": 512,
        "batch": 4,
        "temperature": 0,
        "max_prompt_plus_completion": max(len(row["body_template"]["token_ids"]) + 1024 for row in requests),
    }
    return {
        "public": {"schema": "agnews-official-test-fresh512-public-v1", "contains_gold": False, "records": public_records},
        "gold": {"schema": "agnews-official-test-fresh512-host-gold-v1", "never_include_in_model_prompt": True, "labels": labels},
        "provenance": provenance,
        "requests": requests,
        "audit": audit,
    }


def write_x(path, value, *, sort_keys=True):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=sort_keys, ensure_ascii=False)
        stream.write("\n")


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") not in (None, "") or (ROOT / "inputs").exists():
        raise ValueError("CPU-only unused input freeze required")
    bundle = make_inputs()
    write_x(ROOT / "inputs/PUBLIC.json", bundle["public"])
    write_x(ROOT / "inputs/HOST_GOLD.json", bundle["gold"])
    write_x(ROOT / "inputs/SELECTED_PROVENANCE.json", bundle["provenance"])
    write_x(ROOT / "inputs/REQUESTS.json", bundle["requests"], sort_keys=False)
    write_x(ROOT / "inputs/EXCLUSION_AUDIT.json", bundle["audit"])
    sources = {
        str(PARQUET): sha(PARQUET), str(CACHE / "ACQUISITION.json"): sha(CACHE / "ACQUISITION.json"),
        str(CACHE / "README.md"): sha(CACHE / "README.md"), str(BUILDER): sha(BUILDER), str(BATCH_SOURCES): sha(BATCH_SOURCES),
    }
    for path, row in bundle["audit"]["exposure_files"].items():
        sources[path] = row["sha256"]
    artifacts = {str(path): sha(path) for path in sorted((ROOT / "inputs").iterdir())}
    ready = {
        "schema": "helper-agnews-official-test-fresh512-data-ready-v1",
        "status": "CPU_FROZEN_OUTCOME_BLIND_NO_MODEL_CALLS",
        "question": "Does the broader AG gain replicate on locally unqueried official-test articles, and do RL8/SFT8 differ?",
        "claim_boundary": "new local examples from the same AG task/source test partition; not a new domain and base pretraining exposure unknown",
        "intended_fixed_arms": ["c32", "rl_step8_seed1", "sft_step8", "rl_step8_seed2_if_exactly_qualified"],
        "seed_selection": "none; seed2 is a replication arm, not selected as best",
        "source_revision": REVISION,
        "source_license": "unknown; source card says research/non-commercial",
        "publication": "Do not publish or commit source texts while redistribution rights remain unconfirmed.",
        "source_sha256": sources,
        "artifact_sha256": artifacts,
        "inventory": bundle["audit"],
        "model_or_gpu_calls": 0,
    }
    ready["identity"] = digest(ready)
    write_x(ROOT / "DATA_READY.json", ready)
    print(json.dumps({"identity": ready["identity"], "data_ready_sha256": sha(ROOT / "DATA_READY.json"), "eligible": bundle["audit"]["eligible_after_all_exclusions"]}))


if __name__ == "__main__":
    main()

