"""Freeze the label-blind TREC panel and exact paired native request bodies."""

import copy
import hashlib
import json
import time
from pathlib import Path

import protocol
import study as s


PAIRS = tuple(
    (protocol.CATEGORIES[index], protocol.CATEGORIES[(index + 1) % len(protocol.CATEGORIES)])
    for index in range(len(protocol.CATEGORIES))
)
DEFINITIONS = """Classify the type of answer requested, not words mentioned in the question.
human being: a person, an organization or group of people, or a person's role, title or description.
location: a geographic place, including a city, country, state, mountain or other place.
abbreviation: a shortened form, or the expanded wording represented by a shortened form.
entity: a nonhuman, nongeographic thing or name, including objects, organisms, works, events, substances, methods or synonymous terms.
description and abstract concept: a definition, explanation, reason or manner of doing something, rather than a particular name or number.
numeric value: a quantity, count, measurement, date, duration, rank or numerical code."""


def selected_rows():
    public = s.read(s.PRIOR / "inputs/PUBLIC.json")[0]["records"]
    gold = s.read(s.PRIOR / "inputs/HOST_GOLD.json")["official-trec-test-500"]["labels"]
    ordered = sorted(public, key=lambda row: s.digest([s.ROOT.name, row["id"]]))
    selected = [dict(row, gold=gold[row["id"]]) for row in ordered[:128]]
    return selected, {
        "selection": "first 128 ascending SHA256 canonical JSON [namespace,record_id]",
        "selection_used_labels": False,
        "official_test_rows": len(public),
        "selected_rows": len(selected),
        "research_exposure": "official test is research-exposed; 489/500 groups were used in an earlier selected-test evaluation",
    }


def plan_only(rows):
    plan = []
    for batch in range(8):
        batch_rows = rows[batch * 16 : (batch + 1) * 16]
        for pair_index, pair in enumerate(PAIRS):
            block = batch * 6 + pair_index
            cells = [("base", "full6"), ("base", "abo"), ("c32", "full6"), ("c32", "abo")]
            cells = cells[block % 4 :] + cells[: block % 4]
            for model_policy, interface in cells:
                coordinate = {
                    "context_id": f"official-trec-query-conditioned-{batch:02d}",
                    "batch": batch,
                    "pair_index": pair_index,
                    "pair": list(pair),
                    "seed": s.SEEDS[block],
                    "model_policy": model_policy,
                    "interface": interface,
                    "ids": [row["id"] for row in batch_rows],
                    "n": 16,
                    "dispatch_order": len(plan),
                }
                coordinate["id"] = s.digest([s.ROOT.name, coordinate])
                plan.append(coordinate)
    return plan


def tokenizer():
    return s.renderer()[1]


def model_for(policy):
    if policy == "base":
        return s.BASE_MODEL
    if policy == "c32":
        return s.binding()["fixed_child"]
    raise ValueError("unknown model policy")


def prompt(records, pair, interface):
    pair_line = f"For this requested pair, A means {pair[0]}; B means {pair[1]}; other means any of the other four categories."
    if interface == "full6":
        output = 'Return only one JSON object mapping every supplied id exactly once to one of the six full category labels listed above.'
    elif interface == "abo":
        output = 'Return only one JSON object mapping every supplied id exactly once to A, B, or other.'
    else:
        raise ValueError("unknown interface")
    return (
        "Classify the type of answer requested by each question using these TREC definitions:\n"
        + DEFINITIONS
        + "\n"
        + pair_line
        + "\n"
        + output
        + "\nNo missing or extra ids.\nRecords: "
        + json.dumps(records, separators=(",", ":"), ensure_ascii=False)
    )


def build_bodies(plan, rows, tok):
    template = copy.deepcopy(next(iter(s.read(s.PRIOR / "inputs/REQUESTS.json").values())))
    decoded = tok.decode(template["token_ids"])
    marker = "<|im_start|>user\n"
    start = decoded.index(marker) + len(marker)
    end = decoded.index("<|im_end|>\n<|im_start|>assistant", start)
    prefix, suffix = decoded[:start], decoded[end:]
    by_id = {row["id"]: row for row in rows}
    bodies = {}
    for coordinate in plan:
        records = [{"id": rid, "text": by_id[rid]["text"]} for rid in coordinate["ids"]]
        body = copy.deepcopy(template)
        body["model"] = model_for(coordinate["model_policy"])
        body["token_ids"] = tok.encode(
            prefix + prompt(records, coordinate["pair"], coordinate["interface"]) + suffix,
            add_special_tokens=False,
        )
        body["sampling_params"]["seed"] = coordinate["seed"]
        allowed = protocol.CATEGORIES if coordinate["interface"] == "full6" else protocol.PROJECTED
        body["sampling_params"]["structured_outputs"]["json"] = {
            "type": "object",
            "properties": {rid: {"type": "string", "enum": list(allowed)} for rid in sorted(coordinate["ids"])},
            "required": coordinate["ids"],
            "additionalProperties": False,
        }
        if len(body["token_ids"]) + 2048 > 8192:
            raise ValueError("native context admission")
        bodies[coordinate["id"]] = body
    return bodies


def scan_seeds():
    started = time.time()
    matches = []
    needles = {str(seed) for seed in s.SEEDS}
    for path in sorted(s.SIDE.glob("*/inputs/*.json")):
        if s.ROOT in path.parents:
            continue
        text = path.read_text(errors="replace")
        found = sorted(seed for seed in needles if seed in text)
        if found:
            matches.append({"path": str(path), "seeds": found})
    return {"started_epoch": started, "ended_epoch": time.time(), "scope": "named sidecar input JSON files existing at scan time", "matches_outside_new_sidecar": matches}


def main():
    started = time.time()
    rows, provenance = selected_rows()
    plan = plan_only(rows)
    tok = tokenizer()
    bodies = build_bodies(plan, rows, tok)
    gold = {row["id"]: row["gold"] for row in rows}
    public = [{"id": row["id"], "text": row["text"], "source_line_1based": row["source_line_1based"], "normalized_question_sha256": row["normalized_question_sha256"]} for row in rows]
    seed_scan = scan_seeds()
    if seed_scan["matches_outside_new_sidecar"]:
        raise ValueError("seed collision")
    provenance.update({
        "created_epoch": time.time(),
        "pairs": [list(pair) for pair in PAIRS],
        "batching": "selected order divided into eight contiguous 16-record batches",
        "source_ready_sha256": s.sha(s.PRIOR / "READY.json"),
        "source_public_sha256": s.sha(s.PRIOR / "inputs/PUBLIC.json"),
        "source_gold_sha256": s.sha(s.PRIOR / "inputs/HOST_GOLD.json"),
        "source_license_status": "underlying TREC data rights unspecified; cached source only, no redistribution grant inferred",
        "optimizer_group_overlap": 0,
    })
    s.write(s.ROOT / "inputs/PUBLIC.json", public)
    s.write(s.ROOT / "inputs/HOST_GOLD.json", {"labels": gold})
    s.write(s.ROOT / "inputs/PLAN.json", plan)
    s.write(s.ROOT / "inputs/REQUESTS.json", bodies)
    s.write(s.ROOT / "inputs/PROVENANCE.json", provenance)
    s.write(s.ROOT / "inputs/SEED_SCAN.json", seed_scan)
    s.write(s.ROOT / "CPU_INPUT_NATIVE.json", {
        "planned": len(plan), "selected_records": len(rows), "blocks": 48,
        "max_prompt_tokens": max(len(body["token_ids"]) for body in bodies.values()),
        "elapsed_seconds": time.time() - started, "gpu_calls": 0,
    })
    print({"planned": len(plan), "records": len(rows), "max_prompt_tokens": max(len(body["token_ids"]) for body in bodies.values())})


if __name__ == "__main__":
    main()
