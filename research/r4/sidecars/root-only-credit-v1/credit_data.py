"""Deterministic source-train-only context composition; gold stays host-side."""

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SEED = 981260400
SOURCE = ROOT.parent / "trec-leaf-sft-v1/source/data.py"
SOURCE_SHA = "b5aa353e2173c3fd48ecc36ce0596c9c3328767a7d82c8d22c57b4e0a32f0b8f"
COMPOSITION = ROOT.parent / "leaf-composition-transfer-v1/prepared-v1/DATA.json"
COMPOSITION_SHA = "1ea4640da5a8e3e305bee7f79d5abeecb02507d6bcc33d709d1c7209fd47bfc2"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def file_hash(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def build(rows):
    if len(rows) < 384 or len({r["group_id"] for r in rows}) != len(rows):
        raise ValueError("at least384 unique question groups required")
    ordered = sorted(rows, key=lambda r: digest([ROOT.name, SEED, r["group_id"]]))
    public, gold, plan = {"contexts": [], "tasks": []}, {}, []
    for index in range(6):
        records = ordered[index * 64:(index + 1) * 64]
        if any("\n" in r["question"] or "\r" in r["question"] for r in records):
            raise ValueError("record question contains a line separator")
        text = "\n".join(f"Date: 2000-01-{i % 28 + 1:02d} || User: {i % 8} || Instance: {r['question']}" for i, r in enumerate(records)) + "\n"
        context_id = f"root-credit-context-{index:02d}"
        context_sha = hashlib.sha256(text.encode()).hexdigest()
        split = "training" if index < 4 else "validation"
        public["contexts"].append({"id": context_id, "text": text, "sha256": context_sha,
            "split": split, "group_ids": [r["group_id"] for r in records]})
        for query, label in enumerate(("human being", "numeric value")):
            name = f"root-credit:{index:02d}:{query}"
            task = {"name": name, "context_id": context_id, "context_sha256": context_sha,
                "context_window_id": 1000 + index, "source_id": 14000000 + 2 * index + query,
                "label": label, "split": split, "answer_type": "ANSWER_TYPE.NUMERIC",
                "question": f"How many records in the entire context have questions whose answers belong to the category '{label}'? Return the exact integer count in the form 'Answer: [X]', replacing [X] with the number and omitting square brackets."}
            public["tasks"].append(task)
            gold[name] = {"answer": repr([sum(r["gold"] == label for r in records)]), "records": records}
            for repeat in range(4 if split == "training" else 2):
                row = {"study": ROOT.name, "task_name": name, "source_id": task["source_id"],
                    "context_window_id": task["context_window_id"], "context_sha256": context_sha,
                    "split": split, "analysis_split": "fresh_composition_leaf_train_supported",
                    "repeat": repeat, "seed": int(digest([ROOT.name, SEED, name, repeat])[:8], 16) % (2**31 - 1),
                    "temperature": 0.5, "client_path": "train", "arm": "sft_child",
                    "group_id": digest([ROOT.name, name, 0.5])}
                plan.append({**row, "id": digest(row), "pair_id": digest([row, "unpaired"]), "pair_order": 0})
    plan.sort(key=lambda r: digest([SEED, "dispatch", r["id"]]))
    return public, gold, [{**r, "dispatch_order": i} for i, r in enumerate(plan)]


def prepare():
    if file_hash(SOURCE) != SOURCE_SHA or file_hash(COMPOSITION) != COMPOSITION_SHA:
        raise ValueError("authenticated source/composition changed")
    source = load("root_credit_trec_source", SOURCE)
    partitions = source.load_partitions()
    public, gold, plan = build(partitions["train"])
    selected = {g for c in public["contexts"] for g in c["group_ids"]}
    forbidden = {r["group_id"] for key in ("validation", "test") for r in partitions[key]}
    transfer = {g for c in read(COMPOSITION)["contexts"] for g in c["group_ids"]}
    if selected & (forbidden | transfer):
        raise ValueError("root contexts overlap forbidden source partitions/transfer groups")
    provenance = {"schema": ROOT.name + "-data", "seed": SEED, "source_split_sha256": source.SPLIT_SHA,
        "source_train_groups": 5065, "selected_groups": 384, "contexts": 6,
        "root_train_contexts": 4, "root_validation_contexts": 2,
        "overlap_leaf_validation": 0, "overlap_leaf_test": 0, "overlap_new_composition": 0,
        "child_trained_on_these_questions": True, "base_pretraining_contamination_unknown": True,
        "metadata": "Date/User deterministic by position, independent of labels",
        "gold_scope": "HOST_GOLD.json only; runtime sees context text and public prompt",
        "source_sha256": {str(SOURCE): SOURCE_SHA, str(COMPOSITION): COMPOSITION_SHA,
            str(source.PROVENANCE / "PROPOSED_SPLIT.json"): source.SPLIT_SHA,
            **read(source.PROVENANCE / "INVENTORY.json")["source_file_sha256"]}}
    destination = ROOT / "inputs"
    destination.mkdir(exist_ok=False)
    for name, value in (("PUBLIC.json", public), ("HOST_GOLD.json", gold), ("PLAN.json", plan), ("PROVENANCE.json", provenance)):
        source.write_once(destination / name, value)
        (destination / name).chmod(0o444)
    return provenance


if __name__ == "__main__":
    print(json.dumps(prepare(), indent=2))
