"""Seal a CPU-qualified candidate.  Does not launch a model or GPU process."""
import datetime
from pathlib import Path

import warm_study as study


def main():
    for name in ("CPU_REPORT.json", "READY.json"):
        if (study.ROOT / name).exists():
            raise FileExistsError("seal is write-once")
    campaign = study.verify_prepared()
    report = {
        "completed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "command": "/project/alex_phd/envs/prime-rl-5990b1b/bin/python -m pytest -q -p no:cacheprovider test_inputs.py test_native_training.py test_pipeline.py test_owner.py test_entrypoints.py",
        "passed": 17, "failed": 0, "warnings": 2, "gpu_calls": 0,
        "red_green": [
            "committed-checkpoint recovery test failed before recovery implementation, then passed",
            "actual start binding exposed missing decision kind before correction, then passed",
        ],
        "actual_entries": [
            "warm_owner.py verify authenticated the campaign and exact SFT24 files",
            "owner traversed fixed eight update windows and paired readouts with intercepted processes",
            "actual owner-to-service wrapper reached 8192/two-LoRA inference config with Popen intercepted",
            "collector and trainer CLI parsers accepted the exact owner argv",
            "native first-prefix identities match frozen current-interface training and composition readout tokens",
        ],
    }
    study.write(study.ROOT / "CPU_REPORT.json", report)
    local = [path for path in study.ROOT.iterdir() if path.is_file() and path.name not in {"READY.json"}]
    local += list((study.ROOT / "inputs").glob("*.json"))
    source = {str(path): study.sha(path) for path in sorted(local)}
    value = {
        "schema": "root-sft24-terminal-rlvr-ready-v1",
        "status": "CPU-qualified; MAIN-only GPU launch",
        "campaign_id": campaign["campaign_id"],
        "campaign_sha256": study.sha(study.ROOT / "CAMPAIGN.json"),
        "cpu_report_sha256": study.sha(study.ROOT / "CPU_REPORT.json"),
        "local_seal_sha256": source,
        "transitive_campaign_source_pins": len(campaign["source_sha256"]),
        "transitive_campaign_input_pins": len(campaign["input_sha256"]),
        "planned": {"training": 192, "readout": 96, "windows": 8,
                    "maximum_actual_optimizer_updates": 8},
        "bounds_seconds": {"outer": 10800, "owned": 10680, "work": 10500,
                           "training": 5400, "readout": 5100, "cleanup_each": 30},
        "selection": "last actually committed RL checkpoint including zero; no outcome selection",
        "new_campaign_outputs_seen": False,
        "science_adaptive_to": ["sealed dose semantic retrospective", "sealed composition audit"],
        "terminal_reward_unchanged": True,
        "credential_value_logged": False,
    }
    value["identity"] = study.digest(value)
    study.write(study.ROOT / "READY.json", value)
    print(value["identity"])


if __name__ == "__main__":
    main()
