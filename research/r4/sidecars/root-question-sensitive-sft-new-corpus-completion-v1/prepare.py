"""Seal the additive recovery without changing the source science or capture."""
from pathlib import Path
import recovery as r


def main():
    root = r.ROOT
    source_paths = [root / name for name in (
        "recovery.py", "collect.py", "owner.py", "test_recovery.py", "prepare.py",
        "DESIGN.md", "PLAN.md")]
    exit_path = (root.parents[1] / "operations/2026-09-10-after-two-harness-bridges-new-corpus-sft6"
                 / "attempt-001/new_corpus_sft6_metadata72/EXIT.json")
    input_paths = [r.SOURCE / "READY.json", r.SOURCE_ATTEMPT / "capture/CORPUS_READY.json",
                   r.SOURCE_ATTEMPT / "OWNER_TERMINAL.json", exit_path]
    ready = {
        "schema": "question-sensitive-sft-new-corpus-completion-ready-v1",
        "namespace": "question-sensitive-sft-new-corpus-completion-20260910-v1",
        "attempt": str(r.ATTEMPT),
        "source_attempt": str(r.SOURCE_ATTEMPT),
        "source_sha256": {str(path): r.s.sha(path) for path in source_paths},
        "input_sha256": {str(path): r.s.sha(path) for path in input_paths},
        "budget": r.BUDGET,
        "science_changes": [],
        "infrastructure_changes": ["preserve MAIN-assigned CUDA in owned training subprocess"],
        "planned": {"reused_teachers": 72, "recaptured_teachers": 0,
                    "optimizer_updates": 6, "metadata_readout": 72},
    }
    ready["identity"] = r.s.digest(ready)
    r.s.write(root / "READY.json", ready)
    print(ready["identity"])


if __name__ == "__main__":
    main()
