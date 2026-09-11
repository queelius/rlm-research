"""Seal the isolated recovery source and its transitive frozen inputs."""
import json
from pathlib import Path

import sparse_study as study

SOURCES = [study.ROOT / name for name in (
    "DESIGN.md", "PLAN.md", "sparse_study.py", "sparse_math.py", "cpu_equivalence.py",
    "sparse_qualify.py", "sparse_train.py", "sparse_owner.py", "test_sparse_recovery.py",
    "prepare.py", "seal.py",
)]


def build():
    inputs = study.verify_inputs()
    campaign = {
        "schema": "root-composed-rl-sparse-head-recovery-v1",
        "namespace": study.ROOT.name,
        "question": "Can exact window03 update2 complete after removing unused LM-head positions and enlarging only the infrastructure cap?",
        "source_sha256": {str(path): study.sha(path) for path in SOURCES},
        "input_sha256": {str(path): pin for path, pin in study.PINS.items()},
        "frozen_inventory": inputs,
        "stages": {"qualification_seconds": 900, "training_seconds": 1800,
                   "work_seconds": 2700, "owned_seconds": 2970, "outer_seconds": 3000},
        "scientific_invariants": ["exact old GROUP and GENERATION", "checkpoint1 adapter Adam and RNG",
            "unchanged episode and turn order", "unchanged rewards advantages TIS PPO masks and weights",
            "one possible optimizer step 1 to 2", "no recollection reselection refill truncation or evaluation"],
        "operative_changes": ["LM head only at credited predecessor positions",
                              "training wall cap 1800 instead of failed 240"],
        "status": "CPU qualified only; MAIN alone may launch GPU",
    }
    campaign["identity"] = study.digest(campaign)
    return campaign


if __name__ == "__main__":
    value = build()
    path = study.ROOT / "CAMPAIGN.json"
    if path.exists() and json.loads(path.read_text()) != value:
        raise ValueError("sealed campaign differs")
    if not path.exists():
        study.write(path, value)
    print(value["identity"])
