"""Additive batch-size16 variant of the completed fixed-leaf composition control."""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent / "fixed-leaf-composition-v1"
loader = importlib.util.spec_from_file_location("fixed_batch_helpers", BASE / "driver.py")
fixed = importlib.util.module_from_spec(loader)
loader.loader.exec_module(fixed)


def make_spec():
    spec = json.loads((BASE / "SPEC.json").read_text())
    fixed.verify_inputs(spec)
    design = spec["design"]
    contexts = {c["id"]: c for c in design["contexts"]}
    tasks = {t["name"]: t for t in design["tasks"]}
    batches, by_context = [], {}
    for context in contexts.values():
        by_context[context["id"]] = []
        for start in range(0, 64, 16):
            rows = context["records"][start : start + 16]
            batch_id = len(batches)
            by_context[context["id"]].append(batch_id)
            batches.append(
                {
                    "batch_id": batch_id,
                    "context_id": context["id"],
                    "record_indices": list(range(start + 1, start + 17)),
                    "question_group_ids": [r["group_id"] for r in rows],
                    "questions": [r["question"] for r in rows],
                    "gold": [r["gold"] for r in rows],
                }
            )
    plan = []
    for coordinate in design["coordinates"]:
        context_id = tasks[coordinate["task_name"]]["context_id"]
        for index, batch_id in enumerate(by_context[context_id]):
            row = {
                "coordinate_id": coordinate["id"],
                "pair_id": coordinate["pair_id"],
                "task_name": coordinate["task_name"],
                "context_id": context_id,
                "arm": coordinate["arm"],
                "seed": coordinate["seed"],
                "repeat": coordinate["repeat"],
                "batch_id": batch_id,
                "batch_index": index,
                "batch_size": 16,
                "dispatch_order": len(plan),
            }
            row["id"] = fixed.leaf.digest([ROOT.name, coordinate["id"], index])
            plan.append(row)
    design.update(batches=batches, plan=plan, batch_size=16)
    spec.update(
        schema=ROOT.name,
        parent_spec_sha256=fixed.leaf.file_hash(BASE / "SPEC.json"),
        intervention="Batch16 versus parent batch5; all64 records and parent seeds preserved",
        call_plan_sha256=fixed.leaf.digest(plan),
        request_sha256={r["id"]: fixed.leaf.digest(fixed.make_request(design, r)) for r in plan},
    )
    paths = (Path(__file__), ROOT / "test_driver.py", ROOT / "DESIGN.md", BASE / "SPEC.json")
    spec["source_file_sha256"].update({str(p): fixed.leaf.file_hash(p) for p in paths})
    fixed.verify_inputs(spec)
    return spec


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "run"))
    args = parser.parse_args()
    spec = make_spec()
    path = ROOT / "SPEC.json"
    if args.command == "prepare":
        fixed.leaf.write_once(path, spec)
        print(json.dumps({"prepared": 192, "spec_sha256": fixed.leaf.file_hash(path)}))
    else:
        if json.loads(path.read_text()) != spec:
            raise ValueError("frozen batch16 inputs changed")
        fixed.ROOT = ROOT  # Process-local summary name only; source files remain untouched.
        raise SystemExit(asyncio.run(fixed.run(path, ROOT / "outputs/attempt-001")))


if __name__ == "__main__":
    main()
