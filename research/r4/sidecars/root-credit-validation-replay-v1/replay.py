"""Exact eight-coordinate unchanged-weight validation replay; no training or server startup."""

import argparse
import asyncio
import copy
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PHASE1 = ROOT.parent / "root-only-credit-v1"
PHASE1_SPEC_SHA = "bc38dadf55e6a45cd7c9a417cdafbc52a50494c3bfb6991752e7d0e500a8c4ed"
sys.path.insert(0, str(PHASE1))
loader = importlib.util.spec_from_file_location("root_validation_phase1", PHASE1 / "capture.py")
phase1 = importlib.util.module_from_spec(loader)
sys.modules[loader.name] = phase1
loader.loader.exec_module(phase1)
ORIGINAL_VERIFY = phase1.verify
ORIGINAL_TASKS = phase1.make_tasks
SPEC = ROOT / "SPEC_ORIGINAL.json"


def validation_subset(source):
    plan = copy.deepcopy([row for row in source["plan"] if row["split"] == "validation"])
    names = {row["task_name"] for row in plan}
    tasks = copy.deepcopy([task for task in source["tasks"] if task["name"] in names])
    if len(plan) != 8 or len(names) != 4 or len(tasks) != 4 or len({r["context_window_id"] for r in plan}) != 2:
        raise ValueError("expected exactly8 frozen validation coordinates on4 tasks/two contexts")
    return plan, tasks


def validate_original_identity(source, endpoint, binding):
    expected_binding = copy.deepcopy(source["role_binding"])
    expected_binding.pop("fixed_child")
    if endpoint != source["source_endpoint_descriptor"] or binding != expected_binding:
        raise ValueError("unchanged-weight replay requires exact Phase1 endpoint and original-root/selected-child binding")


def authenticated_inputs(endpoint_path, binding_path):
    if phase1.file_hash(PHASE1 / "SPEC.json") != PHASE1_SPEC_SHA:
        raise ValueError("frozen Phase1 spec changed")
    source = ORIGINAL_VERIFY()
    endpoint, binding = phase1.read(endpoint_path), phase1.read(binding_path)
    validate_original_identity(source, endpoint, binding)
    return source, endpoint, binding


def prepare(endpoint_path, binding_path):
    source, endpoint, binding = authenticated_inputs(endpoint_path, binding_path)
    plan, tasks = validation_subset(source)
    spec = copy.deepcopy(source)
    spec.update(schema=ROOT.name + "-original", plan=plan, tasks=tasks,
        plan_sha256=phase1.digest(plan), coordinate_plan_sha256=phase1.digest(plan),
        replay_condition="unchanged_original_root_and_selected_child",
        interpretation="Exact seed/prompt/weight replay estimates whole-trajectory variability, not a learning effect.",
        training_policy="Validation only. No training-group export or optimization.",
        inherited_record_schema="root-only-credit-v1-episode (collector unchanged; condition is explicit in this spec)",
        phase1_spec_sha256=PHASE1_SPEC_SHA,
        explicit_launch_binding={"endpoint_path": str(endpoint_path), "endpoint_sha256": phase1.file_hash(endpoint_path),
                                 "binding_path": str(binding_path), "binding_sha256": phase1.file_hash(binding_path)},
        prompt_seed_role_and_capture_change=False,
        selection="Exact source-spec split=validation predicate; no trajectory/score/outcome access.")
    for path in (Path(__file__), ROOT / "test_replay.py", PHASE1 / "SPEC.json", endpoint_path, binding_path):
        spec["source_file_sha256"][str(path)] = phase1.file_hash(path)
    phase1.write_once(SPEC, spec)
    SPEC.chmod(0o444)
    return spec


def verify(endpoint_path, binding_path):
    source, endpoint, binding = authenticated_inputs(endpoint_path, binding_path)
    spec = phase1.read(SPEC)
    for path, expected in spec["source_file_sha256"].items():
        if phase1.file_hash(path) != expected:
            raise ValueError(f"pinned replay source/binding changed: {path}")
    plan, tasks = validation_subset(source)
    if spec["plan"] != plan or spec["tasks"] != tasks or spec["plan_sha256"] != phase1.digest(plan):
        raise ValueError("replay coordinate/task identity changed")
    declared = spec["explicit_launch_binding"]
    if (phase1.file_hash(endpoint_path) != declared["endpoint_sha256"]
            or phase1.file_hash(binding_path) != declared["binding_sha256"]):
        raise ValueError("supplied endpoint/binding do not match explicitly frozen replay")
    actual_tasks = ORIGINAL_TASKS()
    for row in plan:
        prompted = phase1.role.with_prompt(actual_tasks[row["task_name"]], "sft_child")
        task_spec = next(task for task in tasks if task["name"] == row["task_name"])
        if (prompted.hash != row["task_hash"] or prompted.hash != task_spec["arms"]["sft_child"]["task_hash"]
                or prompted.data.prompt != task_spec["arms"]["sft_child"]["prompt"]):
            raise ValueError("recreated validation prompt/hash differs from frozen Phase1")
    return spec


async def run(endpoint_path, binding_path, output):
    spec = verify(endpoint_path, binding_path)
    names = {row["task_name"] for row in spec["plan"]}
    tasks = {name: task for name, task in ORIGINAL_TASKS().items() if name in names}
    original_verify, original_tasks = phase1.verify, phase1.make_tasks
    try:
        # In this fresh process only, delegate the qualified collector over the exact subset.
        phase1.verify = lambda: copy.deepcopy(spec)
        phase1.make_tasks = lambda: tasks
        return await phase1.run(output)
    finally:
        phase1.verify, phase1.make_tasks = original_verify, original_tasks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("prepare-original", "verify-original", "run-original"))
    parser.add_argument("--endpoint", type=Path, required=True)
    parser.add_argument("--binding", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/original-replay-attempt-001")
    args = parser.parse_args()
    endpoint, binding = args.endpoint.resolve(), args.binding.resolve()
    if args.command == "run-original":
        raise SystemExit(asyncio.run(run(endpoint, binding, args.output.resolve())))
    spec = prepare(endpoint, binding) if args.command == "prepare-original" else verify(endpoint, binding)
    print(json.dumps({"planned": len(spec["plan"]), "condition": spec["replay_condition"], "plan_sha256": spec["plan_sha256"], "gpu_calls": 0}))


if __name__ == "__main__":
    main()
