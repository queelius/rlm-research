"""Fresh TrainClient rollouts and frozen paired heldout evaluations on an owned endpoint."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import native_prefill_arm as native

base = native.baseline
ROOT = Path(__file__).resolve().parent
_phase = "training"
_temperature = 0.5
EXCLUDED_IDS = {12000008, 12000009, 12000023, 12000029, 12000030, 12000031}


def phase_plans(
    train_names: list[str], eval_names: list[str], temperature: float
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    selected = [name for name in train_names if int(name.rsplit(":", 1)[1]) not in EXCLUDED_IDS]
    if len(selected) != 10 or len(eval_names) != 8 or temperature <= 0:
        raise ValueError("fresh design needs ten uncalibrated train tasks, eight eval tasks, T>0")

    def plan(names: list[str], seeds: range, split: str) -> list[dict[str, Any]]:
        rows = []
        for task_index, task in enumerate(names):
            for repeat, seed in enumerate(seeds):
                identity = {
                    "study": "strict-rlm-fresh-rollouts-v1",
                    "task_name": task,
                    "temperature": temperature,
                    "repeat": repeat,
                    "seed": seed,
                    "split": split,
                    "client_path": "train",
                }
                rows.append(
                    {
                        **identity,
                        "id": base.digest(identity),
                        "pair_id": base.digest([task, temperature, split]),
                        "group_id": base.digest([task, temperature, split]),
                        "pair_order": repeat,
                        "dispatch_order": len(rows),
                        "task_position": task_index,
                    }
                )
        return rows

    return (
        plan(selected, range(950260500, 950260504), "training"),
        plan(eval_names, range(950260600, 950260602), "heldout"),
    )


def load_inputs(args: Any) -> Any:
    from oolong_prime_rlm_strict_v1.taskset import StrictOolongConfig, StrictOolongTaskset

    frozen, _, tasks = native.load_inputs(args)
    evaluation = list(StrictOolongTaskset(StrictOolongConfig(split="eval")).load())
    training_plan, heldout_plan = phase_plans(
        list(tasks), [task.data.name for task in evaluation], _temperature
    )
    tasks.update({task.data.name: task for task in evaluation})
    train_contexts = {tasks[row["task_name"]].data.context_window_id for row in training_plan}
    heldout_contexts = {tasks[row["task_name"]].data.context_window_id for row in heldout_plan}
    if train_contexts != {8} or heldout_contexts != {6} or train_contexts & heldout_contexts:
        raise ValueError("frozen training/heldout context-group separation changed")
    plan = training_plan if _phase == "training" else heldout_plan
    frozen.update(
        {
            "fresh_rollout_design": json.loads((ROOT / "FRESH_RLVR_SPEC.json").read_text()),
            "collection_phase": _phase,
            "temperature": _temperature,
            "plan": plan,
            "coordinate_plan_sha256": base.digest(plan),
            "training_plan": training_plan,
            "heldout_plan": heldout_plan,
            "training_plan_sha256": base.digest(training_plan),
            "heldout_plan_sha256": base.digest(heldout_plan),
            "training_contexts": sorted(train_contexts),
            "heldout_contexts": sorted(heldout_contexts),
            "tasks": [
                {
                    "name": task.data.name,
                    "key": task.key,
                    "hash": task.hash,
                    "context_window_id": task.data.context_window_id,
                }
                for task in tasks.values()
                if task.data.name in {row["task_name"] for row in training_plan + heldout_plan}
            ],
        }
    )
    for path in (
        Path(__file__).resolve(),
        ROOT / "FRESH_RLVR_SPEC.json",
        ROOT / "tests/test_fresh_rlvr.py",
    ):
        frozen["source_file_sha256"][str(path)] = base.file_hash(path)
    return frozen, plan, tasks


def request_metadata(endpoint: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    return {
        **native.request_metadata(endpoint, row),
        "collection_phase": _phase,
        "split": row["split"],
        "fresh_sampler_group": True,
    }


def main() -> int:
    global _phase, _temperature
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--phase", choices=("training", "heldout-before", "heldout-after"), required=True
    )
    parser.add_argument("--temperature", type=float, default=0.5)
    custom, remaining = parser.parse_known_args()
    _phase, _temperature = custom.phase, custom.temperature
    sys.argv = [sys.argv[0], *remaining]
    base.make_context = native.make_context
    base.request_metadata = request_metadata
    base.episode_metrics = native.episode_metrics
    base.load_inputs = load_inputs
    base.summarize = native.summarize
    if not any(arg == "--image-id" or arg.startswith("--image-id=") for arg in remaining):
        design = json.loads((ROOT / "FRESH_RLVR_SPEC.json").read_text())
        sys.argv.extend(["--image-id", design["runtime_image_id"]])
    return base.main()


if __name__ == "__main__":
    raise SystemExit(main())
