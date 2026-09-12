"""Seal one focused actual512 fixture and separately launchable fixed endpoint arms."""

import os
import subprocess
import sys
import time

import eligibility
import study


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or any(
        study.ready_path(a).exists() for a in study.ARMS
    ):
        raise ValueError("CPU-only unused source seal required")
    started = time.monotonic()
    command = [str(study.NATIVE), "-m", "pytest", "test_fixture.py", "-q"]
    completed = subprocess.run(command, cwd=study.ROOT, capture_output=True, text=True, timeout=90)
    if completed.returncode:
        raise RuntimeError(completed.stdout + completed.stderr)
    sft = eligibility.qualify("sft_step8")
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
            "actual_completed_sft_endpoint": {
                key: value for key, value in sft.items() if key != "binding"
            },
            "actual_lifecycle_dependencies_loaded": True,
            "import_only_dummy_credential_restored": os.environ.get(credential_key) == previous,
            "GPU_service_started": False,
            "python": sys.version,
            "executable": sys.executable,
            "max_prompt_plus_1024": max(
                len(r["body"]["token_ids"]) + 1024 for r in study.schedule()
            ),
        },
    )
    closure = {}
    for path in (
        study.RL / "READY_V2.json",
        eligibility.SFT / "READY_V2.json",
        study.DATA / "DATA_READY.json",
    ):
        ready = study.read(path)
        for target, expected in ready.get("closure_sha256", {}).items():
            if target in closure and closure[target] != expected:
                raise ValueError("upstream source pin conflict")
            closure[target] = expected
        closure[str(path)] = study.sha(path)
    for path in sorted(study.ROOT.iterdir()):
        if path.is_file() and path.suffix in (".py", ".md", ".json"):
            closure[str(path)] = study.sha(path)
    extra = study.SIDE / "helper-unseen-generalization-c32-baseline-v1/owner.py"
    closure[str(extra)] = study.sha(extra)
    for path, expected in closure.items():
        if study.sha(path) != expected:
            raise ValueError("pre-seal closure mismatch: " + path)
    for arm in study.ARMS:
        ready = {
            **study.plan(arm),
            "status": "CPU_QUALIFIED_MAIN_FIXED_ENDPOINTS_AND_LAUNCH_REQUIRED",
            "closure_sha256": closure,
            "GPU_launched": False,
            "sft_training_ready_sha256": eligibility.SFT_READY_SHA,
            "rl_launch_ready_sha256": eligibility.RL_REPAIR_SHA,
            "data_manifest_sha256": study.sha(study.DATA / "inputs/MANIFEST.json"),
            "cpu_evidence_sha256": study.sha(study.ROOT / "CPU_EVIDENCE.json"),
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
