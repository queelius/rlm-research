"""Frozen primitives for the released-base role/tool/output-contract screen."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
SOURCE = SIDE / "leaf-free-id-correspondence-v1"
SOURCE_REQUESTS_SHA256 = "bc23e3cf1ff8aee85e4e51ad7663aab06f2f942afde017c08ad5df7e65faa48e"
MODEL = {
    "alias": "Qwen3-4B-Instruct-2507-no-research-adapter",
    "path": "/project/alex_phd/research-cache/models/Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554",
    "revision": "cdbee75f17c01a7cc42f958dc650907174af0554",
    "manifest_sha256": "19619b44b0bd30bf5debe0960e6dfd6acc5be8287c581727456aa5d17699c18f",
}
MASTER_SEED = 981309101
SAMPLE_SEED = 981309111
ROLES = ("coding", "classifier")
TOOLS = ("present", "absent")
ARMS = ("matching", "constant", "plain")
DECODERS = ("free", "exact")
INPUT_MARKER = "\nInput records (ID to text, in input order):\n"
CLASSIFIER_SYSTEM = (
    "You are a text classification assistant. Classify every supplied input record and return "
    "only the requested final answer in the requested format. Do not write code, use tools, "
    "provide explanations, or reason aloud."
)


def sha(path: str | Path) -> str:
    digestor = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digestor.update(chunk)
    return digestor.hexdigest()


def serialize(value) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def digest(value) -> str:
    return hashlib.sha256(serialize(value).encode()).hexdigest()


def read(path: str | Path):
    return json.loads(Path(path).read_text())


def write_once(path: str | Path, value) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as handle:
        json.dump(value, handle, ensure_ascii=False, separators=(",", ":"))
        handle.write("\n")


def group(text: str) -> str:
    normalized = " ".join(unicodedata.normalize("NFKC", text).casefold().split())
    return hashlib.sha256(normalized.encode()).hexdigest()


def choose(rows, excluded, dataset, n=128):
    groups = defaultdict(list)
    for row in rows:
        groups[group(row["text"])].append(row)
    conflicts = {key for key, values in groups.items() if len({v["label"] for v in values}) != 1}
    eligible = set(groups) - set(excluded) - conflicts
    ranked = sorted(eligible, key=lambda key: digest([MASTER_SEED, dataset, "selection", key]))
    if len(ranked) < n:
        raise ValueError("insufficient eligible groups")
    selected = []
    for key in ranked[:n]:
        source = min(groups[key], key=lambda row: row["index"])
        selected.append({**source, "group_id": key,
                         "source_row_indexes": sorted(row["index"] for row in groups[key]),
                         "selection_hash": digest([MASTER_SEED, dataset, "selection", key])})
    return selected, {"rows": len(rows), "groups": len(groups), "conflict_groups": sorted(conflicts),
                      "excluded_groups": sorted(set(groups) & set(excluded)),
                      "eligible_groups": len(eligible),
                      "selected_groups": [row["group_id"] for row in selected]}


def build_data():
    return read(ROOT / "DATA.json")


def _templates():
    path = SOURCE / "REQUESTS.json"
    if sha(path) != SOURCE_REQUESTS_SHA256:
        raise ValueError("qualified free-ID requests changed")
    requests = read(path)
    spec = read(SOURCE / "SPEC.json")
    by_id = {row["id"]: row for row in spec["design"]["plan"]}
    result = {}
    for request_id, body in requests.items():
        row = by_id[request_id]
        key = (row["dataset"], row["arm"])
        if key not in result:
            result[key] = deepcopy(body)
    if set(result) != {(dataset, arm) for dataset in ("agnews", "sst2") for arm in ARMS}:
        raise ValueError("missing qualified request templates")
    return result


def build_design(data):
    contexts = deepcopy(data["contexts"])
    if len(contexts) != 4 or Counter(c["dataset"] for c in contexts) != {"agnews": 2, "sst2": 2}:
        raise ValueError("expected two AG and two SST contexts")
    design = {"contexts": contexts, "plan": [], "coordinates": [], "batches": [],
              "max_concurrent_calls": 4, "call_timeout_seconds": 120,
              "wall_time_cap_seconds": 1500, "max_tokens": 3072}
    for context in contexts:
        if len(context["records"]) != 64 or len({r["group_id"] for r in context["records"]
                                                 if "group_id" in r}) not in (0, 64):
            raise ValueError("each context must contain 64 unique groups")
        cell = 0
        for role in ROLES:
            for tools in TOOLS:
                for arm in ARMS:
                    decoders = DECODERS if cell % 2 == 0 else tuple(reversed(DECODERS))
                    cell += 1
                    for decoder in decoders:
                        row = {"model": "qwen3", "weight": "released_base",
                               "dataset": context["dataset"], "context_index": context["index"],
                               "source_context_index": context["source_context_index"],
                               "system_role": role, "tools": tools, "arm": arm,
                               "decoder": decoder, "seed": SAMPLE_SEED, "size": 64,
                               "batch_id": len(design["batches"]),
                               "dispatch_order": len(design["plan"])}
                        row["id"] = row["coordinate_id"] = digest([ROOT.name, row])
                        gold = {"records": deepcopy(context["records"]),
                                "labels": list(context["labels"]), "arm": arm}
                        design["batches"].append({"gold": gold})
                        design["plan"].append(row)
                        design["coordinates"].append(deepcopy(row))
    if len(design["plan"]) != 96:
        raise ValueError("exact 96-call grid required")
    return design


def _schema(context, arm):
    items = []
    for record in context["records"]:
        if arm == "plain":
            item = {"type": "string", "enum": context["labels"]}
        else:
            item = {"type": "object", "properties": {
                "tag": {"type": "string", "const": record["id"] if arm == "matching" else "p0000"},
                "label": {"type": "string", "enum": context["labels"]}},
                "required": ["tag", "label"], "additionalProperties": False}
        items.append(item)
    return {"json": {"type": "array", "prefixItems": items, "items": False,
                     "minItems": 64, "maxItems": 64}}


def make_request(design, row):
    context = design["contexts"][row["context_index"]]
    body = deepcopy(_templates()[(row["dataset"], row["arm"])])
    prefix = body["messages"][1]["content"].split(INPUT_MARKER, 1)[0]
    body["messages"][1]["content"] = prefix + INPUT_MARKER + serialize(
        {record["id"]: record["question"] for record in context["records"]})
    if row["system_role"] == "classifier":
        body["messages"][0] = {"role": "system", "content": CLASSIFIER_SYSTEM}
    if row["tools"] == "absent":
        body.pop("tools", None)
        body.pop("parallel_tool_calls", None)
    body.update(model=MODEL["alias"], seed=row["seed"], temperature=0.5, top_p=1,
                top_k=-1, min_p=0, repetition_penalty=1, presence_penalty=0,
                frequency_penalty=0, max_tokens=3072,
                chat_template_kwargs={"enable_thinking": False})
    if row["decoder"] == "exact":
        body["structured_outputs"] = _schema(context, row["arm"])
    else:
        body.pop("structured_outputs", None)
    body["cache_salt"] = "leaf-role-tool-contract-v1"
    return body


def _strict_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate_json_key")
        value[key] = item
    return value


def _route(content):
    text = content or ""
    if re.search(r"<\/?tool(?:_call)?>|[\"']?name[\"']?\s*:\s*[\"']ipython", text, re.I):
        return "literal_tool_wrapper"
    if re.search(r"```|(?:^|\n)\s*(?:import |from \S+ import |def |%%bash|%pip|!python)", text):
        return "code_or_shell"
    return "final_text"


def score_missing(gold):
    n = len(gold["records"])
    return {"observed_policy_output": False, "full_shape_valid": None,
            "full_contract_valid": None, "strict_correct_planned_denominator": None,
            "planned_correct_bounds": [0, n], "conditional_positional_correct": None,
            "predictions": [None] * n, "parse_status": "infrastructure_missing",
            "route": None, "field_order_valid": None, "emitted_id_position_matches": None,
            "duplicate_emitted_ids": None, "missing_input_ids": None,
            "extra_emitted_ids": None, "constant_tag_matches": None}


def score_message(message, gold, finish_reason=None):
    n = len(gold["records"])
    base = score_missing(gold)
    base.update(observed_policy_output=True, strict_correct_planned_denominator=0,
                planned_correct_bounds=[0, 0])
    if message.get("tool_calls"):
        base.update(full_shape_valid=False, full_contract_valid=False,
                    parse_status="native_tool_call", route="native_tool_call")
        return base
    content = message.get("content")
    base["route"] = _route(content)
    try:
        raw = json.loads(content, object_pairs_hook=_strict_object,
                         parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
    except (ValueError, TypeError, json.JSONDecodeError) as error:
        base.update(full_shape_valid=False, full_contract_valid=False,
                    parse_status="json:" + str(error))
        return base
    if not isinstance(raw, list) or len(raw) != n:
        base.update(full_shape_valid=False, full_contract_valid=False,
                    parse_status="array_or_cardinality")
        return base
    labels, tags = [], []
    field_order = True
    shape = True
    for item in raw:
        if gold["arm"] == "plain":
            label = item
        elif isinstance(item, dict):
            field_order = field_order and list(item) == ["tag", "label"]
            shape = shape and set(item) == {"tag", "label"} and isinstance(item.get("tag"), str)
            tags.append(item.get("tag") if isinstance(item.get("tag"), str) else None)
            label = item.get("label")
        else:
            shape = False
            tags.append(None)
            label = None
        shape = shape and isinstance(label, str) and label in gold["labels"]
        labels.append(label if isinstance(label, str) else None)
    correct = sum(label == record["gold_label"]
                  for label, record in zip(labels, gold["records"], strict=True))
    expected = [record["id"] for record in gold["records"]]
    contract = shape
    if gold["arm"] == "matching":
        contract = contract and field_order and tags == expected
    elif gold["arm"] == "constant":
        contract = contract and field_order and tags == ["p0000"] * n
    base.update(full_shape_valid=shape, full_contract_valid=contract,
                strict_correct_planned_denominator=correct if contract else 0,
                planned_correct_bounds=[correct if contract else 0] * 2,
                conditional_positional_correct=correct if shape else None,
                predictions=labels if shape else [None] * n,
                parse_status="aligned_contract" if contract else "shape_or_contract_invalid",
                field_order_valid=field_order if gold["arm"] != "plain" else None)
    if gold["arm"] == "matching" and len(tags) == n:
        actual = [tag for tag in tags if isinstance(tag, str)]
        counts = Counter(actual)
        base.update(emitted_id_position_matches=sum(a == b for a, b in zip(tags, expected, strict=True)),
                    duplicate_emitted_ids=sorted(key for key, count in counts.items() if count > 1),
                    missing_input_ids=sorted(set(expected) - set(actual)),
                    extra_emitted_ids=sorted(set(actual) - set(expected)))
    elif gold["arm"] == "constant" and len(tags) == n:
        base["constant_tag_matches"] = sum(tag == "p0000" for tag in tags)
    return base


def summarize(design, records):
    by_id = {record["coordinate"]["id"]: record for record in records}
    coordinates = []
    for row in design["plan"]:
        record = by_id.get(row["id"])
        gold = design["batches"][row["batch_id"]]["gold"]
        score = record.get("score") if record else score_missing(gold)
        coordinates.append({"coordinate": row, "recorded": record is not None,
                            "model_completed": bool(record and record.get("model_completed")),
                            "score": score, "finish_reason": record.get("finish_reason") if record else None,
                            "usage": record.get("usage", {}) if record else {},
                            "provider_response_id": record.get("provider_response_id") if record else None,
                            "error": record.get("error") if record else None})
    cells = []
    for role in ROLES:
        for tools in TOOLS:
            for arm in ARMS:
                for decoder in DECODERS:
                    for dataset in ("agnews", "sst2"):
                        selected = [item for item in coordinates if
                                    (item["coordinate"]["system_role"], item["coordinate"]["tools"],
                                     item["coordinate"]["arm"], item["coordinate"]["decoder"],
                                     item["coordinate"]["dataset"]) ==
                                    (role, tools, arm, decoder, dataset)]
                        observed = [item["score"]["strict_correct_planned_denominator"] for item in selected
                                    if item["score"]["strict_correct_planned_denominator"] is not None]
                        missing = len(selected) - len(observed)
                        cells.append({"system_role": role, "tools": tools, "arm": arm,
                                      "decoder": decoder, "dataset": dataset, "planned": len(selected),
                                      "recorded": len(selected) - missing,
                                      "contract_valid": sum(item["score"]["full_contract_valid"] is True
                                                            for item in selected),
                                      "strict_correct": sum(observed),
                                      "strict_correct_bounds": [sum(observed), sum(observed) + missing * 64],
                                      "routes": dict(Counter(item["score"]["route"] for item in selected
                                                             if item["score"]["route"] is not None))})
    return {"schema": "leaf-role-tool-contract-analysis-v1", "coordinates": coordinates,
            "cells": cells, "sampling_unit": "two disjoint 64-record contexts per dataset; one paired seed",
            "scoring": "Completed invalid outputs are observed zero; infrastructure missing is NULL; no execution, reordering or repair."}
