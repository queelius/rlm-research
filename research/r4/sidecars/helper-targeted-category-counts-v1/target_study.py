"""Frozen targeted requests, local schema validation, and sealed native seams."""

import copy
import functools
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIZE = ROOT.parent / "helper-unseen-size-comparison-v1"
spec = importlib.util.spec_from_file_location("targeted_sealed_size_seams", SIZE / "size_study.py")
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
read, write, sha, digest = prior.read, prior.write, prior.sha, prior.digest
NATIVE, MODEL, CHILD_ALIAS = prior.NATIVE, prior.MODEL, prior.CHILD_ALIAS
PANEL, SERVICE, CONTEXT_SOURCE = prior.PANEL, prior.SERVICE, prior.CONTEXT_SOURCE
source, dependencies = prior.source, prior.dependencies
ATTEMPT = ROOT / "outputs/attempt-001"
CAP, CALLS, PREDICTIONS = 900, 96, 1536


@functools.lru_cache(maxsize=1)
def make_schedule():
    from transformers import AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(MODEL, local_files_only=True)
    full_rows = {
        (row["dataset"], row["block"]): row
        for row in prior.make_schedule()
        if row["batch_size"] == 16
    }
    rows = []
    for block in range(8):
        datasets = ("trec", "ag_news") if block % 2 == 0 else ("ag_news", "trec")
        for dataset in datasets:
            full = full_rows[(dataset, block)]
            labels = json.loads(full["schema_ordered_json"])["properties"][full["ids"][0]]["enum"]
            targets = labels[block % len(labels) :] + labels[: block % len(labels)]
            targets.insert(block % (len(labels) + 1), None)
            needle = tokenizer.encode(full["request_text"], add_special_tokens=False)
            original = full["body"]["token_ids"]
            hits = [
                i
                for i in range(len(original) - len(needle) + 1)
                if original[i : i + len(needle)] == needle
            ]
            if len(hits) != 1:
                raise ValueError("full prompt wrapper has ambiguous token subsequence")
            prefix, suffix = original[: hits[0]], original[hits[0] + len(needle) :]
            for target in targets:
                row = copy.deepcopy(full)
                row.update(
                    arm="full" if target is None else "targeted",
                    target=target,
                    labels=labels,
                    call_id=digest([ROOT.name, dataset, block, target]),
                )
                allowed = labels if target is None else [target, "other"]
                if target is not None:
                    complement = [label for label in labels if label != target]
                    cue = (
                        f"\nTarget category: {json.dumps(target)}. For this request, return the "
                        "target label only when the record belongs to that category under the "
                        "complete definitions above. Return `other` for every remaining category; "
                        f"`other` is the union of {json.dumps(complement, separators=(',', ':'))}, "
                        "not an additional semantic category. Return one keyed answer for every "
                        "supplied record."
                    )
                    old = "Allowed labels: " + json.dumps(labels, separators=(",", ":"))
                    new = "Allowed labels: " + json.dumps(allowed, separators=(",", ":"))
                    marker = "\nReturn only one JSON object"
                    if row["request_text"].count(old) != 1 or marker not in row["request_text"]:
                        raise ValueError("frozen prompt output convention changed")
                    row["request_text"] = (
                        row["request_text"].replace(old, new).replace(marker, cue + marker, 1)
                    )
                    row["body"]["token_ids"] = (
                        prefix
                        + tokenizer.encode(row["request_text"], add_special_tokens=False)
                        + suffix
                    )
                schema = {
                    "type": "object",
                    "properties": {
                        identifier: {"type": "string", "enum": allowed} for identifier in row["ids"]
                    },
                    "required": row["ids"],
                    "additionalProperties": False,
                }
                row["schema_ordered_json"] = json.dumps(schema, separators=(",", ":"))
                row["body"]["sampling_params"]["structured_outputs"]["json"] = schema
                row["body"]["sampling_params"]["seed"] = 202609120820 + (dataset == "ag_news")
                rows.append(row)
    if len(rows) != CALLS or sum(len(row["ids"]) for row in rows) != PREDICTIONS:
        raise ValueError("wrong96/1536 schedule")
    return rows


def schedule():
    rows = read(ROOT / "inputs/SCHEDULE.json")
    for row in rows:
        schema = json.loads(row["schema_ordered_json"])
        if list(schema["properties"]) != row["ids"] or schema["required"] != row["ids"]:
            raise ValueError("schema key order differs")
        row["body"]["sampling_params"]["structured_outputs"]["json"] = schema
    return rows


def context_bound(rows, limit):
    maximum = max(len(row["body"]["token_ids"]) for row in rows)
    if any(row["body"]["sampling_params"]["max_tokens"] != 1024 for row in rows):
        raise ValueError("unchanged output cap required")
    if maximum + 1024 > limit:
        raise ValueError("request exceeds context bound")
    return {
        "maximum_prompt_tokens": maximum,
        "maximum_prompt_plus_output_tokens": maximum + 1024,
        "service_max_model_len": limit,
        "output_token_cap": 1024,
        "all_requests_fit": True,
    }


def response_record(row, raw, tokenizer):
    if len(raw.get("choices", [])) != 1 or not raw.get("request_id"):
        raise ValueError("native response identity differs")
    if raw.get("model") != CHILD_ALIAS:
        raise ValueError("native alias differs")
    choice, usage = raw["choices"][0], raw["usage"]
    ids = choice["token_ids"]
    if not isinstance(ids, list) or any(type(value) is not int or value < 0 for value in ids):
        raise ValueError("invalid completion token inventory")
    if any(
        type(usage.get(key)) is not int or usage[key] < 0
        for key in ("prompt_tokens", "completion_tokens")
    ):
        raise ValueError("invalid native usage counts")
    if usage["prompt_tokens"] != len(row["body"]["token_ids"]) or (
        usage["completion_tokens"] != len(ids)
    ):
        raise ValueError("native physical token inventory differs")
    text = tokenizer.decode(ids, skip_special_tokens=True)
    result = {
        "request_id": raw["request_id"],
        "model": raw["model"],
        "finish_reason": choice.get("finish_reason"),
        "completion_ids": ids,
        "decoded_text": text,
        "prompt_tokens": usage["prompt_tokens"],
        "completion_tokens": usage["completion_tokens"],
        "cached_prompt_tokens": usage.get("prompt_tokens_details", {}).get("cached_tokens"),
        "raw_response_sha256": digest(raw),
    }
    try:
        if not isinstance(json.loads(text), dict):
            raise ValueError("JSON object required, not an array of pairs")
        pairs = json.loads(text, object_pairs_hook=list)
        if not isinstance(pairs, list) or [pair[0] for pair in pairs] != row["ids"]:
            raise ValueError("exact ordered keys required, including no duplicates")
        allowed = row["labels"] if row["arm"] == "full" else [row["target"], "other"]
        if any(pair[1] not in allowed for pair in pairs) or choice.get("finish_reason") != "stop":
            raise ValueError("noncanonical label or non-stop finish")
        result.update(status="returned_valid", prediction=dict(pairs))
    except Exception as error:
        result.update(status="invalid_response", prediction={}, validation_error=str(error))
    return result


def attest(service_directory):
    # The inherited check verifies identical8192 limit and exact v4 pre-exec evidence.
    result = prior.attest(service_directory)
    bound = read(ROOT / "MANIFEST.json")["context_bound"]
    configuration = Path(read(service_directory / "SERVER_START.json")["command"][-1])
    if read(configuration)["vllm"]["max_model_len"] != bound["service_max_model_len"]:
        raise ValueError("actual service context changed")
    context_bound(schedule(), bound["service_max_model_len"])
    result["context_bound"] = bound
    return result


def engine_marker(service_directory):
    path = service_directory / "inference.log"
    lines = path.read_text(errors="replace").splitlines() if path.exists() else []
    matches = [
        line
        for line in lines
        if re.search(r"\(EngineCore[^)]*pid=\d+\)", line) and "batch_invariant.py" in line
    ]
    return {
        "verified": bool(matches),
        "log": str(path),
        "log_sha256": sha(path) if path.exists() else None,
        "matching_lines": matches,
        "meaning": "actual EngineCore trace enters batch-invariant module; not quality evidence",
    }


def verify():
    ready = read(ROOT / "READY.json")
    if ready["status"] != "CPU_READY_MAIN_REVIEW_REQUIRED":
        raise ValueError("unexpected READY status")
    for path, expected in ready["closure_sha256"].items():
        if sha(path) != expected:
            raise ValueError("sealed source changed: " + path)
    if digest(schedule()) != ready["schedule_sha256"]:
        raise ValueError("schedule identity changed")
    return ready
