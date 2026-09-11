"""Build immutable matched training rows and two-panel native readout inputs."""

import copy
import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

import study as s

DATA = s.load(
    "trec_followup_data",
    s.SFT / "source/data.py",
    "b5aa353e2173c3fd48ecc36ce0596c9c3328767a7d82c8d22c57b4e0a32f0b8f",
)
QPREP = s.load(
    "trec_followup_query_prepare",
    s.QUERY / "prepare.py",
    "4940a3ec887016f3b25c579cbdde244c1dfa77429d9e33ea87d7f0fd452abeff",
)
TRAIN_SOURCE = Path(
    "/project/alex_phd/research-cache/2026-09-08-literature/trec-context8.6NYSkv/train_5500.label"
)
OOLONG = Path(
    "/project/alex_phd/research-cache/2026-09-08-literature/trec-context8.6NYSkv/oolong__trec_coarse_validated.jsonl"
)


def normalize(text):
    return " ".join(re.findall(r"\w+", unicodedata.normalize("NFKC", text).casefold()))


def stable_id(group_id):
    return "q" + hashlib.sha256(("source-train-group:" + group_id).encode()).hexdigest()[:12]


def ordered(rows, role, key):
    return sorted(rows, key=lambda row: s.digest([s.ROOT.name, role, row[key]]))


def build_closure():
    partitions = DATA.load_partitions()
    train_rows = ordered(partitions["train"], "continuation-train", "group_id")[:1536]
    test_public = s.read(s.TEST500 / "inputs/PUBLIC.json")[0]["records"]
    query_rows = s.read(s.QUERY / "inputs/PUBLIC.json")
    split = s.read(s.SPLIT / "PROPOSED_SPLIT.json")
    clean = {row["question_group_sha256"]: row for row in split["test"]}
    query_ids = {row["id"] for row in query_rows}
    eligible = [
        row
        for row in test_public
        if row["normalized_question_sha256"] in clean and row["id"] not in query_ids
    ]
    primary = ordered(eligible, "primary-new-contract", "id")[:128]

    train_labels = {}
    for raw in TRAIN_SOURCE.read_bytes().splitlines():
        fine, _, question = raw.replace(b"\xf0", b" ").strip().decode().partition(" ")
        train_labels.setdefault(
            hashlib.sha256(normalize(question).encode()).hexdigest(), set()
        ).add(fine.split(":")[0])
    oolong_groups = {
        hashlib.sha256(normalize(json.loads(line)["input"]).encode()).hexdigest()
        for line in OOLONG.read_text().splitlines()
    }
    excluded = {row["question_group_sha256"]: row for row in split["excluded_test"]}
    query_ineligible = []
    for row in query_rows:
        group = row["normalized_question_sha256"]
        if group not in excluded:
            continue
        reasons = []
        if group in train_labels:
            reasons.append("official_train_overlap")
        test_coarse = excluded[group]["coarse"]
        if group in train_labels and train_labels[group] != {test_coarse}:
            reasons.append("coarse_label_conflict")
        if group in oolong_groups:
            reasons.append("oolong_validated_pool_overlap")
        query_ineligible.append({**row, "test_coarse": test_coarse, "reasons": reasons})
    result = {
        "train_groups": [row["group_id"] for row in train_rows],
        "train_group_ids_digest": s.digest([row["group_id"] for row in train_rows]),
        "primary_rows": primary,
        "primary_record_ids_digest": s.digest([row["id"] for row in primary]),
        "query_rows": query_rows,
        "query_clean_count": sum(row["normalized_question_sha256"] in clean for row in query_rows),
        "query_split_ineligible": query_ineligible,
        "pristine_holdout_available": False,
        "_train_rows": train_rows,
        "_test_gold": s.read(s.TEST500 / "inputs/HOST_GOLD.json")["official-trec-test-500"][
            "labels"
        ],
    }
    if (
        result["train_group_ids_digest"] != s.TRAIN_DIGEST
        or result["primary_record_ids_digest"] != s.PRIMARY_DIGEST
    ):
        raise ValueError("prospective deterministic data identity changed")
    return result


def _wrapper(tokenizer):
    template = copy.deepcopy(next(iter(s.read(s.QUERY / "inputs/REQUESTS.json").values())))
    decoded = tokenizer.decode(template["token_ids"])
    marker = "<|im_start|>user\n"
    start = decoded.index(marker) + len(marker)
    end = decoded.index("<|im_end|>\n<|im_start|>assistant", start)
    return template, decoded[:start], decoded[end:]


def training_rows(closure):
    tokenizer = DATA.load_tokenizer()
    _, prefix, suffix = _wrapper(tokenizer)
    result = {"full6": [], "abo": []}
    for context in range(96):
        batch = closure["_train_rows"][context * 16 : (context + 1) * 16]
        pair = s.TRAIN_PAIRS[context % 6]
        records = [{"id": stable_id(row["group_id"]), "text": row["question"]} for row in batch]
        for interface in result:
            prompt = prefix + QPREP.prompt(records, pair, interface) + suffix
            labels = {
                stable_id(row["group_id"]): row["gold"]
                if interface == "full6"
                else ("A" if row["gold"] == pair[0] else "B" if row["gold"] == pair[1] else "other")
                for row in batch
            }
            target = json.dumps(labels, separators=(",", ":"), ensure_ascii=False)
            prompt_ids = tokenizer.encode(prompt, add_special_tokens=False)
            full_ids = tokenizer.encode(prompt + target + "<|im_end|>\n", add_special_tokens=False)
            row = {
                "id": f"train-{interface}-{context:03d}",
                "context_id": f"train-{context:03d}",
                "interface": interface,
                "pair": list(pair),
                "seed": s.recipe()["train_seed"] + context,
                "ids": [record["id"] for record in records],
                "group_ids": [item["group_id"] for item in batch],
                "prompt": prompt,
                "target": target,
                "prompt_length": len(prompt_ids),
                "target_tokens": len(full_ids) - len(prompt_ids),
                "input_ids": full_ids,
                "labels": [-100] * len(prompt_ids) + full_ids[len(prompt_ids) :],
            }
            result[interface].append(row)
    return result


def evaluation_plan(closure):
    recipe = s.recipe()
    panels = [
        (
            "primary",
            closure["primary_rows"],
            s.NEW_PAIRS,
            ("c32", "full6_sft24", "abo_sft24"),
            recipe["eval_primary_seeds"],
        ),
        (
            "development",
            closure["query_rows"],
            s.TRAIN_PAIRS,
            ("full6_sft24", "abo_sft24"),
            recipe["eval_development_seeds"],
        ),
    ]
    plan = []
    for panel, rows, pairs, policies, seeds in panels:
        for batch in range(8):
            ids = [row["id"] for row in rows[batch * 16 : (batch + 1) * 16]]
            for pair_index, pair in enumerate(pairs):
                block = batch * 6 + pair_index
                projected = [
                    "A"
                    if closure["_test_gold"][rid] == pair[0]
                    else "B"
                    if closure["_test_gold"][rid] == pair[1]
                    else "other"
                    for rid in ids
                ]
                target_support = {label: projected.count(label) for label in ("A", "B", "other")}
                cells = [
                    (policy, interface) for policy in policies for interface in ("full6", "abo")
                ]
                cells = cells[block % len(cells) :] + cells[: block % len(cells)]
                for policy, interface in cells:
                    coordinate = {
                        "panel": panel,
                        "context_id": f"{panel}-{batch:02d}",
                        "batch": batch,
                        "pair_index": pair_index,
                        "pair": list(pair),
                        "seed": seeds[block],
                        "model_policy": policy,
                        "interface": interface,
                        "ids": ids,
                        "n": 16,
                        "target_support": target_support,
                        "dispatch_order": len(plan),
                    }
                    coordinate["id"] = s.digest([s.ROOT.name, coordinate])
                    plan.append(coordinate)
    return plan


def request_bodies(plan, closure):
    tokenizer = DATA.load_tokenizer()
    template, prefix, suffix = _wrapper(tokenizer)
    all_rows = closure["primary_rows"] + closure["query_rows"]
    by_id = {row["id"]: row for row in all_rows}
    bodies = {}
    for coordinate in plan:
        records = [{"id": rid, "text": by_id[rid]["text"]} for rid in coordinate["ids"]]
        body = copy.deepcopy(template)
        body["model"] = s.ALIASES[coordinate["model_policy"]]
        body["token_ids"] = tokenizer.encode(
            prefix + QPREP.prompt(records, coordinate["pair"], coordinate["interface"]) + suffix,
            add_special_tokens=False,
        )
        body["sampling_params"]["seed"] = coordinate["seed"]
        allowed = s.CATEGORIES if coordinate["interface"] == "full6" else ("A", "B", "other")
        body["sampling_params"]["structured_outputs"]["json"] = {
            "type": "object",
            "properties": {
                rid: {"type": "string", "enum": list(allowed)} for rid in sorted(coordinate["ids"])
            },
            "required": coordinate["ids"],
            "additionalProperties": False,
        }
        if len(body["token_ids"]) + 2048 > 8192:
            raise ValueError("native context admission")
        bodies[coordinate["id"]] = body
    return bodies


def write_inputs(output, closure=None):
    output = Path(output)
    if output.exists():
        raise ValueError("unused prepared directory required")
    output.mkdir(parents=True)
    closure = closure or build_closure()
    train = training_rows(closure)
    plan = evaluation_plan(closure)
    bodies = request_bodies(plan, closure)
    gold = closure["_test_gold"]
    public = {"primary": closure["primary_rows"], "development": closure["query_rows"]}
    provenance = {
        "schema": "trec-child-interface-sft-followup-provenance-v1",
        "train_group_ids_digest": closure["train_group_ids_digest"],
        "primary_record_ids_digest": closure["primary_record_ids_digest"],
        "train_unique_groups": 1536,
        "train_contexts_per_arm": 96,
        "primary_unique_groups": 128,
        "primary_contexts": 8,
        "development_unique_groups": 128,
        "development_contexts": 8,
        "development_clean_split_eligible": closure["query_clean_count"],
        "development_split_ineligible": closure["query_split_ineligible"],
        "development_research_exposed": True,
        "primary_query_contract_unexposed_but_prior_semantic_outcomes_exposed": True,
        "pristine_holdout_available": False,
        "interface_intervention": s.recipe()["interface_intervention"],
        "class_counts_train": dict(Counter(row["gold"] for row in closure["_train_rows"])),
    }
    values = {
        "TRAIN.json": train,
        "PUBLIC.json": public,
        "HOST_GOLD.json": {"labels": gold},
        "EVAL_PLAN.json": plan,
        "REQUESTS.json": bodies,
        "PROVENANCE.json": provenance,
    }
    for name, value in values.items():
        s.write(output / name, value)
    return {
        "files": list(values),
        "planned_calls": len(plan),
        "training_contexts": sum(map(len, train.values())),
    }


if __name__ == "__main__":
    print(json.dumps(write_inputs(s.PREPARED), sort_keys=True))
