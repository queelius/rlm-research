"""Materialize MAIN's explicitly predeclared four endpoint identities once."""

import json
import os
import time

import eligibility
import study


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") not in (None, ""):
        raise ValueError("endpoint freeze is CPU only")
    endpoints = {}
    for arm in study.ARMS:
        receipt = eligibility.qualify(arm)
        endpoints[arm] = {
            key: receipt.get(key)
            for key in ("checkpoint", "state_sha256", "step_commit_sha256", "binding_sha256")
            if receipt.get(key) is not None
        }
    value = {
        "schema": "agnews-official-test-fresh512-fixed-endpoints-v1",
        "authority": "MAIN",
        "decision_source": "explicit 2026-09-12 instruction to include all four completed endpoints independent of impending seed2 score",
        "created_epoch": time.time(),
        "evaluation_data_ready_sha256": study.sha(study.EVAL_DATA / "DATA_READY.json"),
        "evaluation_schedule_sha256": study.digest(study.schedule()),
        "new_panel_model_calls_before_fix": 0,
        "seed2_exposed_panel_score_consulted_before_fix": False,
        "checkpoint_selection": "none; exact named final checkpoints",
        "trained_endpoints": endpoints,
        "training_input_lineage": {
            "c32": {"manifest": str(study.SIDE / "trec-leaf-sft-v1/prepared-v1/MANIFEST.json"), "sha256": study.sha(study.SIDE / "trec-leaf-sft-v1/prepared-v1/MANIFEST.json")},
            "rl_step8": {"manifest": str(study.DATA / "inputs/MANIFEST.json"), "sha256": study.sha(study.DATA / "inputs/MANIFEST.json")},
            "sft_step8": {"manifest": str(study.DATA / "inputs/MANIFEST.json"), "sha256": study.sha(study.DATA / "inputs/MANIFEST.json")},
            "rl_seed2_step8": {"manifest": str(eligibility.SEED2_TRAIN / "SOURCE_INVENTORY.json"), "sha256": study.sha(eligibility.SEED2_TRAIN / "SOURCE_INVENTORY.json")},
        },
        "checkpoint_training_inputs_separate_from_evaluation_inputs": True,
    }
    study.write_x(study.ROOT / "ENDPOINTS_FIXED.json", value)
    print(json.dumps({"sha256": study.sha(study.ROOT / "ENDPOINTS_FIXED.json"), "arms": list(endpoints)}))


if __name__ == "__main__":
    main()

