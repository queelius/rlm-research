"""Seal only after the score-blind checkpoint2 readout lifecycle/cost gate."""
import time
import continuation_study as study


def build_ready():
    campaign = study.read(study.ROOT / "CAMPAIGN.json")
    gate = study.readout_gate()
    if not gate["run"]:
        raise ValueError(gate["reason"])
    return {"schema": "root-composed-rl-sparse-continuation-ready-v1",
            "identity": campaign["identity"],
            "campaign_sha256": study.sha(study.ROOT / "CAMPAIGN.json"),
            "checkpoint2_policy": study.checkpoint2_policy(), "readout_gate": gate,
            "training_attempt": str(study.ATTEMPT),
            "conditional_readout_attempt": str(study.READOUT_ATTEMPT),
            "owner_python": str(study.NATIVE), "gpu_launched": False,
            "created_epoch": time.time()}


if __name__ == "__main__":
    ready = build_ready()
    study.write(study.ROOT / "READY.json", ready)
    print(ready["identity"])
