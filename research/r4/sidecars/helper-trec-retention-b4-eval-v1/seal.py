"""CPU-qualify and seal three separately launchable retention endpoint arms."""

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
        raise ValueError("CPU-only unused source seal required")
    started = time.monotonic()
    command = [str(study.NATIVE), "-m", "pytest", "test_fixture.py", "-q"]
    completed = subprocess.run(command, cwd=study.ROOT, capture_output=True, text=True, timeout=90)
    if completed.returncode:
        raise RuntimeError(completed.stdout + completed.stderr)
    qualified = {arm: eligibility.fixed_endpoints(arm)["arm_eligibility"] for arm in study.ARMS}
    credential_key = "STRICT_RLM_CALIBRATION_API_KEY"
    previous = os.environ.get(credential_key)
    os.environ[credential_key] = "cpu-import-fixture-no-service-not-a-credential"
    try:
        lifecycle, suite = study.lifecycle()
    finally:
        if previous is None:
            os.environ.pop(credential_key, None)
        else:
            os.environ[credential_key] = previous
    if suite.SERVE != lifecycle.SERVICE_WRAPPER:
        raise ValueError("actual CPU lifecycle service wrapper differs")
    study.write_x(
        study.ROOT / "CPU_EVIDENCE.json",
        {
            "command": command,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "elapsed_seconds": time.monotonic() - started,
            "actual_endpoint_qualification": {
                arm: {key: value for key, value in receipt.items() if key != "binding"}
                for arm, receipt in qualified.items()
            },
            "actual_lifecycle_dependencies_loaded": True,
            "import_only_dummy_credential_restored": os.environ.get(credential_key) == previous,
            "GPU_service_started": False,
            "python": sys.version,
            "executable": sys.executable,
            "max_prompt_plus_1024": max(
                len(row["body"]["token_ids"]) + 1024 for row in study.schedule()
            ),
        },
    )
    closure = {}
    panel = study.read(study.PANEL / "MANIFEST.json")
    for path, expected in panel["source_and_artifact_sha256"].items():
        closure[path] = expected
    closure[str(study.PANEL / "MANIFEST.json")] = study.sha(study.PANEL / "MANIFEST.json")
    for arm in study.ARMS:
        ready_path = study.SOURCE_EVAL / ("READY_" + arm.upper() + ".json")
        ready = study.read(ready_path)
        for path, expected in ready["closure_sha256"].items():
            if path in closure and closure[path] != expected:
                raise ValueError("upstream closure pin conflict: " + path)
            closure[path] = expected
        closure[str(ready_path)] = study.sha(ready_path)
    closure[str(study.SOURCE_EVAL / "ENDPOINTS_FIXED.json")] = study.sha(
        study.SOURCE_EVAL / "ENDPOINTS_FIXED.json"
    )
    for path in sorted(study.ROOT.iterdir()):
        if path.is_file() and path.suffix in (".py", ".md", ".json"):
            closure[str(path)] = study.sha(path)
    for path, expected in closure.items():
        if study.sha(path) != expected:
            raise ValueError("pre-seal closure mismatch: " + path)
    for arm in study.ARMS:
        ready = {
            **study.plan(arm),
            "status": "CPU_QUALIFIED_MAIN_GPU_LAUNCH_REQUIRED",
            "closure_sha256": closure,
            "GPU_launched": False,
            "cpu_evidence_sha256": study.sha(study.ROOT / "CPU_EVIDENCE.json"),
            "authoritative_panel_manifest_sha256": study.sha(study.PANEL / "MANIFEST.json"),
            "panel_manifest_seed2_note_superseded_by_evaluator_amendment": True,
        }
        ready["identity"] = study.digest(ready)
        study.write_x(study.ready_path(arm), ready)
        print(
            {
                "arm": arm,
                "ready_sha256": study.sha(study.ready_path(arm)),
                "identity": ready["identity"],
                "closure_files": len(closure),
                "command": ready["command"],
            }
        )


if __name__ == "__main__":
    main()

