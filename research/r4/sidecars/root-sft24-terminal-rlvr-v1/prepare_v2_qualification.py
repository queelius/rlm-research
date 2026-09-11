"""Materialize a write-once qualification binding before the expensive CPU fixture."""
from pathlib import Path

import warm_study as study


def main():
    target = study.ROOT / "V2_QUALIFICATION.json"
    if target.exists():
        raise FileExistsError("qualification binding is write-once")
    sources = [study.ROOT / name for name in (
        "warm_verify_v2.py", "warm_collect_v2.py", "warm_export_v2.py",
        "warm_native_v2.py", "warm_train_v2.py", "warm_owner_v2.py",
        "V2_AMENDMENT.md")]
    inputs = list((study.ROOT / "inputs").glob("*.json")) + [
        study.ROOT / "READY.json", study.ROOT / "CAMPAIGN.json",
        study.ROOT.parents[1] / "analyses/root-sft24-terminal-rlvr-cpu-2026-09-10/reproduce_v1.py"]
    value = {
        "schema": "root-sft24-terminal-rlvr-v2-qualification",
        "campaign_id": study.CAMPAIGN_ID,
        "attempt": str(study.ROOT / "outputs/attempt-002"),
        "source_sha256": {str(path): study.sha(path) for path in sources},
        "input_sha256": {str(path): study.sha(path) for path in inputs},
        "science_changed": False, "v1_launched": False,
    }
    value["identity"] = study.digest(value)
    study.write(target, value)
    print(value["identity"])


if __name__ == "__main__":
    main()
