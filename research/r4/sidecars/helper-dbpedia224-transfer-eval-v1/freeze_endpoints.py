"""Freeze MAIN's four named checkpoints before any DBpedia model query."""

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
    official = study.OFFICIAL_SOURCE / "ENDPOINTS_FIXED.json"
    value = {
        "schema": "helper-dbpedia224-transfer-fixed-endpoints-v1",
        "authority": "MAIN",
        "decision_source": (
            "explicit instruction to evaluate c32, RL8 seed1, SFT8, and RL8 seed2; no selection"
        ),
        "created_epoch": time.time(),
        "evaluation_data_ready_sha256": study.sha(study.EVAL_DATA / "DATA_READY.json"),
        "evaluation_schedule_sha256": study.digest(study.schedule()),
        "new_dbpedia_model_calls_before_fix": 0,
        "checkpoint_selection": "none; exact four named completed checkpoints",
        "trained_endpoints": endpoints,
        "official_test_endpoint_receipt": str(official),
        "official_test_endpoint_receipt_sha256": study.sha(official),
        "checkpoint_training_inputs_separate_from_evaluation_inputs": True,
    }
    study.write_x(study.ROOT / "ENDPOINTS_FIXED.json", value)
    print(json.dumps({"sha256": study.sha(study.ROOT / "ENDPOINTS_FIXED.json"), "arms": list(endpoints)}))


if __name__ == "__main__":
    main()

