"""Additive singleton/whole-document variants of the fixed-leaf operator."""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent / "fixed-leaf-composition-v1"
loader = importlib.util.spec_from_file_location("fixed_endpoint_helpers", BASE / "driver.py")
fixed = importlib.util.module_from_spec(loader)
loader.loader.exec_module(fixed)


def make_spec(size: int) -> dict:
    if size not in (1, 64):
        raise ValueError("batch size must be one or sixty-four")
    spec = json.loads((BASE / "SPEC.json").read_text())
    fixed.verify_inputs(spec)
    design = spec["design"]
    tasks = {t["name"]: t for t in design["tasks"]}
    batches, by_context = [], {}
    for context in design["contexts"]:
        by_context[context["id"]] = []
        if len(context["records"]) != 64:
            raise ValueError("expected frozen 64-record contexts")
        for start in range(0, 64, size):
            records = context["records"][start : start + size]
            batch_id = len(batches)
            by_context[context["id"]].append(batch_id)
            batches.append(
                {
                    "batch_id": batch_id,
                    "context_id": context["id"],
                    "record_indices": list(range(start + 1, start + size + 1)),
                    "question_group_ids": [r["group_id"] for r in records],
                    "questions": [r["question"] for r in records],
                    "gold": [r["gold"] for r in records],
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
                "batch_size": size,
                "dispatch_order": len(plan),
            }
            row["id"] = fixed.leaf.digest([ROOT.name, size, coordinate["id"], index])
            plan.append(row)
    design.update(
        batches=batches,
        plan=plan,
        batch_size=size,
        max_tokens=1024,
        call_timeout_seconds=60,
    )
    spec.update(
        schema=ROOT.name,
        parent_spec_sha256=fixed.leaf.file_hash(BASE / "SPEC.json"),
        intervention=f"Batch{size}; all 64 records and parent seeds preserved; output cap1024",
        call_plan_sha256=fixed.leaf.digest(plan),
        request_sha256={r["id"]: fixed.leaf.digest(fixed.make_request(design, r)) for r in plan},
        contract_caution=(
            "Fixed first-response operator; cap1024 versus parent256, not exact "
            "full-RLM replay or equal-budget causal intervention."
        ),
    )
    paths = (Path(__file__), ROOT / "test_driver.py", ROOT / "DESIGN.md", BASE / "SPEC.json")
    spec["source_file_sha256"].update({str(p): fixed.leaf.file_hash(p) for p in paths})
    fixed.verify_inputs(spec)
    return spec


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "run"))
    parser.add_argument("--size", type=int, choices=(1, 64), required=True)
    args = parser.parse_args()
    spec = make_spec(args.size)
    path = ROOT / f"SPEC-B{args.size:03d}.json"
    if args.command == "prepare":
        fixed.leaf.write_once(path, spec)
        print(
            json.dumps(
                {"prepared": len(spec["design"]["plan"]), "spec_sha256": fixed.leaf.file_hash(path)}
            )
        )
    else:
        if json.loads(path.read_text()) != spec:
            raise ValueError("frozen batch endpoint inputs changed")
        fixed.ROOT = ROOT
        output = ROOT / "outputs" / f"batch{args.size:03d}-attempt-001"
        raise SystemExit(asyncio.run(fixed.run(path, output)))


if __name__ == "__main__":
    main()
