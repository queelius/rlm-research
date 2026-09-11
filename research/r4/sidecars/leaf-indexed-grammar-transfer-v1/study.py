"""Fixed160-call design over qualified first-response leaf helpers; no GPU access."""
from __future__ import annotations

import hashlib
import importlib.util
from collections import Counter, defaultdict
from copy import deepcopy
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
ANCHOR = SIDE / "leaf-correspondence-anchor-transfer-v1"
ANCHOR_SOURCE_SHA = "5794187b8a6ab18a12103bd54a60bed8d55875e0292d74b2cfe082dbc9c02a00"
if hashlib.sha256((ANCHOR / "study.py").read_bytes()).hexdigest() != ANCHOR_SOURCE_SHA:
    raise ValueError("qualified anchor helper changed")
loader = importlib.util.spec_from_file_location("grammar_private_anchor_helpers", ANCHOR / "study.py")
anchor = importlib.util.module_from_spec(loader)
loader.loader.exec_module(anchor)
read, digest, file_hash, serialize, write_once = anchor.read, anchor.digest, anchor.file_hash, anchor.serialize, anchor.write_once
INPUT_MARKER = anchor.INPUT_MARKER
SEEDS = [981263401, 981263402]
WEIGHTS = ["old_sft", "indexed_final"]
INPUT_HASHES = {
    str(SIDE / "leaf-sentiment-transfer-v1/DATA.json"): "e3b929cab3e16296e6b92efceddca0a7a84fbec3455c569ec0e66c91cf30e9b8",
    str(ANCHOR / "DATA.json"): "0f37d7e4820e77f6057577cad3afa103957b3a99e8449fa7c03e53a19f4c4739",
    str(anchor.TREC_DATA): anchor.TREC_SHA,
    str(anchor.sst.CACHE / "validation.parquet"): "fb00fe008f6828f86ba2beda8415a4cf5da0c884f21c5f238c87131b5aa19529",
}


@lru_cache(maxsize=1)
def load_data():
    import pyarrow.parquet as pq
    anchor.sst.verify_hashes(INPUT_HASHES)
    earlier = read(SIDE / "leaf-sentiment-transfer-v1/DATA.json")
    prior_anchor = read(ANCHOR / "DATA.json")
    prior = [
        {r["group_id"] for r in earlier["selected"]},
        {r["group_id"] for c in prior_anchor["contexts"] if c["dataset"] == "sst2" for r in c["records"]},
    ]
    assert [len(x) for x in prior] == [256, 256] and not prior[0] & prior[1]
    assert prior[0] == {anchor.normalized_hash(r["sentence"]) for r in earlier["selected"]}
    assert prior[1] == {anchor.normalized_hash(r["question"]) for c in prior_anchor["contexts"] if c["dataset"] == "sst2" for r in c["records"]}
    rows = pq.read_table(anchor.sst.CACHE / "validation.parquet").to_pylist()
    _, dedup = anchor.sst.select_groups(rows)
    remaining = [r for r in dedup["all_groups_in_selection_order"] if r["group_id"] not in prior[0] | prior[1]]
    if len(remaining) < 256:
        raise ValueError("insufficient fresh SST groups; do not substitute reused groups")
    chosen = remaining[:256]
    contexts = []
    for c in read(anchor.TREC_DATA)["contexts"]:
        contexts.append({"dataset": "trec", "source_context_id": c["id"], "records": [
            {"question": r["question"], "group_id": r["group_id"], "gold_label": r["gold"],
             "source_line_1based": r["source_line_1based"]} for r in c["records"]]})
    assert len(contexts) == 6
    for index in range(4):
        contexts.append({"dataset": "sst2", "source_context_id": f"fresh-third-sst2-{index:02d}", "records": [
            {"question": r["sentence"], "group_id": r["group_id"], "gold_label": r["gold"],
             "source_indexes": r["source_indexes"], "source_row_indexes": r["source_row_indexes"],
             "source_labels": r["source_labels"]} for r in chosen[index * 64:(index + 1) * 64]]})
    for index, c in enumerate(contexts):
        c["index"] = index
        source = c["records"]
        c["source_group_order"] = [r["group_id"] for r in source]
        c["permutation"] = sorted(range(64), key=lambda j: digest([ROOT.name, "context-permutation-v1",
            c["dataset"], c["source_context_id"], source[j]["group_id"]]))
        c["records"] = [{**source[j], "source_position": j + 1, "input_position": i + 1,
                         "id": f"q{i + 1:04d}"} for i, j in enumerate(c["permutation"])]
    return {"contexts": contexts, "source_sha256": INPUT_HASHES, "sampling_seeds": SEEDS,
        "permutation_rule": "SHA256(namespace,context-permutation-v1,dataset,source_context_id,group_id), ascending; labels excluded",
        "id_rule": "Batch-local q0001..q0064 assigned after fixed permutation; source positions retained",
        "sst_provenance": {"dataset": "stanfordnlp/sst2", "revision": anchor.sst.REVISION,
            "split": "validation", "source_rows": len(rows), "unique_groups": dedup["unique_groups"],
            "normalization": "NFKC, casefold, whitespace collapse", "prior_group_sets": [sorted(x) for x in prior],
            "remaining_after_both": len(remaining), "new_groups": len(chosen),
            "intersection_with_each_prior": [len(x & {r["group_id"] for r in chosen}) for x in prior],
            "selection": "first256 remaining normalized hashes in lexical order, then4 contiguous64 groups; no labels used",
            "source_acquisition": str(anchor.sst.CACHE / "ACQUISITION.json"),
            "license": "underlying dataset unknown in official card; not inferred from software license",
            "freshness": "Not prompted in either earlier SST study; base-model pretraining and outside study exposure unknown"},
        "trec_provenance": {**prior_anchor["trec_provenance"], "fresh_context_group_claim": False,
                            "interpretation": "Six exposed384-question test compositions, newly permuted without label selection"}}


def build_design(data):
    previous = read(ANCHOR / "SPEC.json")["design"]
    d = {"contexts": deepcopy(data["contexts"]), "contract": deepcopy(previous["contract"]),
        "labels": previous["labels"], "definitions": previous["definitions"],
        "task_labels": previous["task_labels"], "task_definitions": previous["task_definitions"],
        "model_alias": "__ROW_WEIGHT_ALIAS__", "model_aliases": {w: "__UNBOUND_" + w.upper() + "__" for w in WEIGHTS},
        "max_tokens": 3072, "max_concurrent_calls": 4, "call_timeout_seconds": 120,
        "wall_time_cap_seconds": 1800, "plan": [], "coordinates": [], "batches": []}
    cells = [(w, a, g) for w in WEIGHTS for a in ["anonymous", "indexed"] for g in ["free", "exact"]]
    for c in d["contexts"]:
        for repeat, seed in enumerate(SEEDS):
            shift = (c["index"] * 2 + repeat) % 8
            order = cells[shift:] + cells[:shift]
            if (c["index"] + repeat) % 2:
                order = list(reversed(order))
            for position, (weight, arm, grammar) in enumerate(order):
                row = {"dataset": c["dataset"], "context_index": c["index"], "source_context_id": c["source_context_id"],
                    "weight": weight, "arm": arm, "grammar": grammar, "seed": seed, "repeat": repeat,
                    "size": 64, "permutation": 0, "start": 0, "cell_order": position,
                    "batch_id": len(d["batches"]), "dispatch_order": len(d["plan"])}
                row["id"] = digest([ROOT.name, row])
                row["coordinate_id"] = row["id"]
                d["coordinates"].append(deepcopy(row))
                d["plan"].append(row)
                d["batches"].append({"questions": [r["question"] for r in c["records"]],
                    "gold": {"records": deepcopy(c["records"]), "order": list(range(64)), "arm": arm,
                             "labels": d["task_labels"][c["dataset"]]}})
    return d


def make_request(design, row):
    body = anchor.make_request(design, row)
    body["model"] = design["model_aliases"][row["weight"]]
    if row["grammar"] == "free":
        body.pop("structured_outputs")
    elif row["grammar"] != "exact":
        raise ValueError("unknown grammar state")
    return body


score_labels = anchor.score_labels


def score_coordinate(design, coordinate, records):
    result = anchor.score_coordinate(design, coordinate, records)
    result["call_wall_seconds_sum"] = sum(r["ended"] - r["started"] for r in records)
    result["model_called"] = sum(bool(r["model_called"]) for r in records)
    result["format_statuses"] = dict(Counter((r.get("score") or {}).get("parse_status", "infrastructure_null") for r in records))
    result["output_order_matches_input"] = (all(r["output_position"] == r["input_position"] for r in result["records"])
        if result["complete"] and result["aligned_records"] == 64 else None)
    return result


def summarize(design, records):
    coordinates = [score_coordinate(design, row, [r for r in records if r["coordinate"]["id"] == row["id"]])
                   for row in design["coordinates"]]
    cells = []
    for key in sorted({(c["dataset"], c["weight"], c["arm"], c["grammar"]) for c in design["coordinates"]}):
        chosen = [r for r in coordinates if tuple(r["coordinate"][k] for k in ["dataset", "weight", "arm", "grammar"]) == key]
        items = [i for r in chosen for i in r["records"]]
        aligned = [i for i in items if i["aligned"]]
        cells.append({"dataset": key[0], "weight": key[1], "representation": key[2], "grammar": key[3],
            "planned_calls": len(chosen), "completed_calls": sum(r["complete"] for r in chosen),
            "observable_calls": sum(r["strict_full64_correct"] is not None for r in chosen),
            "strict_whole64_successes": sum(r["strict_full64_correct"] == 1 for r in chosen),
            "valid_complete64_calls": sum(r["fully_valid"] for r in chosen),
            "planned_assignments": len(chosen) * 64, "aligned_assignments": len(aligned),
            "canonical_correct": sum(i["correct"] for i in aligned),
            "accuracy_among_aligned": sum(i["correct"] for i in aligned) / len(aligned) if aligned else None,
            "input_position_quartiles": [{"quartile": q, "aligned": sum((i["input_position"] - 1) // 16 == q for i in aligned),
                "correct": sum(i["correct"] and (i["input_position"] - 1) // 16 == q for i in aligned)} for q in range(4)],
            "confusion": [{"gold": g, "prediction": p, "count": n} for (g, p), n in sorted(Counter((i["gold"], i["prediction"]) for i in aligned).items())],
            "usage": {k: sum(r["usage"][k] for r in chosen) for k in ["logical_input_tokens", "cached_input_tokens", "uncached_input_tokens", "completion_tokens"]},
            "missing_usage": {k: sum(r["missing_usage"][k] for r in chosen) for k in ["logical_input_tokens", "cached_input_tokens", "uncached_input_tokens", "completion_tokens"]},
            "length_stops": sum(r["length_stops"] for r in chosen),
            "call_wall_seconds_sum": sum(r["call_wall_seconds_sum"] for r in chosen)})
    grouped = defaultdict(dict)
    for row in coordinates:
        c = row["coordinate"]
        grouped[c["dataset"], c["context_index"], c["repeat"]][c["weight"], c["arm"], c["grammar"]] = row
    pairs = []
    for key, group in grouped.items():
        for weight in WEIGHTS:
            for grammar in ["free", "exact"]:
                a, b = group[weight, "anonymous", grammar], group[weight, "indexed", grammar]
                observable = a["strict_full64_correct"] is not None and b["strict_full64_correct"] is not None
                pairs.append({"dataset": key[0], "context_index": key[1], "repeat": key[2], "weight": weight,
                    "grammar": grammar, "both_observable": observable, "jointly_valid": a["fully_valid"] and b["fully_valid"],
                    "indexed_minus_anonymous_correct": b["canonical_correct"] - a["canonical_correct"] if observable else None})
    return {"cells": cells, "paired_context_effects": pairs, "coordinates": coordinates,
        "unit_caution": "6 exposed TREC and4 newly unexposed SST context groups; repeated seeds/cells nested. Invalid structure is unavailable semantic alignment, not64 established semantic errors.",
        "inference_caution": "No prefix credit/repair; fixed output cap is not equal actual compute. Old/indexed SFT curricula differ; not an ID-only training ablation or RLM result."}


# Only this private imported collector instance changes; upstream files/processes do not.
anchor.corr.fixed.make_request = make_request
anchor.corr.fixed.score_coordinate = score_coordinate
anchor.corr.fixed.leaf.score_labels = score_labels
anchor.corr.fixed.leaf.write_once = write_once
collect_calls = anchor.corr.fixed.collect_calls
