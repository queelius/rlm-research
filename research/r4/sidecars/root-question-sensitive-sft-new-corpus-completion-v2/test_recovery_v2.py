import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "root-question-sensitive-sft-new-corpus-replication-v1"
TRAIN = Path("/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python")


def test_gate_is_mechanical_six_family_subset_of_immutable_corpus():
    train = json.loads((SOURCE / "inputs/TRAIN_PLAN.json").read_text())
    gate = json.loads((ROOT / "inputs/GATE_PLAN.json").read_text())
    assert len(gate) == 6
    assert [row["slot"] for row in gate] == ["T1", "M1", "J1", "P1", "P2", "P3"]
    assert [row["context_id"] for row in gate] == [
        f"question-sensitive-new-corpus-train-{i:02}" for i in range(6)]
    assert all(row in train for row in gate)


def test_actual_training_entry_resolves_gate_and_all72_corpus():
    result = subprocess.run([str(TRAIN), str(ROOT / "train_v2.py"), "verify-inputs"],
                            text=True, capture_output=True, check=True)
    value = json.loads(result.stdout)
    assert value == {"corpus": 72, "gate": 6, "gate_ids_in_corpus": True}


def test_recovery_namespace_is_new_and_no_recapture():
    sys.path.insert(0, str(ROOT))
    import recovery
    assert recovery.ATTEMPT == ROOT / "outputs/attempt-001"
    assert recovery.source_corpus_receipt()["capture_rerun"] is False
    assert str(recovery.training_argv(ROOT / "x", 123.0)[1]).endswith("completion-v2/train_v2.py")
