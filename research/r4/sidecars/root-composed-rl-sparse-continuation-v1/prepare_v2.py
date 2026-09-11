"""Seal additive runtime V2 after preserving frozen V1."""
import continuation_study_v2 as study


def prepare():
    root = study.ROOT
    sources = [root / name for name in (
        "continuation_study_v2.py", "continuation_train_v2.py", "continuation_owner_v2.py",
        "continuation_readout_owner_v2.py", "seal_v2.py", "test_continuation_v2.py",
        "RUNTIME_V2.md")]
    inputs = [root / "CAMPAIGN.json", root / "DESIGN.md", root / "PLAN.md",
              root / "continuation_study.py", root / "continuation_train.py",
              root / "continuation_owner.py", root / "continuation_readout_owner.py",
              study.READOUT / "READY_V5.json", study.READOUT / "CAMPAIGN_V5.json"]
    old = study.read(root / "CAMPAIGN.json")
    campaign = {"schema": "root-composed-rl-sparse-continuation-campaign-v2",
                "question": old["question"], "training_attempt": str(study.ATTEMPT),
                "readout_attempt": str(study.READOUT_ATTEMPT), "windows": old["windows"],
                "planned_training": old["planned_training"],
                "max_new_updates": old["max_new_updates"],
                "start_optimizer_step": old["start_optimizer_step"],
                "collection_cap_seconds_each": old["collection_cap_seconds_each"],
                "optimizer_cap_seconds_each": old["optimizer_cap_seconds_each"],
                "training_budget_seconds": old["training_budget_seconds"],
                "readout_budget_seconds": old["readout_budget_seconds"],
                "source_namespace": old["source_namespace"], "science_unchanged": True,
                "runtime_correction": {"training_python": str(study.TRAIN),
                    "v1_missing_path": "/project/alex_phd/envs/bootstrap-training-v1/bin/python"},
                "source_sha256": {str(path): study.sha(path) for path in sources},
                "input_sha256": {str(path): study.sha(path) for path in inputs}}
    campaign["identity"] = study.digest(campaign)
    study.write(root / "CAMPAIGN_V2.json", campaign)
    return campaign


if __name__ == "__main__":
    print(prepare()["identity"])
