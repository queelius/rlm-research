"""Freeze the additive attempt-002 recovery after the observed pre-model launcher failure."""

import json
import os
import subprocess

import study as s


READY_V2_SHA256 = "754540d9f1940a9dcdad581838ca5b5ff090b0b36f73d0bbbfdb66623fcc9837"
ATTEMPT1 = s.ROOT / "outputs/attempt-001"


def main():
    for name in ("RECOVERY.json", "CPU_TESTS_RECOVERY.json", "READY_RECOVERY.json"):
        if (s.ROOT / name).exists():
            raise FileExistsError("recovery preparation requires absent " + name)
    if s.sha(s.ROOT / "READY_V2.json") != READY_V2_SHA256:
        raise ValueError("frozen READY V2 changed")
    terminal = s.read(ATTEMPT1 / "OWNER_TERMINAL.json")
    log = (ATTEMPT1 / "owned-service/launcher.log").read_text()
    if terminal.get("collector_status") is not None or terminal.get("complete") is not False:
        raise ValueError("attempt-001 failure class changed")
    if "KeyError" not in log or "scripts/launch.py" not in log:
        raise ValueError("attempt-001 launcher evidence changed")

    evidence_paths = [ATTEMPT1 / "OWNER_TERMINAL.json",
                      ATTEMPT1 / "owned-service/launcher.log",
                      ATTEMPT1 / "owned-service/SERVICE_STOPPED.json"]
    recovery = {
        "schema": "leaf-free-id-correspondence-startup-recovery-v1",
        "failed_attempt": "attempt-001",
        "failure_class": "PRE_MODEL_PRE_COLLECTOR_STARTUP_CONFIGURATION",
        "root_cause": (
            "The inherited released-base serve.py looked up launch.py in SPEC.source_sha256. "
            "V2 directly authenticated that launcher in READY_V2, but the preserved V1 SPEC map "
            "does not contain the key, causing the observed KeyError before model startup."
        ),
        "narrow_fix": (
            "service_wrapper_v3 replaces only that consumer lookup with the same already-frozen "
            "launcher SHA-256; driver-library adaptation and V2 lifecycle ownership are unchanged."
        ),
        "science_unchanged": True,
        "requests_seeds_contexts_rerolls_changed": False,
        "scoring_contract": "Unchanged READY_V2 contract-valid planned-denominator primary.",
        "deadline_contract": "Unchanged min(shared work deadline, collection start + 1500).",
        "failed_attempt_evidence_sha256": {str(path): s.sha(path) for path in evidence_paths},
        "failed_attempt_released": terminal.get("released"),
        "failed_attempt_collector_status": terminal.get("collector_status"),
        "gpu_calls_during_recovery_preparation": 0,
        "model_calls_during_recovery_preparation": 0,
    }
    s.write_once(s.ROOT / "RECOVERY.json", recovery)

    command = ["/project/alex_phd/envs/prime-rl-5990b1b/bin/python", "-m", "pytest", "-q",
               "test_study.py", "test_owner.py", "test_scoring_v2.py", "test_owner_v2.py",
               "test_recovery.py"]
    environment = {**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"}
    result = subprocess.run(command, cwd=s.ROOT, env=environment, capture_output=True,
                            text=True, timeout=60)
    s.write_once(s.ROOT / "CPU_TESTS_RECOVERY.json", {
        "argv": command, "returncode": result.returncode, "stdout": result.stdout,
        "stderr": result.stderr, "gpu_calls": 0, "model_calls": 0,
    })
    if result.returncode:
        raise ValueError("focused recovery CPU tests failed")

    old = s.read(s.ROOT / "READY_V2.json")
    sources = dict(old["source_sha256"])
    for path in evidence_paths:
        sources[str(path)] = s.sha(path)
    for name in ("READY_V2.json", "RECOVERY.json", "service_wrapper_v3.py",
                 "lifecycle_adapter_v3.py", "owner_v3.py", "test_recovery.py",
                 "CPU_TESTS_RECOVERY.json", "prepare_recovery.py"):
        path = s.ROOT / name
        sources[str(path)] = s.sha(path)
    output = s.ROOT / "outputs/attempt-002"
    python = "/project/alex_phd/envs/prime-rl-5990b1b/bin/python"
    ready = {
        "status": "CPU_READY_FOR_MAIN_ACCEPTANCE_NOT_LAUNCHED",
        "schema": "leaf-free-id-correspondence-recovery-ready-v1",
        "supersedes_for_launch": READY_V2_SHA256,
        "failed_attempt": str(ATTEMPT1),
        "recovery_sha256": s.sha(s.ROOT / "RECOVERY.json"),
        "spec_sha256": old["spec_sha256"],
        "amendment_sha256": old["amendment_sha256"],
        "source_sha256": sources,
        "output": str(output),
        "argv": [python, str(s.ROOT / "owner_v3.py"), "run", "--output", str(output)],
        "verify_argv": [python, str(s.ROOT / "owner_v3.py"), "verify"],
        "credential": old["credential"],
        "service_wrapper": str(s.ROOT / "service_wrapper_v3.py"),
        "runtime_lifecycle_manifest": old["runtime_lifecycle_manifest"],
        "actual_wrapper_identity_symmetric": True,
        "collection_deadline": old["collection_deadline"],
        "headline_primary": old["headline_primary"],
        "same_science_no_rerolls": True,
        "gpu_calls": 0,
        "model_calls": 0,
        "main_owns_gpu_lock_acceptance_and_launch": True,
    }
    ready["identity"] = s.digest(ready)
    s.write_once(s.ROOT / "READY_RECOVERY.json", ready)
    print(json.dumps({"ready_recovery_sha256": s.sha(s.ROOT / "READY_RECOVERY.json"),
                      "identity": ready["identity"], "tests": result.stdout.strip()}))


if __name__ == "__main__":
    main()
