"""Frozen public-only components and unchanged native service/validation seams."""

import copy
import functools
import hashlib
import importlib.util
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGET = ROOT.parent / "helper-targeted-category-counts-v1"
spec = importlib.util.spec_from_file_location(
    "adaptive_sealed_target_seams", TARGET / "target_study.py"
)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)
prior = target.prior
read, write, sha, digest = prior.read, prior.write, prior.sha, prior.digest
NATIVE, MODEL, CHILD_ALIAS = prior.NATIVE, prior.MODEL, prior.CHILD_ALIAS
SERVICE, CONTEXT_SOURCE = prior.SERVICE, prior.CONTEXT_SOURCE
source, dependencies = prior.source, prior.dependencies
context_bound, engine_marker = target.context_bound, target.engine_marker
PANEL = ROOT.parent / "helper-adaptive-fresh-panel-v1"
ATTEMPT = ROOT / "outputs/attempt-001"
CAP, CALLS, PREDICTIONS = 1100, 152, 512


@functools.lru_cache(maxsize=1)
def make_schedule():
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(MODEL, local_files_only=True)
    # Wrapper-only reuse. CPU preparation may inspect old panel metadata; live owner never does.
    first = source().panel()[4][0]
    tokens = first["body_template"]["token_ids"]
    needle = tokenizer.encode(first["request_text"], add_special_tokens=False)
    hits = [
        i for i in range(len(tokens) - len(needle) + 1) if tokens[i : i + len(needle)] == needle
    ]
    if len(hits) != 1:
        raise ValueError("ambiguous frozen native wrapper")
    prefix, suffix = tokens[: hits[0]], tokens[hits[0] + len(needle) :]
    public = read(PANEL / "PUBLIC.json")["records"]
    matrix, permutations = {}, {}
    for dataset in ("trec", "ag_news"):
        records = [r for r in public if r["dataset"] == dataset]
        if len(records) != 64:
            raise ValueError("expected frozen64 per dataset")
        matrix[dataset] = [records[i : i + 16] for i in range(0, 64, 16)]
        for arm in ("neighbor_A", "neighbor_B"):
            for column in range(16):
                namespace = f"helper-adaptive-fresh-live-v1|202609121212|{dataset}|{arm}|{column}"
                order = list(range(4))
                random.Random(int(hashlib.sha256(namespace.encode()).hexdigest(), 16)).shuffle(
                    order
                )
                permutations[dataset, arm, column] = order

    def request(dataset, arm, block, selected):
        text, labels = prior.builder().prompt(dataset, selected)
        ids = [r["id"] for r in selected]
        schema = {
            "type": "object",
            "properties": {i: {"type": "string", "enum": labels} for i in ids},
            "required": ids,
            "additionalProperties": False,
        }
        body = copy.deepcopy(first["body_template"])
        body["model"] = CHILD_ALIAS
        body["token_ids"] = prefix + tokenizer.encode(text, add_special_tokens=False) + suffix
        body["sampling_params"]["seed"] = 202609121210 + (dataset == "ag_news")
        body["sampling_params"]["structured_outputs"]["json"] = schema
        return {
            "call_id": digest([ROOT.name, dataset, arm, ids]),
            "dataset": dataset,
            "arm": arm,
            "block": block,
            "start": block * 16,
            "batch_size": len(ids),
            "target": None,
            "labels": labels,
            "ids": ids,
            "request_text": text,
            "schema_ordered_json": json.dumps(schema, separators=(",", ":")),
            "body": body,
            "source_rows_by_column": [permutations[dataset, arm, j][block] for j in range(16)]
            if arm.startswith("neighbor")
            else None,
        }

    rows = []
    for block in range(4):
        for index, dataset in enumerate(("trec", "ag_news")):
            arms = (
                ("original", "neighbor_A")
                if (block + index) % 2 == 0
                else ("neighbor_A", "original")
            )
            for arm in arms:
                selected = (
                    matrix[dataset][block]
                    if arm == "original"
                    else [
                        matrix[dataset][permutations[dataset, arm, j][block]][j] for j in range(16)
                    ]
                )
                rows.append(request(dataset, arm, block, selected))
    for block in range(4):
        for dataset in ("trec", "ag_news"):
            selected = [
                matrix[dataset][permutations[dataset, "neighbor_B", j][block]][j] for j in range(16)
            ]
            rows.append(request(dataset, "neighbor_B", block, selected))
    for dataset in ("trec", "ag_news"):
        for block, records in enumerate(matrix[dataset]):
            for record in records:
                rows.append(request(dataset, "singleton", block, [record]))
    if len(rows) != CALLS or sum(len(r["ids"]) for r in rows) != PREDICTIONS:
        raise ValueError("wrong152/512 component inventory")
    return rows


def schedule():
    rows = read(ROOT / "inputs/SCHEDULE.json")
    for row in rows:
        schema = json.loads(row["schema_ordered_json"])
        if list(schema["properties"]) != row["ids"] or schema["required"] != row["ids"]:
            raise ValueError("ordered schema differs")
        row["body"]["sampling_params"]["structured_outputs"]["json"] = schema
    return rows


def response_record(row, raw, tokenizer):
    return target.response_record({**row, "arm": "full"}, raw, tokenizer)


@functools.lru_cache(maxsize=1)
def wire_send():
    import adaptive_metrics

    aliases = {"target_study": sys.modules[__name__], "metrics": adaptive_metrics}
    previous = {key: sys.modules.get(key) for key in aliases}
    sys.modules.update(aliases)
    try:
        module = prior.load("adaptive_existing_target_wire_sender", TARGET / "owner.py")
    finally:
        for key, value in previous.items():
            if value is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = value
    return module.send


def attest(service_directory):
    result = prior.attest(service_directory)
    configuration = Path(read(service_directory / "SERVER_START.json")["command"][-1])
    bound = context_bound(schedule(), read(configuration)["vllm"]["max_model_len"])
    if bound != read(ROOT / "MANIFEST.json")["context_bound"]:
        raise ValueError("actual context differs from frozen bound")
    result["context_bound"] = bound
    return result


def verify():
    ready = read(ROOT / "READY.json")
    if ready["status"] != "CPU_READY_MAIN_REVIEW_REQUIRED":
        raise ValueError("unexpected READY status")
    for path, expected in ready["closure_sha256"].items():
        if sha(path) != expected:
            raise ValueError("sealed source changed: " + path)
    if digest(schedule()) != ready["schedule_sha256"]:
        raise ValueError("component inventory changed")
    return ready
