"""CPU-qualify and seal four separately launchable DBpedia-224 arms."""

import os
import subprocess
import sys
import time

import eligibility
import study


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or any(
        study.ready_path(arm).exists() for arm in study.ARMS
    ):
        raise ValueError("CPU-only unused seal required")
    if not (study.ROOT / "ENDPOINTS_FIXED.json").exists():
        raise ValueError("MAIN-fixed endpoint receipt must exist before qualification")
    started = time.monotonic()
    command = [
        str(study.NATIVE),
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:cacheprovider",
        "test_fixture.py",
    ]
    tests = subprocess.run(command, cwd=study.ROOT, capture_output=True, text=True, timeout=240)
    if tests.returncode:
        raise RuntimeError(tests.stdout + tests.stderr)
    qualified = {arm: eligibility.fixed_endpoints(arm)["arm_eligibility"] for arm in study.ARMS}
    key, prior = "STRICT_RLM_CALIBRATION_API_KEY", os.environ.get("STRICT_RLM_CALIBRATION_API_KEY")
    os.environ[key] = "cpu-import-fixture-no-service-not-a-credential"
    try:
        lifecycle, suite = study.lifecycle()
    finally:
        if prior is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = prior
    if suite.SERVE != lifecycle.SERVICE_WRAPPER:
        raise ValueError("actual lifecycle service wrapper differs")
    study.write_x(
        study.ROOT / "CPU_EVIDENCE.json",
        {
            "command": command,
            "tests_stdout": tests.stdout,
            "tests_stderr": tests.stderr,
            "elapsed_seconds": time.monotonic() - started,
            "actual_four_endpoint_qualification": {
                arm: {key: value for key, value in receipt.items() if key != "binding"}
                for arm, receipt in qualified.items()
            },
            "actual_owner_entrypoint_loaded": True,
            "actual_lifecycle_dependencies_loaded": True,
            "dummy_credential_restored": os.environ.get(key) == prior,
            "GPU_or_model_calls": 0,
            "python": sys.version,
            "max_prompt_plus_1024": max(
                len(row["body"]["token_ids"]) + 1024 for row in study.schedule()
            ),
        },
    )
    closure = {}
    data_ready = study.read(study.EVAL_DATA / "DATA_READY.json")
    closure[str(study.EVAL_DATA / "DATA_READY.json")] = study.sha(study.EVAL_DATA / "DATA_READY.json")
    closure.update(data_ready["source_sha256"])
    closure.update(data_ready["artifact_sha256"])
    for arm in study.ARMS:
        path = study.OFFICIAL_SOURCE / ("READY_" + arm.upper() + ".json")
        ready = study.read(path)
        closure.update(ready["closure_sha256"])
        closure[str(path)] = study.sha(path)
    for path in sorted(study.ROOT.iterdir()):
        if path.is_file() and path.suffix in (".py", ".json", ".md"):
            closure[str(path)] = study.sha(path)
    for path, expected in closure.items():
        if study.sha(path) != expected:
            raise ValueError("pre-seal closure differs: " + path)
    for arm in study.ARMS:
        ready = {
            **study.plan(arm),
            "status": "CPU_QUALIFIED_MAIN_GPU_LAUNCH_REQUIRED",
            "closure_sha256": closure,
            "endpoints_fixed_sha256": study.sha(study.ROOT / "ENDPOINTS_FIXED.json"),
            "cpu_evidence_sha256": study.sha(study.ROOT / "CPU_EVIDENCE.json"),
            "source_to_raw_comparator": str(study.ROOT / "compare.py"),
            "claim_boundary": (
                "New DBpedia domain and 14-label vocabulary, but still short classification; "
                "unknown base pretraining exposure and no planning/recursion claim."
            ),
            "GPU_launched": False,
        }
        ready["identity"] = study.digest(ready)
        study.write_x(study.ready_path(arm), ready)
        print(
            {
                "arm": arm,
                "ready_sha256": study.sha(study.ready_path(arm)),
                "identity": ready["identity"],
                "command": ready["command"],
            }
        )


if __name__ == "__main__":
    main()

