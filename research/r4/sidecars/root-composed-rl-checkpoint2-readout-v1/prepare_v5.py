"""Seal the source-namespace capture recovery."""
import readout_study_v5 as meta


def prepare():
    root = meta.ROOT
    sources = [root / name for name in (
        "readout_study_v5.py", "readout_owner_v5.py", "readout_seal_v5.py",
        "readout_owner.py", "readout_study.py", "RECOVERY_V5.md", "test_recovery_v5.py")]
    inputs = [root / "CAMPAIGN_V4.json", root / "READY_V4.json", root / "START.json",
              meta.SOURCE / "START.json", meta.SOURCE / "READY.json", meta.SOURCE / "CAMPAIGN.json",
              meta.SOURCE / "RECIPE.json", meta.SOURCE / "inputs/PLANS.json",
              meta.SOURCE / "inputs/PUBLIC.json", meta.SOURCE / "inputs/HOST_GOLD.json",
              meta.SOURCE / "inputs/TASKS.json"]
    prior = meta.read(root / "CAMPAIGN_V4.json")
    campaign = {"schema": "root-composed-rl-checkpoint2-readout-campaign-v5",
                "question": prior["question"], "attempt": str(meta.ATTEMPT),
                "recovery": "qualified source namespace binding/spec/collector",
                "science_unchanged": True, "planned_endpoints": 72,
                "capture_phase": "readout-rl_last", "external_arm": "checkpoint2",
                "budget_seconds": prior["budget_seconds"],
                "source_sha256": {str(path): meta.sha(path) for path in sources},
                "input_sha256": {str(path): meta.sha(path) for path in inputs}}
    if campaign["input_sha256"][str(root / "START.json")] != campaign["input_sha256"][str(meta.SOURCE / "START.json")]:
        raise ValueError("local starting lineage receipt differs from source")
    campaign["identity"] = meta.digest(campaign)
    meta.write(root / "CAMPAIGN_V5.json", campaign)
    return campaign


if __name__ == "__main__":
    print(prepare()["identity"])
