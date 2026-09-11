"""Freeze the narrow attempt-003 collector-namespace recovery."""

import json
import os
import subprocess

import study as s

READY2 = s.ROOT / "READY_RECOVERY.json"
READY2_SHA256 = "04b6db524b63f4bc3ffa5c152720c1c5ac21f63c5f4c01b4e3b63b105b09d96f"
ATTEMPT2 = s.ROOT / "outputs/attempt-002"


def main():
    for name in ("RECOVERY3.json", "CPU_TESTS_RECOVERY3.json", "READY_RECOVERY3.json"):
        if (s.ROOT / name).exists():
            raise FileExistsError("attempt-003 preparation requires absent " + name)
    if s.sha(READY2) != READY2_SHA256:
        raise ValueError("attempt-002 READY changed")
    terminal = s.read(ATTEMPT2 / "OWNER_TERMINAL.json")
    collect_log = ATTEMPT2 / "owned-service/free-id-collect.log"
    log = collect_log.read_text()
    if terminal.get("collector_status") is not None or "only exact owned output namespace" not in log:
        raise ValueError("attempt-002 pre-request evidence changed")
    recovery = {
        "schema": "leaf-free-id-correspondence-attempt003-recovery-v1",
        "failed_attempt": "attempt-002",
        "failure_class": "POST_SERVICE_PREFLIGHT_PRE_REQUEST_COLLECTOR_NAMESPACE",
        "root_cause": "Frozen driver.py authorized only attempt-001/rollout while owner_v3 composed attempt-002/rollout.",
        "fix": "driver_v3 authorizes only attempt-003/rollout; owner_v4 composes and validates that exact argv before command launch.",
        "service_wrapper": "service_wrapper_v3.py unchanged",
        "lifecycle_adapter": "lifecycle_adapter_v3.py unchanged",
        "science_unchanged_no_rerolls": True,
        "failed_attempt_released": terminal.get("released"),
        "failed_attempt_collector_status": terminal.get("collector_status"),
        "failed_attempt_evidence_sha256": {
            str(ATTEMPT2 / "OWNER_TERMINAL.json"): s.sha(ATTEMPT2 / "OWNER_TERMINAL.json"),
            str(collect_log): s.sha(collect_log),
            str(ATTEMPT2 / "owned-service/SERVICE_STOPPED.json"): s.sha(ATTEMPT2 / "owned-service/SERVICE_STOPPED.json"),
        },
        "gpu_calls": 0, "model_calls": 0,
    }
    s.write_once(s.ROOT / "RECOVERY3.json", recovery)
    command = ["/project/alex_phd/envs/prime-rl-5990b1b/bin/python", "-m", "pytest", "-q",
               "test_recovery3.py"]
    result = subprocess.run(command, cwd=s.ROOT,
                            env={**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"},
                            capture_output=True, text=True, timeout=30)
    s.write_once(s.ROOT / "CPU_TESTS_RECOVERY3.json", {
        "argv": command, "returncode": result.returncode, "stdout": result.stdout,
        "stderr": result.stderr, "gpu_calls": 0, "model_calls": 0,
    })
    if result.returncode:
        raise ValueError("narrow attempt-003 regression failed")
    old = s.read(READY2)
    sources = dict(old["source_sha256"])
    for path in (ATTEMPT2 / "OWNER_TERMINAL.json", collect_log,
                 ATTEMPT2 / "owned-service/SERVICE_STOPPED.json"):
        sources[str(path)] = s.sha(path)
    for name in ("READY_RECOVERY.json", "RECOVERY3.json", "driver_v3.py", "owner_v4.py",
                 "test_recovery3.py", "CPU_TESTS_RECOVERY3.json", "prepare_recovery3.py"):
        path = s.ROOT / name
        sources[str(path)] = s.sha(path)
    python = "/project/alex_phd/envs/prime-rl-5990b1b/bin/python"
    output = s.ROOT / "outputs/attempt-003"
    ready = {
        "status": "CPU_READY_FOR_MAIN_ACCEPTANCE_NOT_LAUNCHED",
        "schema": "leaf-free-id-correspondence-attempt003-ready-v1",
        "supersedes_for_launch": READY2_SHA256,
        "recovery_sha256": s.sha(s.ROOT / "RECOVERY3.json"),
        "spec_sha256": old["spec_sha256"], "amendment_sha256": old["amendment_sha256"],
        "source_sha256": sources, "output": str(output),
        "argv": [python, str(s.ROOT / "owner_v4.py"), "run", "--output", str(output)],
        "verify_argv": [python, str(s.ROOT / "owner_v4.py"), "verify"],
        "credential": old["credential"],
        "service_wrapper": str(s.ROOT / "service_wrapper_v3.py"),
        "runtime_lifecycle_manifest": old["runtime_lifecycle_manifest"],
        "collector": str(s.ROOT / "driver_v3.py"),
        "same_science_no_rerolls": True,
        "collection_deadline": old["collection_deadline"],
        "headline_primary": old["headline_primary"],
        "gpu_calls": 0, "model_calls": 0,
        "main_owns_gpu_lock_acceptance_and_launch": True,
    }
    ready["identity"] = s.digest(ready)
    s.write_once(s.ROOT / "READY_RECOVERY3.json", ready)
    print(json.dumps({"sha256": s.sha(s.ROOT / "READY_RECOVERY3.json"),
                      "identity": ready["identity"], "tests": result.stdout.strip()}))


if __name__ == "__main__":
    main()
