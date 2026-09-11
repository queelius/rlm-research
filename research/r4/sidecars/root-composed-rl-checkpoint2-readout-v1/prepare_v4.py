"""Seal the additive native-entry recovery without changing scientific inputs."""
import readout_study_v4 as study


def prepare():
    root = study.ROOT
    sources = [root / name for name in (
        "readout_study_v4.py", "readout_owner_v4.py", "readout_seal_v4.py",
        "readout_study.py", "readout_owner.py", "readout_collect.py", "readout_common.py",
        "readout_export.py", "readout_native.py", "readout_metrics.py", "RECOVERY_V4.md",
        "test_recovery_v4.py")]
    inputs = [root / "CAMPAIGN_V3.json", root / "READY.json"]
    prior = study.read(root / "CAMPAIGN_V3.json")
    campaign = {
        "schema": "root-composed-rl-checkpoint2-readout-campaign-v4",
        "question": prior["question"],
        "attempt": str(study.ATTEMPT),
        "recovery": "native Python entry after attempt-001 control-Python dependency failure",
        "science_unchanged": True,
        "planned_endpoints": prior["planned_endpoints"],
        "policies_new": prior["policies_new"],
        "comparators_reused": prior["comparators_reused"],
        "budget_seconds": prior["budget_seconds"],
        "source_sha256": {str(path): study.sha(path) for path in sources},
        "input_sha256": {str(path): study.sha(path) for path in inputs},
    }
    campaign["identity"] = study.digest(campaign)
    study.write(root / "CAMPAIGN_V4.json", campaign)
    return campaign


if __name__ == "__main__":
    print(prepare()["identity"])
