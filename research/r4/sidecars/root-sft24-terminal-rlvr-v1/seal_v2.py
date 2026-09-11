"""Seal additive V2 after focused CPU qualification; never launches a model."""
import datetime

import warm_study as study


def main():
    if (study.ROOT / "READY_v2.json").exists():
        raise FileExistsError("V2 READY is write-once")
    report = {
        "completed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "focused_commands": [
            "/project/alex_phd/envs/prime-rl-5990b1b/bin/python -m pytest -q -p no:cacheprovider test_v2_integration.py",
            "/project/alex_phd/envs/prime-rl-5990b1b/bin/python -m pytest -q -p no:cacheprovider test_inputs.py test_native_training.py test_pipeline.py test_owner.py test_entrypoints.py test_v2.py",
        ],
        "passed": 22, "failed": 0, "gpu_calls": 0,
        "integration": "actual authored mixed24 native collection, complete export, native replay, root token/logprob admission, trainer --preflight; synthetic provider only",
        "v1_reproduction_sha256": "3bcbd8b550920bbc84fef9343405f1c1acb94945f37a664462824ab6aae034f5",
        "science_changed": False,
    }
    study.write(study.ROOT / "CPU_REPORT_v2.json", report)
    sources = [study.ROOT / name for name in (
        "warm_verify_v2.py", "warm_collect_v2.py", "warm_export_v2.py",
        "warm_native_v2.py", "warm_train_v2.py", "warm_owner_v2.py",
        "V2_AMENDMENT.md", "test_v2.py", "test_v2_integration.py", "seal_v2.py")]
    inputs = list((study.ROOT / "inputs").glob("*.json")) + [
        study.ROOT / "READY.json", study.ROOT / "CAMPAIGN.json",
        study.ROOT / "V2_QUALIFICATION.json", study.ROOT / "CPU_REPORT_v2.json"]
    value = {
        "schema": "root-sft24-terminal-rlvr-ready-v2",
        "status": "CPU-qualified additive correction; MAIN acceptance required",
        "campaign_id": study.CAMPAIGN_ID,
        "attempt": str(study.ROOT / "outputs/attempt-002"),
        "owner_argv": [str(study.NATIVE), str(study.ROOT / "warm_owner_v2.py"),
                       "run", "--output", str(study.ROOT / "outputs/attempt-002")],
        "verify_argv": [str(study.NATIVE), str(study.ROOT / "warm_owner_v2.py"), "verify"],
        "qualification_sha256": study.sha(study.ROOT / "V2_QUALIFICATION.json"),
        "source_sha256": {str(path): study.sha(path) for path in sources},
        "input_sha256": {str(path): study.sha(path) for path in inputs},
        "planned_training": 192, "planned_readout": 96, "scheduled_windows": 8,
        "maximum_actual_updates": 8, "outer_seconds": 10800,
        "work_seconds": 10500, "owned_seconds": 10680,
        "same_science_as_v1": True, "v1_launched": False,
        "main_launch_only": True, "gpu_calls_in_preparation": 0,
    }
    value["identity"] = study.digest(value)
    study.write(study.ROOT / "READY_v2.json", value)
    print(value["identity"])


if __name__ == "__main__":
    main()
