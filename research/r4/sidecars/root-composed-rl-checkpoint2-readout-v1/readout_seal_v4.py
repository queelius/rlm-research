"""Seal attempt-002 against the exact completed checkpoint-2 decision."""
import time

import readout_study_v4 as study


def build_ready(created_epoch=None):
    campaign = study.read(study.ROOT / "CAMPAIGN_V4.json")
    decision = study.checkpoint2_decision()
    if not decision["run"]:
        raise ValueError(decision["reason"])
    return {
        "schema": "root-composed-rl-checkpoint2-readout-ready-v4",
        "identity": campaign["identity"],
        "campaign_sha256": study.sha(study.ROOT / "CAMPAIGN_V4.json"),
        "attempt": str(study.ATTEMPT),
        "checkpoint2": {
            "policy": decision["policy"],
            "owner_terminal_sha256": decision["owner_terminal_sha256"],
            "state_sha256": decision["state_sha256"],
        },
        "required_python": str(study.NATIVE),
        "created_epoch": time.time() if created_epoch is None else created_epoch,
        "gpu_launched": False,
    }


if __name__ == "__main__":
    ready = build_ready()
    study.write(study.ROOT / "READY_V4.json", ready)
    print(ready["identity"])
