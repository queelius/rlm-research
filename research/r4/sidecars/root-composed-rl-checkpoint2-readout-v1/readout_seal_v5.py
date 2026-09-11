import time
import readout_study_v5 as meta


def build_ready():
    campaign = meta.read(meta.ROOT / "CAMPAIGN_V5.json")
    decision = meta.checkpoint2_decision()
    if not decision["run"]:
        raise ValueError(decision["reason"])
    return {"schema": "root-composed-rl-checkpoint2-readout-ready-v5",
            "identity": campaign["identity"],
            "campaign_sha256": meta.sha(meta.ROOT / "CAMPAIGN_V5.json"),
            "attempt": str(meta.ATTEMPT), "required_python": str(meta.NATIVE),
            "checkpoint2": {"policy": decision["policy"],
                            "owner_terminal_sha256": decision["owner_terminal_sha256"],
                            "state_sha256": decision["state_sha256"]},
            "created_epoch": time.time(), "gpu_launched": False}


if __name__ == "__main__":
    ready = build_ready()
    meta.write(meta.ROOT / "READY_V5.json", ready)
    print(ready["identity"])
