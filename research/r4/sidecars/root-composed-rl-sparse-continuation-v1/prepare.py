"""Freeze the training/readout package before continuation outcomes."""
from pathlib import Path

import continuation_study as study


def prepare():
    root = study.ROOT
    source_names = ("continuation_study.py", "continuation_train.py", "continuation_owner.py",
                    "continuation_readout_owner.py", "seal.py", "test_continuation.py",
                    "DESIGN.md", "PLAN.md")
    sources = [root / name for name in source_names]
    sources += [study.SPARSE_V1 / "sparse_math.py",
                study.SIDE / "root-rlvr-campaign-v1/campaign_train.py"]
    checkpoint = Path(study.checkpoint2_policy()["path"])
    inputs = [study.SOURCE / name for name in ("READY.json", "CAMPAIGN.json", "RECIPE.json",
                                                "START.json", "terminal_study.py", "terminal_common.py",
                                                "terminal_native.py", "terminal_collect.py",
                                                "terminal_export.py", "terminal_train.py",
                                                "terminal_owner.py")]
    inputs += [study.SOURCE / "inputs" / name for name in
               ("PLANS.json", "PUBLIC.json", "HOST_GOLD.json", "TASKS.json", "NATIVE_TEMPLATE.json")]
    inputs += [study.READOUT / "READY_V5.json", study.READOUT / "CAMPAIGN_V5.json",
               study.SPARSE / "outputs/attempt-001/OWNER_TERMINAL.json", checkpoint / "state.json",
               checkpoint / "adapter_model.safetensors", checkpoint / "adapter_config.json",
               checkpoint / "optimizer.pt", checkpoint / "rng_state.pt"]
    campaign = {"schema": "root-composed-rl-sparse-continuation-campaign-v1",
                "question": "Do fixed remaining composed windows4..8 improve grounded behavior beyond Adam2?",
                "attempt": str(study.ATTEMPT), "readout_attempt": str(study.READOUT_ATTEMPT),
                "windows": [4, 5, 6, 7, 8], "planned_training": 120,
                "max_new_updates": 5, "start_optimizer_step": 2,
                "collection_cap_seconds_each": 360, "optimizer_cap_seconds_each": 1800,
                "training_budget_seconds": {"work": 11700, "owned": 11970, "outer": 12000},
                "readout_budget_seconds": {"work": 2400, "owned": 2670, "outer": 2700},
                "source_namespace": str(study.SOURCE), "science_unchanged": True,
                "source_sha256": {str(path): study.sha(path) for path in sources},
                "input_sha256": {str(path): study.sha(path) for path in inputs}}
    campaign["identity"] = study.digest(campaign)
    study.write(root / "CAMPAIGN.json", campaign)
    return campaign


if __name__ == "__main__":
    print(prepare()["identity"])
