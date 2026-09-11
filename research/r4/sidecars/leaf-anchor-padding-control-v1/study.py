"""Frozen meaningful-tag versus placeholder control; private qualified helpers."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
GRAMMAR = SIDE / "leaf-indexed-grammar-transfer-v1"
PINS = {
    GRAMMAR / "study.py": "861fae26e0b5bc6855b80c20a459cd1526e4bfd49b4e83fb3a380abb4a161487",
    GRAMMAR / "driver.py": "17d46458875e2fdbb3f03d951ef6659ae54165cb3d420b5f4678886eb1857f67",
    GRAMMAR / "DATA.json": "ca5a895f361d8a590078e36393c6edf900e86a6da7b17382440366581642e17f",
    GRAMMAR / "SPEC.json": "c9bdead579cc6da8ae5910835f6c4742f2f1ed0121c42afcd397be1bc99e7f3b",
}
for path, expected in PINS.items():
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError("qualified source changed: " + str(path))
loader = importlib.util.spec_from_file_location("padding_private_grammar", GRAMMAR / "study.py")
grammar = importlib.util.module_from_spec(loader)
loader.loader.exec_module(grammar)
anchor = grammar.anchor
read, digest, file_hash, serialize, write_once = anchor.read, anchor.digest, anchor.file_hash, anchor.serialize, anchor.write_once
INPUT_MARKER = anchor.INPUT_MARKER
SEEDS = [981264101, 981264102]
ARMS = ["anonymous", "indexed", "meaningful_tag", "placeholder_tag"]
WEIGHTS = ["old_sft"]
ALIAS = "strict-rlm-qwen3-4b-role-sft-selected-v1"


def select_data(source):
    contexts = [c for c in source["contexts"] if c["dataset"] == "trec"][:4]
    contexts += [c for c in source["contexts"] if c["dataset"] == "sst2"]
    if len(contexts) != 8 or any(len(c["records"]) != 64 for c in contexts):
        raise ValueError("expected four TREC and four SST64 contexts")
    contexts = deepcopy(contexts)
    for index, c in enumerate(contexts):
        c["grammar_context_index"] = c["index"]
        c["index"] = index
        if any(r["id"] == "q0000" for r in c["records"]):
            raise ValueError("placeholder must not be an input ID")
    return {"contexts": contexts, "sampling_seeds": SEEDS,
        "source_path": str(GRAMMAR / "DATA.json"), "source_sha256": PINS[GRAMMAR / "DATA.json"],
        "selection": "First four declared TREC contexts and all four SST contexts; exact records/order/IDs retained; labels and outcomes unused",
        "freshness": "Developmental/exposed following grammar160; not new independent test data",
        "source_provenance": {k: source[k] for k in ["sst_provenance", "trec_provenance"]}}


def load_data():
    return select_data(read(GRAMMAR / "DATA.json"))


def build_design(data):
    previous = read(GRAMMAR / "SPEC.json")["design"]
    d = {k: deepcopy(previous[k]) for k in ["contract", "labels", "definitions", "task_labels", "task_definitions"]}
    d.update(contexts=deepcopy(data["contexts"]), model_alias=ALIAS, model_aliases={"old_sft": ALIAS},
        max_tokens=3072, max_concurrent_calls=4, call_timeout_seconds=120, wall_time_cap_seconds=900,
        plan=[], coordinates=[], batches=[])
    cells = [(a, g) for a in ARMS for g in ["free", "exact"]]
    for c in d["contexts"]:
        for repeat, seed in enumerate(SEEDS):
            shift = (c["index"] * 2 + repeat) % 8
            for position, (arm, mode) in enumerate(cells[shift:] + cells[:shift]):
                row = {"dataset": c["dataset"], "context_index": c["index"], "source_context_id": c["source_context_id"],
                    "weight": "old_sft", "arm": arm, "grammar": mode, "seed": seed, "repeat": repeat,
                    "size": 64, "permutation": 0, "start": 0, "cell_order": position,
                    "batch_id": len(d["batches"]), "dispatch_order": len(d["plan"])}
                row["id"] = digest([ROOT.name, row])
                row["coordinate_id"] = row["id"]
                d["plan"].append(row)
                d["coordinates"].append(deepcopy(row))
                d["batches"].append({"questions": [r["question"] for r in c["records"]],
                    "gold": {"records": deepcopy(c["records"]), "order": list(range(64)), "arm": arm,
                             "labels": d["task_labels"][c["dataset"]]}})
    return d


def make_request(design, row):
    body = anchor.make_request(design, row)
    if row["arm"] not in ARMS:
        raise ValueError("unknown representation")
    if row["arm"] in ["meaningful_tag", "placeholder_tag"]:
        records = design["batches"][row["batch_id"]]["gold"]["records"]
        original = body["messages"][1]["content"]
        prefix, rest = original.split("Return only", 1)
        rest = rest.split("\nAllowed labels:", 1)[1]
        instruction = "Return only a JSON array of objects in input order, exactly one object per input ID. Each object has exactly the keys tag then label. "
        instruction += ("Set tag to the corresponding input ID and label to its label." if row["arm"] == "meaningful_tag"
                        else 'Set tag to the literal "q0000" in every object and label to the corresponding input record\'s label. The tag is task-irrelevant and is not an input ID.')
        body["messages"][1]["content"] = prefix + instruction + "\nAllowed labels:" + rest
        items = [{"type": "object", "properties": {
                    "tag": {"type": "string", "const": r["id"] if row["arm"] == "meaningful_tag" else "q0000"},
                    "label": {"type": "string", "enum": design["task_labels"][row["dataset"]]}},
                  "required": ["tag", "label"], "additionalProperties": False} for r in records]
        body["structured_outputs"] = {"json": {"type": "array", "prefixItems": items,
            "items": False, "minItems": len(records), "maxItems": len(records)}}
    if row["grammar"] == "free":
        body.pop("structured_outputs")
    elif row["grammar"] != "exact":
        raise ValueError("unknown decoding mode")
    return body


def synthetic_output(records, arm, label):
    if arm == "anonymous":
        return [label for _ in records]
    if arm == "indexed":
        return {r["id"]: label for r in records}
    return [{"tag": r["id"] if arm == "meaningful_tag" else "q0000", "label": label} for r in records]


def score_labels(content, gold):
    n = len(gold["records"])
    if gold["arm"] in ["anonymous", "indexed"]:
        score = anchor.score_labels(content, gold)
        if score["schema_valid"]:
            return score
        reason = score["parse_status"] if score["parse_status"] != "aligned" else "noncanonical_label"
        raw_length = score["raw_array_length"]
    else:
        raw = None
        try:
            raw = json.loads(content, object_pairs_hook=anchor.corr.strict_object,
                             parse_constant=anchor.corr.reject_constant)
            if not isinstance(raw, list) or len(raw) != n:
                raise ValueError("wrong_cardinality_or_representation")
            for item, record in zip(raw, gold["records"], strict=True):
                expected = record["id"] if gold["arm"] == "meaningful_tag" else "q0000"
                if not isinstance(item, dict) or set(item) != {"tag", "label"}:
                    raise ValueError("wrong_object_shape")
                if item["tag"] != expected:
                    raise ValueError("wrong_tag_or_order")
                if not isinstance(item["label"], str) or item["label"] not in gold["labels"]:
                    raise ValueError("noncanonical_label")
            predictions = [x["label"] for x in raw]
            return {"parse_status": "aligned", "raw_array_length": n, "schema_valid": True,
                "records": n, "aligned_records": n, "predictions": predictions,
                "strict_correct": sum(p == r["gold_label"] for p, r in zip(predictions, gold["records"], strict=True)),
                "noncanonical_labels": 0, "output_positions": list(range(1, n + 1)), "input_positions": list(range(1, n + 1))}
        except (ValueError, TypeError) as error:
            reason = str(error)
            raw_length = len(raw) if isinstance(raw, list) else None
    return {"parse_status": reason, "raw_array_length": raw_length, "schema_valid": False,
        "records": n, "aligned_records": 0, "predictions": [None] * n, "strict_correct": 0,
        "noncanonical_labels": int(reason == "noncanonical_label"), "output_positions": [None] * n,
        "input_positions": list(range(1, n + 1))}


def score_coordinate(design, coordinate, records):
    if len(records) > 1:
        raise ValueError("duplicate coordinate outcome")
    result = grammar.score_coordinate(design, coordinate, records)
    observed = result["complete"] and result["infrastructure_errors"] == 0
    result["strict_correct_assignments"] = result["canonical_correct"] if observed else None
    result["semantic_correct_among_aligned"] = result["canonical_correct"] if result["aligned_records"] == 64 else None
    return result


def summarize(design, records):
    out = {"coordinates": [score_coordinate(design, c, [r for r in records if r["coordinate"]["id"] == c["id"]]) for c in design["coordinates"]]}
    cells = []
    for dataset in ["trec", "sst2"]:
        for arm in ARMS:
            for mode in ["free", "exact"]:
                selected = [r for r in out["coordinates"] if (r["coordinate"]["dataset"], r["coordinate"]["arm"], r["coordinate"]["grammar"]) == (dataset, arm, mode)]
                aligned = [i for r in selected for i in r["records"] if i["aligned"]]
                cells.append({"dataset": dataset, "arm": arm, "grammar": mode,
                    "planned_calls": len(selected), "recorded_calls": sum(r["complete"] for r in selected),
                    "observable_calls": sum(r["strict_correct_assignments"] is not None for r in selected),
                    "valid_calls": sum(r["fully_valid"] for r in selected),
                    "complete_batch_correct": sum(r["strict_full64_correct"] == 1 for r in selected),
                    "planned_assignments": 64 * len(selected), "aligned_assignments": len(aligned),
                    "canonical_correct": sum(i["correct"] for i in aligned),
                    "position_accuracy": [{"position": p, "aligned": sum(i["input_position"] == p for i in aligned),
                        "correct": sum(i["input_position"] == p and i["correct"] for i in aligned)} for p in range(1, 65)],
                    "gold_counts_aligned": dict(Counter(i["gold"] for i in aligned)),
                    "prediction_counts_aligned": dict(Counter(i["prediction"] for i in aligned)),
                    "confusion": [{"gold": g, "prediction": p, "count": n} for (g, p), n in sorted(Counter((i["gold"], i["prediction"]) for i in aligned).items())],
                    "usage": {k: sum(r["usage"][k] for r in selected) for k in ["logical_input_tokens", "cached_input_tokens", "uncached_input_tokens", "completion_tokens"]},
                    "missing_usage": {k: sum(r["missing_usage"][k] for r in selected) for k in ["logical_input_tokens", "cached_input_tokens", "uncached_input_tokens", "completion_tokens"]},
                    "length_stops": sum(r["length_stops"] for r in selected),
                    "call_wall_seconds_sum": sum(r["call_wall_seconds_sum"] for r in selected)})
    grouped = defaultdict(dict)
    for r in out["coordinates"]:
        c = r["coordinate"]
        grouped[c["dataset"], c["context_index"], c["repeat"], c["grammar"]][c["arm"]] = r
    pairs = []
    for key, arms in grouped.items():
        if not {"meaningful_tag", "placeholder_tag"} <= arms.keys():
            continue
        a, b = arms["meaningful_tag"], arms["placeholder_tag"]
        observed = all(x["strict_correct_assignments"] is not None for x in [a, b])
        pairs.append({"dataset": key[0], "context_index": key[1], "repeat": key[2], "grammar": key[3],
            "both_observed": observed, "jointly_valid": a["fully_valid"] and b["fully_valid"],
            "meaningful_minus_placeholder_correct": a["strict_correct_assignments"] - b["strict_correct_assignments"] if observed else None})
    out.update(cells=cells, paired_context_effects=pairs,
        inference_unit="Four source contexts per task; seeds and cells are nested; TREC/SST reported separately",
        failure_caution="Invalid complete output yields zero strict correct assignments, with unavailable semantic alignment; not 64 established semantic mistakes. Infrastructure/unrun strict scores stay null.",
        compute_caution="Matched synthetic structure/token lengths do not imply equal realized compute or neutral padding; preserve actual usage.")
    return out


# Private imported module graph only; never modifies qualified files or active processes.
anchor.corr.fixed.make_request = make_request
anchor.corr.fixed.score_coordinate = score_coordinate
anchor.corr.fixed.leaf.score_labels = score_labels
anchor.corr.fixed.leaf.write_once = write_once
collect_calls = anchor.corr.fixed.collect_calls
