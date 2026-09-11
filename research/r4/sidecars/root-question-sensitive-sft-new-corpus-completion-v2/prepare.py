"""Freeze the missing deterministic gate receipt and additive v2 closure."""
from pathlib import Path
import recovery as r


def main():
    inputs = r.ROOT / "inputs"
    inputs.mkdir()
    train = r.s.read(r.SOURCE / "inputs/TRAIN_PLAN.json")
    slots = ["T1", "M1", "J1", "P1", "P2", "P3"]
    gate = []
    for index, slot in enumerate(slots):
        context = f"question-sensitive-new-corpus-train-{index:02}"
        rows = [row for row in train if row["context_id"] == context and row["slot"] == slot]
        if len(rows) != 1:
            raise ValueError("mechanical gate coordinate missing")
        gate.extend(rows)
    r.s.write(inputs / "GATE_PLAN.json", gate)
    source_paths = [r.ROOT / name for name in (
        "recovery.py", "train_v2.py", "collect.py", "owner.py", "prepare.py",
        "test_recovery_v2.py", "DESIGN.md", "PLAN.md")]
    exit_path = (r.ROOT.parents[1] / "operations/2026-09-10-after-stable-anchor-new-corpus-completion"
                 / "attempt-001/new_corpus_sft6_completion/EXIT.json")
    input_paths = [inputs / "GATE_PLAN.json", r.SOURCE / "READY.json",
        r.SOURCE_ATTEMPT / "capture/CORPUS_READY.json", r.V1 / "READY.json",
        r.V1 / "outputs/attempt-001/OWNER_TERMINAL.json", exit_path]
    ready = {"schema": "new-corpus-sft-completion-ready-v2", "attempt": str(r.ATTEMPT),
        "source_attempt": str(r.SOURCE_ATTEMPT),
        "source_sha256": {str(path): r.s.sha(path) for path in source_paths},
        "input_sha256": {str(path): r.s.sha(path) for path in input_paths},
        "budget": r.BUDGET, "planned": {"reused_teachers": 72, "recaptured_teachers": 0,
            "optimizer_updates": 6, "metadata_readout": 72},
        "science_changes": [],
        "infrastructure_changes": ["explicit deterministic six-row gate receipt required by qualified trainer"],
        "gate_rule": "T1/M1/J1/P1/P2/P3 from new training contexts 00..05, mirroring original context-family gate layout"}
    ready["identity"] = r.s.digest(ready)
    r.s.write(r.ROOT / "READY.json", ready)
    print(ready["identity"])


if __name__ == "__main__":
    main()
