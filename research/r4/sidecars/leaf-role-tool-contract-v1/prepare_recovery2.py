"""Seal additive attempt-003 recovery for the observed ambiguous service import."""

import os
import subprocess
import sys

import study as s

PRIOR_READY_SHA256 = "23130a3726fed1cfe13c34d6b1513fe4e05343f37cc009799349bcb092780609"
ATTEMPT2 = s.ROOT / "outputs/attempt-002"


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("recovery preparation must hide GPUs")
    for name in ("RECOVERY2.json", "CPU_TESTS_RECOVERY2.json", "READY_RECOVERY2.json"):
        if (s.ROOT / name).exists():
            raise FileExistsError("recovery2 preparation requires absent " + name)
    if s.sha(s.ROOT / "READY_RECOVERY.json") != PRIOR_READY_SHA256:
        raise ValueError("accepted recovery READY changed")
    terminal = s.read(ATTEMPT2 / "OWNER_TERMINAL.json")
    log = (ATTEMPT2 / "owned-service/launcher.log").read_text()
    if terminal.get("complete") is not False or terminal.get("collector_status") is not None or \
            "module 'service' has no attribute 'OLD'" not in log:
        raise ValueError("attempt-002 failure evidence differs")
    evidence = [ATTEMPT2 / "OWNER_TERMINAL.json", ATTEMPT2 / "owned-service/launcher.log",
                ATTEMPT2 / "owned-service/SERVICE_STOPPED.json"]
    recovery = {
        "schema": "leaf-role-tool-startup-recovery-v2", "failed_attempt": "attempt-002",
        "failure_class": "PRE_MODEL_PRE_COLLECTOR_AMBIGUOUS_SERVICE_IMPORT",
        "root_cause": (
            "Transformed serve.py retained `import service`; because wrapper V4 was leaf-local, "
            "Python selected this sidecar's validation-only service.py, which has no OLD/config/descriptor."
        ),
        "narrow_fix": (
            "Wrapper V5 explicitly loads the pinned qualified free-ID service.py and injects it at "
            "the transformed serve consumer. Attempt-003 lifecycle/owner/collector wrappers change "
            "only that binding and exact output namespaces."
        ),
        "qualified_service_sha256": "51215324f767d3b7fc214bed4c64e61592fb3be8223c8d5f1dd4773fae4c48cd",
        "same_science_no_rerolls": True, "failed_attempt_released": terminal.get("released"),
        "failed_attempt_collector_status": terminal.get("collector_status"),
        "failed_attempt_evidence_sha256": {str(path): s.sha(path) for path in evidence},
        "gpu_calls_during_preparation": 0, "model_calls_during_preparation": 0,
    }
    s.write_once(s.ROOT / "RECOVERY2.json", recovery)
    command = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
               "test_recovery2.py"]
    result = subprocess.run(command, cwd=s.ROOT,
        env={**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True, text=True, timeout=60)
    s.write_once(s.ROOT / "CPU_TESTS_RECOVERY2.json", {"argv": command,
        "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr,
        "scope": "full service entry through config/descriptor/launcher prelaunch with Popen intercepted; exact attempt003 composition",
        "gpu_calls": 0, "model_calls": 0})
    if result.returncode:
        raise ValueError("focused recovery2 tests failed")
    old = s.read(s.ROOT / "READY_RECOVERY.json")
    sources = dict(old["source_sha256"])
    for path in evidence:
        sources[str(path)] = s.sha(path)
    qualified = s.SIDE / "leaf-free-id-correspondence-v1/service.py"
    sources[str(qualified)] = s.sha(qualified)
    for name in ("READY_RECOVERY.json", "RECOVERY2.json", "CPU_TESTS_RECOVERY2.json",
                 "service_wrapper_v5.py", "lifecycle_v3.py", "driver_v4.py", "owner_v4.py",
                 "test_recovery2.py", "prepare_recovery2.py"):
        path = s.ROOT / name
        sources[str(path)] = s.sha(path)
    output = s.ROOT / "outputs/attempt-003"
    python = "/project/alex_phd/envs/prime-rl-5990b1b/bin/python"
    ready = {"status": "CPU_READY_RECOVERY2_FOR_MAIN_ACCEPTANCE_NOT_LAUNCHED",
        "schema": "leaf-role-tool-contract-recovery-ready-v2",
        "supersedes_for_launch": PRIOR_READY_SHA256,
        "preserved_spec_sha256": s.sha(s.ROOT / "SPEC.json"),
        "preserved_data_sha256": s.sha(s.ROOT / "DATA.json"),
        "preserved_requests_sha256": s.sha(s.ROOT / "REQUESTS.json"),
        "preserved_prompt_ids_sha256": s.sha(s.ROOT / "PROMPT_IDS.json"),
        "recovery2_sha256": s.sha(s.ROOT / "RECOVERY2.json"), "source_sha256": sources,
        "output": str(output),
        "launch_argv": [python, str(s.ROOT / "owner_v4.py"), "run", "--output", str(output)],
        "verify_argv": [python, str(s.ROOT / "owner_v4.py"), "verify"],
        "budget": old["budget"], "same_science_no_rerolls": True,
        "failed_attempts_preserved": [str(s.ROOT / "outputs/attempt-001"), str(ATTEMPT2)],
        "credential": old["credential"], "gpu_calls": 0, "model_calls": 0,
        "main_owns_gpu_lock_acceptance_and_launch": True}
    ready["identity"] = s.digest(ready)
    s.write_once(s.ROOT / "READY_RECOVERY2.json", ready)
    print(s.serialize({"ready_recovery2_sha256": s.sha(s.ROOT / "READY_RECOVERY2.json"),
                       "identity": ready["identity"], "tests": result.stdout.strip()}))


if __name__ == "__main__":
    main()
