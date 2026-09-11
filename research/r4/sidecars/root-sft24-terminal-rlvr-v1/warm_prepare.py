"""Deterministically construct the fixed192 training and paired composition96 readout."""
import copy
import functools
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import warm_study as study


def _jsons(root):
    return {path.name: json.loads(path.read_text()) for path in Path(root).glob("*.json")}


def composition_inputs():
    return _jsons(study.COMPOSITION / "inputs")


def _protocol():
    path = study.SIDE / "root-operator-diverse-sft-v1/od_protocol.py"
    if study.sha(path) != "1ee6f9c71addfbf4f6e5f47f52ea2547bddf5cb8979d67ffb86cd3e88adc5acc":
        raise ValueError("current clarified question source changed")
    spec = importlib.util.spec_from_file_location("warm_qualified_od_protocol", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _new_id(kind, old, seed):
    return hashlib.sha256(f"sft24-terminal-rlvr-v1|{kind}|{old}|{seed}".encode()).hexdigest()


@functools.lru_cache(maxsize=1)
def _build_inputs():
    qsr = _jsons(study.QSR / "inputs")
    comp = composition_inputs()
    protocol = _protocol()
    training, tasks = {}, {}
    old_training = qsr["PLANS.json"]["training"]
    seed = 981731101
    for window in range(1, 9):
        rows = []
        for old in old_training[str(window)]:
            row = copy.deepcopy(old)
            row.update(source_coordinate_id=old["id"], seed=seed,
                       namespace="sft24-terminal-rlvr-training-v1")
            row["id"] = _new_id("training", old["id"], seed)
            seed += 1
            rows.append(row)
            query = copy.deepcopy(qsr["QUERIES.json"][row["task_name"]])
            question = protocol.question(query, window % 4)
            tasks[row["task_name"]] = {**query, "question": question,
                                       "source": "current clarified operator question"}
        training[str(window)] = rows
    readout, prompts = [], {}
    for index, old in enumerate(comp["FREE_PLAN.json"]):
        seed = 981732101 + index
        row = copy.deepcopy(old)
        row.update(source_coordinate_id=old["id"], seed=seed,
                   namespace="sft24-terminal-rlvr-readout-v1")
        row["id"] = _new_id("readout", old["id"], seed)
        readout.append(row)
        prompts[row["id"]] = copy.deepcopy(comp["PROMPTS_ACCURATE.json"][old["id"]])
        tasks[row["task_name"]] = {"question": row["question"], "operator": row["operator"],
                                   "scope": row["scope"], "first_prompt_token_ids": prompts[row["id"]]["token_ids"]}
    evaluation = [{"policy": policy, "coordinate": copy.deepcopy(row), "available": False}
                  for policy in ("unchanged", "trained") for row in readout]
    train_ids = {f"training-{index:02d}" for index in range(8)}
    public = [copy.deepcopy(row) for row in qsr["PUBLIC.json"] if row["id"] in train_ids]
    public += copy.deepcopy(comp["PUBLIC.json"])
    host = {key: copy.deepcopy(value) for key, value in qsr["HOST_GOLD.json"].items() if key in train_ids}
    host.update(copy.deepcopy(comp["HOST_GOLD.json"]))
    groups = [copy.deepcopy(row) for row in qsr["GROUPS.json"] if row["id"] in train_ids]
    groups += copy.deepcopy(comp["GROUPS.json"])
    # Bind every training task to its actual current native first prefix, not the old QSR wording.
    import warm_native
    by_context = {row["id"]: row for row in public}
    for rows in training.values():
        for row in rows:
            task = tasks[row["task_name"]]
            if "first_prompt_token_ids" not in task:
                native_task = warm_native.make_task(by_context[row["context_id"]], task["question"],
                                                    0, row["task_name"])
                task["first_prompt_token_ids"] = warm_native.first_prefix(native_task)
    return {
        "PLANS.json": {"training": training, "readout": readout, "evaluation": evaluation,
                       "planned_training": 192, "planned_readout": 96},
        "TASKS.json": tasks, "PUBLIC.json": public, "HOST_GOLD.json": host,
        "GROUPS.json": groups, "PROMPTS_ACCURATE.json": prompts,
        "NATIVE_TEMPLATE.json": copy.deepcopy(comp["NATIVE_TEMPLATE.json"]),
        "PROVENANCE.json": {
            "qsr_ready_sha256": study.sha(study.QSR / "READY.json"),
            "composition_ready_sha256": study.sha(study.COMPOSITION / "READY.json"),
            "composition_outcomes_used": False,
            "readout_status": "research-exposed exploratory panel",
            "training_contexts": sorted(train_ids), "training_eval_overlap": False,
            "selection": "first eight fixed QSR training contexts; no model-outcome filtering",
        },
    }


def build_inputs():
    return copy.deepcopy(_build_inputs())


def seed_collisions(candidates, catalog):
    found = set()
    def visit(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in {"seed", "master_seed"} and type(child) is int and child in candidates:
                    found.add(child)
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)
    visit(catalog)
    return sorted(found)


def write_inputs(target):
    target = Path(target)
    target.mkdir(parents=True, exist_ok=False)
    values = build_inputs()
    for name, value in values.items():
        with (target / name).open("x") as handle:
            json.dump(value, handle, sort_keys=True, indent=2, allow_nan=False)
            handle.write("\n")
    return len(values)
