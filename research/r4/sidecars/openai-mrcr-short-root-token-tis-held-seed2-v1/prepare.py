"""Freeze the second paired seed block without model or GPU calls."""

from __future__ import annotations

import json
import os
from pathlib import Path
import time

import owner
import study


def _add(closure: dict[str, str], path: Path) -> None:
    path = Path(path)
    expected = study.sha(path)
    raw = str(path)
    if raw in closure and closure[raw] != expected:
        raise ValueError("closure sources disagree: " + raw)
    closure[raw] = expected


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("CPU-only preparation requires hidden CUDA")
    if study.READY.exists() or any(path.exists() for path in owner.STAGES.values()):
        raise FileExistsError("READY or fixed output already exists")
    qualified = study.verify_frozen_inputs()
    inputs = study.prepare_inputs()
    reference = study._load_base()
    old_schedule = {row["record_id"]: row for row in reference.schedule("held")}
    new_schedule = {row["record_id"]: row for row in study.schedule("held")}
    old_prefixes = study.read(reference.input_dir("held") / "PREFIXES.json")
    new_prefixes = study.read(study.input_dir("held") / "PREFIXES.json")
    prefix_pairs = []
    for record_id in old_schedule:
        old = old_prefixes[old_schedule[record_id]["id"]]
        new = new_prefixes[new_schedule[record_id]["id"]]
        if old["token_ids"] != new["token_ids"] or old["task_prompt_sha256"] != new["task_prompt_sha256"]:
            raise ValueError("seed-only replication changed prompt/prefix: " + record_id)
        prefix_pairs.append(
            {
                "record_id": record_id,
                "old_coordinate_id": old_schedule[record_id]["id"],
                "new_coordinate_id": new_schedule[record_id]["id"],
                "token_ids_sha256": new["token_ids_sha256"],
                "task_prompt_sha256": new["task_prompt_sha256"],
            }
        )

    closure = dict(qualified["closure_sha256"])
    _add(closure, study.QUALIFIED / "CPU_READY_V4.json")
    _add(closure, study.QUALIFIED / "checkpoint-artifacts-v2/CHECKPOINT_READY.json")
    for name in (
        "study.py", "checkpoint.py", "collect.py", "owner.py", "prepare.py", "test_seed2.py",
        "QUESTION.md", "RUNBOOK.md",
    ):
        _add(closure, study.ROOT / name)
    for name in ("tasks.json", "PUBLIC.json", "HOST_GOLD.json", "PREFIXES.json"):
        _add(closure, study.input_dir("held") / name)
    for path in sorted((study.input_dir("held") / "contexts").glob("*.json")):
        _add(closure, path)

    ready = {
        "schema": "mrcr-token-tis-held16-seed2-three-arm-cpu-ready-v1",
        "status": "CPU_READY_FIXED_SEED_ONLY_REPLICATION",
        "created_epoch": time.time(),
        "question_sha256": study.sha(study.ROOT / "QUESTION.md"),
        "qualified_source_ready": str(study.QUALIFIED / "CPU_READY_V4.json"),
        "qualified_source_ready_sha256": study.sha(study.QUALIFIED / "CPU_READY_V4.json"),
        "qualified_source_ready_identity": qualified["identity"],
        "checkpoint_receipt": str(study.QUALIFIED / "checkpoint-artifacts-v2/CHECKPOINT_READY.json"),
        "checkpoint_receipt_sha256": study.sha(
            study.QUALIFIED / "checkpoint-artifacts-v2/CHECKPOINT_READY.json"
        ),
        "stage_order": ["base", "lr1e-5", "lr1e-4"],
        "stage_argv": owner.plan()["stage_argv"],
        "inputs": {
            "held": {
                **inputs["held"],
                "seed_namespace": "2026091900-2026091915",
                "seed_range_inclusive": [2026091900, 2026091915],
                "same_records_and_order_as_first_block": True,
                "same_prompts_and_prefix_token_ids_as_first_block": True,
                "prefix_pairs": prefix_pairs,
            }
        },
        "sampling": {
            "temperature": 0.5,
            "max_tokens_per_response": 2048,
            "max_total_root_child_turns": 6,
            "retries": 0,
        },
        "arms": {
            "base": "qualified exact-zero transport adapter",
            "lr1e-5": "fixed independent token-TIS step-one branch",
            "lr1e-4": "fixed independent token-TIS step-one branch",
        },
        "science": {
            "episodes_per_arm": 16,
            "optimizer_steps": 0,
            "checkpoint_selection": False,
            "success_only_subset": False,
            "primary": "paired raw exact with unavailable separate",
            "diagnostics": [
                "raw official similarity", "similarity at least 0.90", "calls and tokens",
                "broad-dump/copy mechanism", "six-total-turn compliance",
            ],
            "prior_panel_exposure": True,
        },
        "caps": {"science_each_seconds": 500, "owner_each_seconds": 650, "external_each_seconds": 700},
        "gpu_calls_in_preparation": 0,
        "launch_authority": "MAIN only",
        "closure_sha256": closure,
    }
    ready["identity"] = study.digest(ready)
    study.write_x(study.READY, ready)
    print(
        json.dumps(
            {"ready": str(study.READY), "sha256": study.sha(study.READY), "identity": ready["identity"]},
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
