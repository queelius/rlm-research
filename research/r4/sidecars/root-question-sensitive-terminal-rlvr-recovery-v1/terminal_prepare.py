"""Deterministically freeze composed48 x four samples and protected72 readout."""
import copy
import functools
import hashlib
import json
from pathlib import Path

import terminal_study as study
import terminal_native as native

COMPOSED = {"T1", "T2", "M1", "M2", "J1", "J2"}


def new_id(kind, source_id, seed):
    return hashlib.sha256(f"question-sensitive-terminal-rlvr-v1|{kind}|{source_id}|{seed}".encode()).hexdigest()


@functools.lru_cache(maxsize=1)
def _build_inputs():
    source = study.QS / "inputs"
    train = study.read(source / "TRAIN_PLAN.json")
    protected = study.read(source / "FREE_PLAN.json")
    prompts = study.read(source / "PROMPTS_ACCURATE.json")
    public_all = study.read(source / "PUBLIC.json")
    gold_all = study.read(source / "HOST_GOLD.json")
    groups_all = study.read(source / "GROUPS.json")
    contexts = {row["id"]: row for row in public_all}
    by_context = {}
    for row in train:
        if row["slot"] in COMPOSED:
            by_context.setdefault(row["context_id"], []).append(row)
    if len(by_context) != 8 or any(len(rows) != 6 for rows in by_context.values()):
        raise ValueError("exact eight TRAIN contexts x six composed tasks required")
    windows, frozen_prompts, tasks = {}, {}, {}
    for window, context_id in enumerate(sorted(by_context), 1):
        rows = []
        for group, old in enumerate(sorted(by_context[context_id], key=lambda r: r["slot"])):
            for repeat in range(4):
                seed = study.SEED + window * 100 + group * 4 + repeat
                row = copy.deepcopy(old)
                row.update(source_coordinate_id=old["id"], source_split=old["split"],
                           split="training", seed=seed, repeat=repeat,
                           namespace="question-sensitive-terminal-rlvr-train-v1")
                row["id"] = new_id("train", old["id"], seed)
                rows.append(row)
                frozen_prompts[row["id"]] = copy.deepcopy(prompts[old["id"]])
                task = native.make_task(contexts[row["context_id"]], row["question"],
                                        gold_all[row["context_id"]]["answers"][row["family"]],
                                        row["task_name"])
                prefix = native.first_prefix(task)
                if prefix != prompts[old["id"]]["token_ids"]:
                    raise ValueError("actual native prefix differs from frozen QS prompt")
                tasks[row["task_name"]] = {
                    "question": row["question"],
                    "prompt": task.data.prompt,
                    "task_hash": task.hash,
                    "first_prompt_token_ids": prefix,
                    "operator": row["operator"],
                    "scope": row["scope"],
                    "threshold": row["threshold"],
                }
        windows[str(window)] = rows
    readout = []
    for index, old in enumerate(protected):
        seed = 990732000 + index
        row = copy.deepcopy(old)
        row.update(source_coordinate_id=old["id"], seed=seed,
                   namespace="question-sensitive-terminal-rlvr-readout-v1")
        row["id"] = new_id("readout", old["id"], seed)
        readout.append(row)
        frozen_prompts[row["id"]] = copy.deepcopy(prompts[old["id"]])
        task = native.make_task(contexts[row["context_id"]], row["question"],
                                gold_all[row["context_id"]]["answers"][row["family"]],
                                row["task_name"])
        prefix = native.first_prefix(task)
        if prefix != prompts[old["id"]]["token_ids"]:
            raise ValueError("actual native prefix differs from frozen QS prompt")
        tasks[row["task_name"]] = {
            "question": row["question"],
            "prompt": task.data.prompt,
            "task_hash": task.hash,
            "first_prompt_token_ids": prefix,
            "operator": row["operator"],
            "scope": row["scope"],
            "threshold": row["threshold"],
        }
    evaluation = [
        {"policy": policy, "coordinate": copy.deepcopy(row), "available": False}
        for policy in ("start", "rl_last") for row in readout
    ]
    contexts = set(by_context) | {row["context_id"] for row in readout}
    public = [copy.deepcopy(row) for row in public_all if row["id"] in contexts]
    gold = {key: copy.deepcopy(value) for key, value in gold_all.items() if key in contexts}
    groups = [copy.deepcopy(row) for row in groups_all if row["id"] in contexts]
    return {
        "PLANS.json": {"training": windows, "readout": readout, "evaluation": evaluation,
                       "planned_training": 192, "planned_readout": 144},
        "TASKS.json": tasks,
        "PROMPTS_ACCURATE.json": frozen_prompts,
        "PUBLIC.json": public,
        "HOST_GOLD.json": gold,
        "GROUPS.json": groups,
        "NATIVE_TEMPLATE.json": study.read(source / "NATIVE_TEMPLATE.json"),
        "PROVENANCE.json": {
            "selection_path": str(study.SELECTION),
            "selection_sha256": study.sha(study.SELECTION),
            "qs_ready_sha256": study.sha(study.QS / "READY.json"),
            "training_selection": "all composed T1/T2/M1/M2/J1/J2 on all eight TRAIN contexts",
            "samples_per_task": 4,
            "protected_selection": "all fixed 72; start versus fixed-last RL; no selection",
            "training_protected_disjoint": True,
            "outcomes_used": False,
        },
    }


def build_inputs():
    return copy.deepcopy(_build_inputs())


def write_inputs(target):
    target = Path(target)
    target.mkdir(parents=True, exist_ok=False)
    values = build_inputs()
    for name, value in values.items():
        with (target / name).open("x") as handle:
            json.dump(value, handle, indent=2, sort_keys=True, allow_nan=False)
            handle.write("\n")
    return values
