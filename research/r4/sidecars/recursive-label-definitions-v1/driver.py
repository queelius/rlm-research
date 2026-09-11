"""Matched full-RLM executable examples with/without public child-label definitions.

Three reused development questions, two fresh paired seeds, original4B weights.
No grammar, forced plan, gold hints, weight updates or root-parser changes. This
tests a prompt intervention visible to root and child, not isolated leaf routing.
"""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
import os
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OLD = ROOT.parent / "recursive-call-example-v1/driver.py"
LEAF = ROOT.parent / "trec-leaf-contract-probe-v1/driver.py"
ENDPOINT = ROOT.parents[1] / "operations/2026-09-08-resume/inference-frozen-contract-attempt-001/endpoint.json"
ARMS = {"abstract": "example_only", "example": "example_definitions"}


def load(name, path):
    loader = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(module)
    return module


old = load("original_example_helpers", OLD)
leaf = load("original_leaf_helpers", LEAF)
original_code = old.EXAMPLE_CODE


def example_code(arm):
    if arm == "example_only":
        return original_code
    if arm != "example_definitions":
        raise ValueError("unknown definitions arm")
    code = original_code.replace(
        "child = await rlm(", "definitions = " + repr(leaf.DEFINITIONS) + "\nchild = await rlm(", 1
    )
    before = '"numeric value.\\n" + json.dumps(batch)'
    after = '"numeric value.\\n" + definitions + "\\n" + json.dumps(batch)'
    if before not in code:
        raise ValueError("frozen executable example changed")
    return code.replace(before, after, 1)


def with_prompt(task, arm):
    arm = ARMS.get(arm, arm)
    base_task = old.original_prompt(task, "procedure")
    example = (
        "Executable API example for the first four context records (a starting batch, "
        "not the final answer). You can run this in ipython:\n```python\n"
        + example_code(arm)
        + "\n```\nContinue covering the remaining relevant records and compute the aggregate "
        "requested by the question."
    )
    marker = "\n\nQuestion: "
    if base_task.data.prompt.count(marker) != 1:
        raise ValueError("question boundary changed")
    text = base_task.data.prompt.replace(marker, "\n\n" + example + marker, 1)
    return type(task)(base_task.data.model_copy(update={"prompt": text}), task.config)


def summarize(records, plan):
    result = old.original_summary(records, plan)
    pairs = defaultdict(dict)
    for record in records:
        pairs[record["coordinate"]["pair_id"]][record["coordinate"]["arm"]] = record["derived"]
    result["paired"] = []
    for key, arms in pairs.items():
        if set(arms) == set(ARMS.values()):
            left, right = arms["example_only"], arms["example_definitions"]
            observable = left["strict_reward"] is not None and right["strict_reward"] is not None
            result["paired"].append({"pair_id": key, "both_observable": observable,
                "strict_success_definitions_minus_control": right["strict_reward"] - left["strict_reward"] if observable else None,
                "recursion_definitions_minus_control": int(right["actual_recursive_model_call"]) - int(left["actual_recursive_model_call"])})
    for cell in result["cells"]:
        rows = [r["derived"] for r in records if r["coordinate"]["arm"] == cell["arm"]]
        for field in ("actual_recursive_model_call", "committed_subagent_call_edges", "committed_subagent_return_edges"):
            cell[field] = sum(row[field] for row in rows)
    result["caution"] = "One reused development context, three questions, six pairs; not transfer or training. Definitions are also visible to the root."
    return result


def make_spec():
    old.STUDY = ROOT.name
    old.with_prompt = with_prompt
    frozen, tasks = old.make_spec(ENDPOINT, "pre_update")
    for task in frozen["tasks"]:
        task["arms"] = {ARMS[key]: value for key, value in task["arms"].items()}
    plan = frozen["plan"]
    for row in plan:
        row["arm"] = ARMS[row["arm"]]
        row["group_id"] = old.q.digest([ROOT.name, row["task_name"], row["arm"]])
        row.pop("id")
        row["id"] = old.q.digest(row)
    assert len(plan) == 12 and len({r["id"] for r in plan}) == 12
    assert len({r["pair_id"] for r in plan}) == 6
    frozen.update(
        plan_sha256=old.q.digest(plan),
        interpretation=__doc__,
        primary_outcome="Strict final correctness; actual child-definition use, canonical leaf accuracy and faithful aggregation are mechanism diagnostics.",
        executable_examples={arm: example_code(arm) for arm in ARMS.values()},
        definitions=leaf.DEFINITIONS,
    )
    frozen.pop("example_code", None)
    frozen["source_file_sha256"].update({str(p): old.q.file_hash(p) for p in (Path(__file__), LEAF, ROOT / "test_driver.py")})
    old.validate_runtime_spec(frozen)
    return frozen, tasks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true")
    args = parser.parse_args()
    spec, tasks = make_spec()
    path = ROOT / "SPEC.json"
    if args.prepare:
        if path.exists():
            raise ValueError("spec already exists")
        old.q.atomic_json(path, spec)
        print(json.dumps({"prepared": 12, "sha256": old.q.file_hash(path)}), flush=True)
        return 0
    if json.loads(path.read_text()) != spec:
        raise ValueError("frozen inputs changed")
    os.environ["PATH"] = str(old.q.ROOTLESS / "bin") + os.pathsep + os.environ.get("PATH", "")
    os.environ.setdefault("VERIFIERS_CACHE_DIR", "/project/alex_phd/cache/verifiers-prime")
    old.base.STUDY = ROOT.name
    old.base.with_prompt = with_prompt
    old.base.crossover_metrics = old.example_metrics
    old.base.summarize = summarize
    run_args = argparse.Namespace(endpoint_url=None, output_dir=ROOT / "outputs/attempt-001", resume=False)
    return asyncio.run(old.base.run(run_args, spec, tasks))


if __name__ == "__main__":
    raise SystemExit(main())
