"""Gold-free companion/order schedule and sealed native wire/token seams."""

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
    "companion_sealed_target_seams", TARGET / "target_study.py"
)
target = importlib.util.module_from_spec(spec)
spec.loader.exec_module(target)
prior = target.prior
read, write, sha, digest = prior.read, prior.write, prior.sha, prior.digest
NATIVE, MODEL, CHILD_ALIAS = prior.NATIVE, prior.MODEL, prior.CHILD_ALIAS
PANEL, SERVICE, CONTEXT_SOURCE = prior.PANEL, prior.SERVICE, prior.CONTEXT_SOURCE
source, dependencies = prior.source, prior.dependencies
context_bound, engine_marker = target.context_bound, target.engine_marker
CAP, CALLS, PREDICTIONS = 900, 64, 1024
ARMS = ("original", "reverse", "neighbor_A", "neighbor_B")
ATTEMPT = ROOT / "outputs/attempt-001"


@functools.lru_cache(maxsize=1)
def make_schedule():
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(MODEL, local_files_only=True)
    _, _, public, _, requests = source().panel()
    first = requests[0]
    tokens = first["body_template"]["token_ids"]
    needle = tokenizer.encode(first["request_text"], add_special_tokens=False)
    hits = [
        i for i in range(len(tokens) - len(needle) + 1) if tokens[i : i + len(needle)] == needle
    ]
    if len(hits) != 1:
        raise ValueError("frozen request wrapper is not unambiguous")
    prefix, suffix = tokens[: hits[0]], tokens[hits[0] + len(needle) :]
    matrix, permutations, old_coordinates = {}, {}, {}
    for dataset in ("trec", "ag_news"):
        records = [row for row in public["records"] if row["dataset"] == dataset]
        if len(records) != 128:
            raise ValueError("wrong public dataset inventory")
        matrix[dataset] = [records[i : i + 16] for i in range(0, 128, 16)]
        old_coordinates.update(
            {row["id"]: (dataset, index // 16, index % 16) for index, row in enumerate(records)}
        )
        for arm in ARMS[2:]:
            for column in range(16):
                namespace = f"helper-companion-position-v1|202609120932|{dataset}|{arm}|{column}"
                order = list(range(8))
                random.Random(int(hashlib.sha256(namespace.encode()).hexdigest(), 16)).shuffle(
                    order
                )
                permutations[(dataset, arm, column)] = order
    rows = []
    for block in range(8):
        datasets = ("trec", "ag_news") if block % 2 == 0 else ("ag_news", "trec")
        for dataset in datasets:
            dataset_index = int(dataset == "ag_news")
            shift = (block + dataset_index) % 4
            for arm in ARMS[shift:] + ARMS[:shift]:
                if arm == "original":
                    selected = matrix[dataset][block]
                elif arm == "reverse":
                    selected = matrix[dataset][block][::-1]
                else:
                    selected = [
                        matrix[dataset][permutations[(dataset, arm, column)][block]][column]
                        for column in range(16)
                    ]
                request_text, labels = prior.builder().prompt(dataset, selected)
                ids = [record["id"] for record in selected]
                schema = {
                    "type": "object",
                    "properties": {
                        identifier: {"type": "string", "enum": labels} for identifier in ids
                    },
                    "required": ids,
                    "additionalProperties": False,
                }
                body = copy.deepcopy(first["body_template"])
                body["model"] = CHILD_ALIAS
                body["token_ids"] = (
                    prefix + tokenizer.encode(request_text, add_special_tokens=False) + suffix
                )
                body["sampling_params"]["seed"] = 202609120930 + dataset_index
                body["sampling_params"]["structured_outputs"]["json"] = schema
                provenance = []
                for slot, identifier in enumerate(ids):
                    _, old_block, old_slot = old_coordinates[identifier]
                    old_companions = {record["id"] for record in matrix[dataset][old_block]} - {
                        identifier
                    }
                    new_companions = set(ids) - {identifier}
                    provenance.append(
                        {
                            "id": identifier,
                            "original_block": old_block,
                            "original_slot": old_slot,
                            "new_block": block,
                            "new_slot": slot,
                            "retained_companions": len(old_companions & new_companions),
                            "companion_jaccard": len(old_companions & new_companions)
                            / len(old_companions | new_companions),
                        }
                    )
                rows.append(
                    {
                        "call_id": digest([ROOT.name, dataset, block, arm]),
                        "dataset": dataset,
                        "block": block,
                        "start": block * 16,
                        "batch_size": 16,
                        "arm": arm,
                        "target": None,
                        "labels": labels,
                        "ids": ids,
                        "request_text": request_text,
                        "schema_ordered_json": json.dumps(schema, separators=(",", ":")),
                        "body": body,
                        "position_provenance": provenance,
                        "source_rows_by_column": [
                            permutations[(dataset, arm, column)][block] for column in range(16)
                        ]
                        if arm.startswith("neighbor")
                        else None,
                    }
                )
    if len(rows) != CALLS:
        raise ValueError("wrong64-call schedule")
    return rows


def schedule():
    rows = read(ROOT / "inputs/SCHEDULE.json")
    for row in rows:
        schema = json.loads(row["schema_ordered_json"])
        if list(schema["properties"]) != row["ids"] or schema["required"] != row["ids"]:
            raise ValueError("ordered schema inventory changed")
        row["body"]["sampling_params"]["structured_outputs"]["json"] = schema
    return rows


def response_record(row, raw, tokenizer):
    # Full-category validation for all four treatment names; no changes to the sealed validator.
    return target.response_record({**row, "arm": "full"}, raw, tokenizer)


@functools.lru_cache(maxsize=1)
def wire_send():
    import companion_metrics

    names = {"target_study": sys.modules[__name__], "metrics": companion_metrics}
    previous = {key: sys.modules.get(key) for key in names}
    sys.modules.update(names)
    try:
        module = prior.load("companion_existing_target_wire_sender", TARGET / "owner.py")
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
        raise ValueError("actual context cap differs from frozen manifest")
    result["context_bound"] = bound
    return result


def verify():
    ready = read(ROOT / "READY.json")
    if ready["status"] != "CPU_READY_MAIN_REVIEW_REQUIRED":
        raise ValueError("unexpected READY")
    for path, expected in ready["closure_sha256"].items():
        if sha(path) != expected:
            raise ValueError("sealed source changed: " + path)
    if digest(schedule()) != ready["schedule_sha256"]:
        raise ValueError("request schedule changed")
    return ready
