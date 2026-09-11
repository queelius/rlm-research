"""Freeze all 500 official TREC test rows and paired native requests."""
import copy
import hashlib
import json
import re
import time
import unicodedata

import protocol
import study as s

LABELS = {"HUM": "human being", "LOC": "location", "ABBR": "abbreviation", "ENTY": "entity", "DESC": "description and abstract concept", "NUM": "numeric value"}


def normalize(question):
    return " ".join(re.findall(r"\w+", unicodedata.normalize("NFKC", question).casefold()))


def official_rows():
    split = s.read(s.SPLIT)
    train_groups = {row["question_group_sha256"] for row in split["source_train"]}
    excluded = {row["question_group_sha256"] for row in split["excluded_test"]}
    raw_rows = []
    for line, raw in enumerate(s.SOURCE.read_bytes().splitlines(), 1):
        fine, _, question = raw.replace(b"\xf0", b" ").strip().decode("utf8").partition(" ")
        coarse = fine.split(":")[0]
        group = hashlib.sha256(normalize(question).encode()).hexdigest()
        rid = "q" + hashlib.sha256(f"official-test-line:{line}:{question}".encode()).hexdigest()[:12]
        raw_rows.append({"id": rid, "text": question, "gold": LABELS[coarse], "coarse": coarse, "fine": fine, "source_line_1based": line, "normalized_question_sha256": group})
    groups = {row["normalized_question_sha256"] for row in raw_rows}
    rows = sorted(raw_rows, key=lambda row: (hashlib.sha256(row["id"].encode()).hexdigest(), row["source_line_1based"]))
    provenance = {
        "official_source_rows": len(rows),
        "normalized_question_groups": len(groups),
        "duplicate_source_lines_retained": len(rows) - len(groups),
        "deduplication_policy": "none: every official source line is an evaluation record; normalized groups are reported diagnostically",
        "order_policy": "ascending SHA256 of stable per-source-line record ID, then source line",
        "optimizer_train_groups": len(train_groups),
        "optimizer_train_normalized_group_intersection": sorted(groups & train_groups),
        "raw_train_overlap_groups": len(groups & excluded),
        "raw_train_overlap_group_ids": sorted(groups & excluded),
        "research_exposure": "489 of 500 official-test groups were used in the earlier c32 selected-test evaluation; 11 raw-train-overlap groups were excluded from that evaluation and from c32 optimizer training. The panel is partly research-exposed, not pristine",
    }
    return rows, provenance


def model_for(policy, base, child):
    if policy == "base":
        return base
    if policy == "c32":
        return child
    raise ValueError("unknown model policy")


def plan_only(rows):
    plan = []
    for repeat, seed in enumerate(s.SEEDS):
        arms = ("W", "S") if repeat == 0 else ("S", "W")
        for arm in arms:
            width = 100 if arm == "W" else 16
            for batch_index, start in enumerate(range(0, len(rows), width), 1):
                batch = rows[start:start + width]
                policies = ("base", "c32") if (repeat + batch_index + (arm == "S")) % 2 == 0 else ("c32", "base")
                for policy in policies:
                    coordinate = {"context_id": "official-trec-test-500", "repeat": repeat, "seed": seed, "arm": arm, "batch": batch_index, "model_policy": policy, "ids": [row["id"] for row in batch], "n": len(batch), "dispatch_order": len(plan)}
                    coordinate["id"] = s.digest([s.ROOT.name, repeat, arm, batch_index, policy, coordinate["ids"]])
                    plan.append(coordinate)
    return plan


def build_bodies(plan, rows, tokenizer):
    templates = s.read(s.PRIOR / "inputs/REQUESTS.json")
    first = next(iter(templates.values()))
    decoded = tokenizer.decode(first["token_ids"])
    offset = decoded.rindex("Records: ") + len("Records: ")
    _, length = json.JSONDecoder().raw_decode(decoded[offset:])
    prefix, suffix = decoded[:offset], decoded[offset + length:]
    by_id = {row["id"]: row for row in rows}
    child = s.binding()["fixed_child"]
    bodies = {}
    for coordinate in plan:
        batch = [{"id": rid, "text": by_id[rid]["text"]} for rid in coordinate["ids"]]
        body = copy.deepcopy(first)
        body["model"] = model_for(coordinate["model_policy"], s.BASE_MODEL, child)
        body["token_ids"] = tokenizer.encode(prefix + json.dumps(batch, separators=(",", ":"), ensure_ascii=False) + suffix, add_special_tokens=False)
        body["sampling_params"]["seed"] = coordinate["seed"]
        schema = body["sampling_params"]["structured_outputs"]["json"]
        example = next(iter(schema["properties"].values()))
        schema["properties"] = {key: copy.deepcopy(example) for key in sorted(coordinate["ids"])}
        schema["required"] = coordinate["ids"]
        if len(body["token_ids"]) + 2048 > 8192:
            raise ValueError("native context admission")
        bodies[coordinate["id"]] = body
    return bodies


def main():
    started = time.time()
    rows, provenance = official_rows()
    assert len(rows) == 500 and provenance["normalized_question_groups"] == 500
    assert not provenance["optimizer_train_normalized_group_intersection"]
    plan = plan_only(rows)
    _, tokenizer = s.renderer()
    bodies = build_bodies(plan, rows, tokenizer)
    gold = {"official-trec-test-500": {"labels": {row["id"]: row["gold"] for row in rows}}}
    public = [{"id": "official-trec-test-500", "records": [{"id": row["id"], "text": row["text"], "source_line_1based": row["source_line_1based"], "normalized_question_sha256": row["normalized_question_sha256"]} for row in rows]}]
    source_paths = [s.SOURCE, s.SPLIT, s.PRIOR / "READY.json", s.PRIOR / "inputs/REQUESTS.json", s.TRAIN_PREPARED / "MANIFEST.json", s.TRAIN_PREPARED / "data.json"]
    provenance.update({"schema": "official-trec-test-adapter-granularity-provenance-v1", "created_epoch": time.time(), "source_sha256": {str(path): s.sha(path) for path in source_paths}, "source_url": "https://cogcomp.seas.upenn.edu/Data/QA/QC/TREC_10.label", "source_revision": None, "source_content_sha256": s.sha(s.SOURCE), "license_status": "underlying TREC data rights unspecified; cached source only, no redistribution grant inferred", "fine_labels_retained_in_private_gold_only": True})
    s.write(s.ROOT / "inputs/PUBLIC.json", public)
    s.write(s.ROOT / "inputs/HOST_GOLD.json", gold)
    s.write(s.ROOT / "inputs/PLAN.json", plan)
    s.write(s.ROOT / "inputs/REQUESTS.json", bodies)
    s.write(s.ROOT / "inputs/PROVENANCE.json", provenance)
    s.write(s.ROOT / "CPU_INPUT_NATIVE.json", {"planned": len(plan), "official_rows": len(rows), "normalized_groups": provenance["normalized_question_groups"], "max_prefix": max(len(body["token_ids"]) for body in bodies.values()), "all_prefixes_fit": True, "paired_body_difference_only_model": True, "elapsed_seconds": time.time() - started, "gpu_calls": 0})
    print({"planned": len(plan), "rows": len(rows), "groups": provenance["normalized_question_groups"], "max_prefix": max(len(body["token_ids"]) for body in bodies.values())})


if __name__ == "__main__":
    main()
