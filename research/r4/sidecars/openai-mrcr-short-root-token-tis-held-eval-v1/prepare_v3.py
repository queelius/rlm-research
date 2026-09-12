"""Seal the additive V3 inherited-interface/provenance repair."""

from __future__ import annotations

import json
import os
from pathlib import Path
import time

import owner_v3 as owner
import study_v3 as study


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("CPU-only preparation requires hidden CUDA")
    if study.READY.exists() or any(path.exists() for path in owner.STAGES.values()):
        raise FileExistsError("V3 READY or output already exists")
    source_ready = study.verify_frozen_inputs()
    training_ready_path = study.TRAINING / "CPU_READY_V2.json"
    training_ready = study.read(training_ready_path)
    local_names = (
        "study_v3.py", "checkpoint_v3.py", "collect_v3.py", "owner_v3.py",
        "prepare_v3.py", "test_eval_v3.py", "study_v2.py", "checkpoint_v2.py",
        "collect_v2.py", "owner_v2.py", "prepare_v2.py", "test_eval_v2.py",
        "REPAIR_V2.md", "CPU_READY_V2.json", "CPU_READY.json", "study.py",
        "checkpoint.py", "collect.py", "owner.py", "prepare.py", "test_eval.py",
        "DESIGN.md", "RUNBOOK.md",
    )
    paths = [study.ROOT / name for name in local_names]
    paths.extend(
        [
            training_ready_path,
            study.TRAIN_INPUTS,
            study.SOURCE_EVAL / "CPU_READY.json",
            study.SOURCE_EVAL / "study.py",
            study.SOURCE_EVAL / "checkpoint.py",
            study.SOURCE_EVAL / "collect.py",
            study.SOURCE_EVAL / "owner.py",
        ]
    )
    for name in ("tasks.json", "PUBLIC.json", "HOST_GOLD.json", "PREFIXES.json"):
        paths.append(study.input_dir("held") / name)
    paths.extend(sorted((study.input_dir("held") / "contexts").glob("*.json")))
    closure = dict(source_ready["closure_sha256"])
    for raw, expected in training_ready["closure_sha256"].items():
        if raw in closure and closure[raw] != expected:
            raise ValueError("parent closures disagree: " + raw)
        closure[raw] = expected
    closure.update({str(path): study.sha(path) for path in paths})
    plan = owner.plan()
    ready = {
        "schema": "mrcr-token-tis-held16-three-arm-cpu-ready-v3",
        "status": "CPU_READY_CONDITIONAL_ON_TWO_INDEPENDENT_STEP1_BRANCHES_V3",
        "created_epoch": time.time(),
        "supersedes_unlaunched_ready": str(study.ROOT / "CPU_READY_V2.json"),
        "superseded_ready_sha256": study.sha(study.ROOT / "CPU_READY_V2.json"),
        "v2_reason": "its hashed fake fixture was corrected after sealing; no GPU launch occurred",
        "training_ready_sha256": study.sha(training_ready_path),
        "training_ready_identity": training_ready["identity"],
        "stage_argv": plan["stage_argv"],
        "stage_order": ["base", "lr1e-5", "lr1e-4"],
        "inputs": {
            "held": {
                "episodes": 16,
                "schedule_sha256": study.digest(study.schedule("held")),
                "source_held_ready_sha256": study.sha(study.SOURCE_EVAL / "CPU_READY.json"),
                "reused_exact_coordinates": True,
            }
        },
        "checkpoint_gate": {
            "both_independent_step1_commits": True,
            "result_state_commit_links": True,
            "initial_tensor_identity": True,
            "initial_rng_and_saved_gradient_hashes": True,
            "result_linked_10x_relation": True,
            "both_postupdate_likelihood_inventories": True,
            "checkpoint_selection": False,
        },
        "sampling": {"temperature": 0.5, "max_tokens": 2048, "max_total_turns": 6,
                     "retries": 0, "workers": 4},
        "metrics": {
            "primary": "paired raw exact",
            "diagnostic": ["raw official similarity", "similarity>=0.90", "shaped reward",
                           "availability", "native calls and tokens"],
            "newline_or_output_repair": None,
        },
        "caps": {"science_each": 500, "owner_each": 650, "external_each": 700},
        "held_panel_prior_exposure": "procedural-SFT evaluation used these contexts separately",
        "gpu_calls_in_preparation": 0,
        "optimizer_steps_in_evaluator": 0,
        "closure_sha256": closure,
        "launch_authority": "MAIN only",
    }
    ready["identity"] = study.digest(ready)
    study.write_x(study.READY, ready)
    print(json.dumps({"ready": str(study.READY), "sha256": study.sha(study.READY),
                      "identity": ready["identity"]}, sort_keys=True))


if __name__ == "__main__":
    main()

