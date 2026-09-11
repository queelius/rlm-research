"""Free-versus-exact output decoding on the frozen fresh96 correspondence inputs."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
SOURCE = SIDE / "leaf-fresh-correspondence-v1"
SOURCE_STUDY_SHA256 = "7d23d89907645c66fedfedeff408ab7797d0887004d162722a3d58d24f49140b"
SOURCE_DATA_SHA256 = "1f8205546dbdc635bb54a6e90e1c92f733997110eb380bf7b0d109d5222fb4a6"
SOURCE_SPEC_SHA256 = "9e0618c5714b82374328e7679acf65dd8bdd691f1edfd83e072b4281930ec580"
ARMS = ("matching", "constant", "plain")
DECODERS = ("free", "exact")
MODEL = "qwen3"


def sha(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


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


def source_module():
    if sha(SOURCE / "study.py") != SOURCE_STUDY_SHA256:
        raise ValueError("frozen fresh96 study changed")
    spec = importlib.util.spec_from_file_location("free_id_pinned_fresh96", SOURCE / "study.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SOURCE_MODULE = source_module()
MODELS = {MODEL: deepcopy(SOURCE_MODULE.MODELS[MODEL])}
SEEDS = tuple(SOURCE_MODULE.SEEDS)


def build_data():
    if (ROOT / "DATA.json").exists():
        value = read(ROOT / "DATA.json")
    else:
        if sha(SOURCE / "DATA.json") != SOURCE_DATA_SHA256:
            raise ValueError("frozen fresh96 data changed")
        source = read(SOURCE / "DATA.json")
        value = {
            "schema": "leaf-free-id-correspondence-data-v1",
            "source_data_path": str(SOURCE / "DATA.json"),
            "source_data_sha256": SOURCE_DATA_SHA256,
            "contexts": deepcopy(source["contexts"]),
            "exposure": "Exact frozen fresh96 AG/SST contexts; reused and explicitly exposed.",
        }
    if len(value["contexts"]) != 8:
        raise ValueError("expected eight frozen fresh96 contexts")
    counts = Counter(c["dataset"] for c in value["contexts"])
    if counts != {"agnews": 4, "sst2": 4}:
        raise ValueError("expected four AG and four SST contexts")
    return value


def _source_design(data):
    return SOURCE_MODULE.build_design({"contexts": deepcopy(data["contexts"])})


def build_design(data):
    source_design = _source_design(data)
    source_rows = [r for r in source_design["plan"] if r["model"] == MODEL]
    plan = []
    batches = []
    for old_row in source_rows:
        order = DECODERS if (old_row["batch_id"] % 2 == 0) else tuple(reversed(DECODERS))
        for decoder in order:
            row = {
                **{k: v for k, v in old_row.items() if k not in {"id", "coordinate_id", "batch_id", "dispatch_order"}},
                "decoder": decoder,
                "source_coordinate_id": old_row["id"],
                "batch_id": len(batches),
                "dispatch_order": len(plan),
            }
            row["id"] = row["coordinate_id"] = digest([ROOT.name, row])
            context = data["contexts"][row["context_index"]]
            batches.append(
                {
                    "gold": {
                        "records": deepcopy(context["records"]),
                        "labels": list(context["labels"]),
                        "arm": row["arm"],
                    }
                }
            )
            plan.append(row)
    if len(plan) != 96:
        raise ValueError("exact 96-call factorial required")
    return {
        "contexts": deepcopy(data["contexts"]),
        "plan": plan,
        "coordinates": deepcopy(plan),
        "batches": batches,
        "max_concurrent_calls": 4,
        "call_timeout_seconds": 120,
        "wall_time_cap_seconds": 1500,
        "owned_outer_cap_seconds": 1800,
        "max_tokens": 3072,
    }


def _source_request(design, row):
    source_design = _source_design({"contexts": design["contexts"]})
    source_row = next(r for r in source_design["plan"] if r["id"] == row["source_coordinate_id"])
    return SOURCE_MODULE.make_request(source_design, source_row)


def make_request(design, row):
    body = deepcopy(_source_request(design, row))
    if row["decoder"] == "free":
        body.pop("structured_outputs")
    elif row["decoder"] != "exact":
        raise ValueError("unknown decoder")
    return body


def _strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key")
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError("nonfinite_json_constant:" + value)


def score_missing(gold):
    n = len(gold["records"])
    return {
        "observed_policy_output": False,
        "full_shape_valid": None,
        "strict_correct_planned_denominator": None,
        "planned_correct_bounds": [0, n],
        "conditional_correct": None,
        "conditional_aligned_records": 0,
        "predictions": [None] * n,
        "parse_status": "infrastructure_missing",
        "field_order_valid": None,
        "emitted_id_position_matches": None,
        "emitted_id_set_coverage": None,
        "duplicate_emitted_ids": None,
        "missing_input_ids": None,
        "extra_emitted_ids": None,
        "constant_tag_matches": None,
    }


def score_content(content, gold):
    n = len(gold["records"])
    base = score_missing(gold)
    base.update(observed_policy_output=True, planned_correct_bounds=[0, 0])
    try:
        raw = json.loads(content, object_pairs_hook=_strict_object, parse_constant=_reject_constant)
    except (ValueError, TypeError, json.JSONDecodeError) as error:
        base.update(full_shape_valid=False, strict_correct_planned_denominator=0,
                    parse_status="json:" + str(error))
        return base
    if not isinstance(raw, list) or len(raw) != n:
        base.update(full_shape_valid=False, strict_correct_planned_denominator=0,
                    parse_status="array_or_cardinality")
        return base

    labels = []
    tags = []
    field_order = True
    label_only = True
    full_shape = True
    for item in raw:
        if gold["arm"] == "plain":
            label = item
            if not isinstance(label, str) or label not in gold["labels"]:
                label_only = full_shape = False
            labels.append(label if isinstance(label, str) else None)
            continue
        if not isinstance(item, dict):
            labels.append(None)
            tags.append(None)
            label_only = full_shape = False
            continue
        field_order = field_order and list(item) == ["tag", "label"]
        label = item.get("label")
        tag = item.get("tag")
        if not isinstance(label, str) or label not in gold["labels"]:
            label_only = False
        if set(item) != {"tag", "label"} or not isinstance(tag, str):
            full_shape = False
        labels.append(label if isinstance(label, str) else None)
        tags.append(tag if isinstance(tag, str) else None)
    full_shape = full_shape and label_only
    conditional = (
        sum(label == record["gold_label"] for label, record in zip(labels, gold["records"], strict=True))
        if label_only
        else None
    )
    base.update(
        full_shape_valid=full_shape,
        strict_correct_planned_denominator=conditional if full_shape else 0,
        planned_correct_bounds=[conditional if full_shape else 0, conditional if full_shape else 0],
        conditional_correct=conditional,
        conditional_aligned_records=n if label_only else 0,
        predictions=labels if label_only else [None] * n,
        parse_status="aligned" if full_shape else "invalid_object_or_label_shape",
        field_order_valid=field_order if gold["arm"] != "plain" else None,
    )
    if gold["arm"] == "matching" and len(tags) == n:
        expected = [r["id"] for r in gold["records"]]
        actual = [tag for tag in tags if isinstance(tag, str)]
        counts = Counter(actual)
        base.update(
            emitted_id_position_matches=sum(a == b for a, b in zip(tags, expected, strict=True)),
            emitted_id_set_coverage=len(set(actual) & set(expected)),
            duplicate_emitted_ids=sorted(k for k, v in counts.items() if v > 1),
            missing_input_ids=sorted(set(expected) - set(actual)),
            extra_emitted_ids=sorted(set(actual) - set(expected)),
        )
    elif gold["arm"] == "constant" and len(tags) == n:
        base["constant_tag_matches"] = sum(tag == "p0000" for tag in tags)
    return base


def summarize(design, records):
    by_id = {r["coordinate"]["id"]: r for r in records}
    coordinates = []
    for row in design["coordinates"]:
        record = by_id.get(row["id"])
        score = record.get("score") if record else None
        gold = design["batches"][row["batch_id"]]["gold"]
        if score is None:
            score = score_missing(gold)
        coordinates.append(
            {
                "coordinate": row,
                "recorded": record is not None,
                "model_completed": bool(record and record.get("model_completed")),
                "policy_output_observed": score["observed_policy_output"],
                "score": score,
                "finish_reason": record.get("finish_reason") if record else None,
                "usage": record.get("usage", {}) if record else {},
                "error": record.get("error") if record else None,
            }
        )
    cells = []
    for task in ("agnews", "sst2"):
        for arm in ARMS:
            for decoder in DECODERS:
                selected = [x for x in coordinates if (x["coordinate"]["dataset"], x["coordinate"]["arm"],
                            x["coordinate"]["decoder"]) == (task, arm, decoder)]
                values = [x["score"]["strict_correct_planned_denominator"] for x in selected]
                observed = [v for v in values if v is not None]
                missing = len(values) - len(observed)
                cells.append({
                    "dataset": task,
                    "arm": arm,
                    "decoder": decoder,
                    "planned_calls": len(selected),
                    "observed_policy_outputs": sum(x["policy_output_observed"] for x in selected),
                    "full_shape_valid": sum(x["score"]["full_shape_valid"] is True for x in selected),
                    "strict_correct_observed_sum": sum(observed),
                    "strict_correct_planned_bounds": [sum(observed), sum(observed) + missing * 64],
                    "infrastructure_nulls": missing,
                })
    return {
        "schema": "leaf-free-id-correspondence-analysis-v1",
        "coordinates": coordinates,
        "cells": cells,
        "scoring": "Completed invalid policy output contributes zero strict labels; infrastructure missing is NULL with bounds. No ID reordering or answer repair.",
        "sampling_unit": "Four explicitly reused fresh96 contexts per task; two nested seeds.",
    }

