"""Freeze label-independent new contexts and matched role-treatment coordinates."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "trec-leaf-sft-v1/source/data.py"
SEED = 981260300
LABELS = ("human being", "numeric value")
ARMS = ("original_child", "sft_child")


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def build(rows):
    if len(rows) < 384 or len({row["group_id"] for row in rows}) != len(rows):
        raise ValueError("requires at least384 unique source groups")
    ordered = sorted(rows, key=lambda row: digest([ROOT.name, SEED, row["group_id"]]))
    contexts, tasks, pairs = [], [], []
    for index in range(6):
        records = ordered[index * 64 : (index + 1) * 64]
        context_id = f"trec-test-context-{index:02d}"
        text = (
            "\n".join(
                f"Date: 2000-01-{i % 28 + 1:02d} || User: {i % 8} || Instance: {row['question']}"
                for i, row in enumerate(records)
            )
            + "\n"
        )
        if any("\n" in row["question"] or "\r" in row["question"] for row in records):
            raise ValueError("question breaks declared one-record-per-line layout")
        context_sha = hashlib.sha256(text.encode()).hexdigest()
        contexts.append(
            {
                "id": context_id,
                "index": index,
                "text": text,
                "sha256": context_sha,
                "group_ids": [row["group_id"] for row in records],
                "records": records,
                "synthetic_metadata": "Date and User are label-independent deterministic fields",
            }
        )
        for query_index, label in enumerate(LABELS):
            name = f"trec-composition:{index:02d}:{query_index}"
            question = (
                f"How many records in the entire context have questions whose answers belong "
                f"to the category '{label}'? Return the exact integer count in the form "
                "'Answer: [X]', replacing [X] with the number and omitting square brackets."
            )
            task = {
                "name": name,
                "context_id": context_id,
                "context_sha256": context_sha,
                "context_window_id": 900 + index,
                "source_id": 13000000 + 2 * index + query_index,
                "label": label,
                "question": question,
                "answer_type": "ANSWER_TYPE.NUMERIC",
                "answer": repr([sum(row["gold"] == label for row in records)]),
            }
            tasks.append(task)
            for repeat in range(2):
                pair = {
                    "study": ROOT.name,
                    "task_name": name,
                    "source_id": task["source_id"],
                    "context_window_id": task["context_window_id"],
                    "context_sha256": context_sha,
                    "analysis_split": "new_composition_source_test",
                    "repeat": repeat,
                    "seed": int(digest([ROOT.name, SEED, name, repeat])[:8], 16) % (2**31 - 1),
                    "temperature": 0.5,
                    "client_path": "eval",
                }
                order = ARMS if (index + query_index + repeat) % 2 == 0 else ARMS[::-1]
                pairs.append(
                    [
                        {
                            **pair,
                            "arm": arm,
                            "pair_id": digest(pair),
                            "pair_order": position,
                            "group_id": digest([ROOT.name, name, arm]),
                            "id": digest([pair, arm]),
                        }
                        for position, arm in enumerate(order)
                    ]
                )
    pairs.sort(key=lambda pair: digest([SEED, "dispatch", pair[0]["pair_id"]]))
    plan = [
        {**row, "dispatch_order": i} for i, row in enumerate(row for pair in pairs for row in pair)
    ]
    return {"contexts": contexts, "tasks": tasks, "plan": plan}


def main():
    spec = importlib.util.spec_from_file_location("fixed_trec_sft_data", SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    partitions = module.load_partitions()
    data = build(partitions["test"])
    selected_groups = {g for context in data["contexts"] for g in context["group_ids"]}
    forbidden = {row["group_id"] for key in ("train", "validation") for row in partitions[key]}
    if selected_groups & forbidden:
        raise ValueError("context source leaks across SFT partitions")
    data.update(
        schema="trec-new-composition-v1",
        design_seed=SEED,
        source_split_sha256=module.SPLIT_SHA,
        source_test_groups=len(partitions["test"]),
        selected_groups=len(selected_groups),
        excluded_group_ids=sorted({r["group_id"] for r in partitions["test"]} - selected_groups),
        max_concurrent_pairs=4,
        wall_time_cap_seconds=1800,
        independent_context_groups=6,
        source_question_overlap_with_component_test=True,
        source_question_overlap_with_sft_train_validation=False,
        model_outputs_inspected_for_context_or_query_selection=False,
        gold_scope="Host-only records/answers; runtime gets context text and public task prompt only",
    )
    destination = ROOT / "prepared-v1"
    destination.mkdir()
    module.write_once(destination / "DATA.json", data)
    paths = (
        Path(__file__),
        ROOT / "test_prepare.py",
        ROOT / "DESIGN.md",
        SOURCE,
        module.PROVENANCE / "PROPOSED_SPLIT.json",
        module.PROVENANCE / "INVENTORY.json",
    )
    manifest = {
        "schema": "trec-new-composition-manifest-v1",
        "source_sha256": {str(path): module.file_hash(path) for path in paths},
        "data_sha256": module.file_hash(destination / "DATA.json"),
        "preparation": "CPU-only, no model calls or test-output inspection",
    }
    manifest["identity"] = digest(manifest)
    module.write_once(destination / "MANIFEST.json", manifest)
    for path in destination.iterdir():
        path.chmod(0o444)
    print(json.dumps({"prepared": 48, "contexts": 6, "identity": manifest["identity"]}))


if __name__ == "__main__":
    main()
