"""Seal V2 only after the unchanged score-blind checkpoint2 readout gate."""
import time
import continuation_study_v2 as study


def build_ready():
    campaign = study.read(study.ROOT / "CAMPAIGN_V2.json")
    gate = study.readout_gate()
    if not gate["run"]:
        raise ValueError(gate["reason"])
    return {"schema": "root-composed-rl-sparse-continuation-ready-v2",
            "identity": campaign["identity"],
            "campaign_sha256": study.sha(study.ROOT / "CAMPAIGN_V2.json"),
            "checkpoint2_policy": study.checkpoint2_policy(), "readout_gate": gate,
            "training_attempt": str(study.ATTEMPT),
            "conditional_readout_attempt": str(study.READOUT_ATTEMPT),
            "owner_python": str(study.NATIVE), "trainer_python": str(study.TRAIN),
            "created_epoch": time.time(), "gpu_launched": False}


if __name__ == "__main__":
    ready = build_ready()
    study.write(study.ROOT / "READY_V2.json", ready)
    print(ready["identity"])
