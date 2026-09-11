"""Seal the additive attempt-002 startup recovery after the observed namespace failure."""

import os
import subprocess
import sys

import study as s

READY_V2_SHA256 = "4fe1f1f7307cace2b007fac258c5d0f9340d0b84fc3423f704c29e49ec407bbb"
ATTEMPT1 = s.ROOT / "outputs/attempt-001"


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("recovery preparation must hide GPUs")
    for name in ("RECOVERY.json", "CPU_TESTS_RECOVERY.json", "READY_RECOVERY.json"):
        if (s.ROOT / name).exists():
            raise FileExistsError("recovery preparation requires absent " + name)
    if s.sha(s.ROOT / "READY_V2.json") != READY_V2_SHA256:
        raise ValueError("accepted V2 READY changed")
    terminal = s.read(ATTEMPT1 / "OWNER_TERMINAL.json")
    log = (ATTEMPT1 / "owned-service/launcher.log").read_text()
    if terminal.get("complete") is not False or terminal.get("collector_status") is not None:
        raise ValueError("attempt-001 failure class changed")
    if "ValueError: base binding changed" not in log:
        raise ValueError("observed launcher evidence changed")
    evidence = [ATTEMPT1 / "OWNER_TERMINAL.json",
                ATTEMPT1 / "owned-service/launcher.log",
                ATTEMPT1 / "owned-service/SERVICE_STOPPED.json"]
    recovery = {
        "schema": "leaf-role-tool-startup-recovery-v1",
        "failed_attempt": "attempt-001",
        "failure_class": "PRE_MODEL_PRE_COLLECTOR_SERVICE_BINDING_NAMESPACE",
        "root_cause": (
            "The reused free-ID wrapper executed released serve.py in the free-ID sidecar's "
            "study namespace. The leaf-role binding carried this sidecar's independently richer "
            "WEIGHTS.json identity, so serve.py compared it with the free-ID WEIGHTS.json hash "
            "and raised 'base binding changed' before model startup."
        ),
        "narrow_fix": (
            "A leaf-local wrapper binds the identical released base checkpoint and qualified "
            "launcher to this sidecar's exact WEIGHTS.json hash. Additive lifecycle, owner, and "
            "collector wrappers authorize only attempt-002; requests, contexts, seeds, scoring, "
            "sampling, service configuration, and deadlines are unchanged."
        ),
        "same_science_no_rerolls": True,
        "failed_attempt_released": terminal.get("released"),
        "failed_attempt_collector_status": terminal.get("collector_status"),
        "failed_attempt_evidence_sha256": {str(path): s.sha(path) for path in evidence},
        "gpu_calls_during_preparation": 0,
        "model_calls_during_preparation": 0,
    }
    s.write_once(s.ROOT / "RECOVERY.json", recovery)

    command = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
               "test_recovery.py"]
    result = subprocess.run(command, cwd=s.ROOT,
        env={**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True, text=True, timeout=60)
    s.write_once(s.ROOT / "CPU_TESTS_RECOVERY.json", {
        "argv": command, "returncode": result.returncode, "stdout": result.stdout,
        "stderr": result.stderr, "gpu_calls": 0, "model_calls": 0,
        "scope": "leaf manifest consumer binding plus actual owner/lifecycle/collector composition"})
    if result.returncode:
        raise ValueError("focused recovery tests failed")

    old = s.read(s.ROOT / "READY_V2.json")
    sources = dict(old["source_sha256"])
    for path in evidence:
        sources[str(path)] = s.sha(path)
    for name in ("READY_V2.json", "RECOVERY.json", "CPU_TESTS_RECOVERY.json",
                 "service_wrapper_v4.py", "lifecycle_v2.py", "driver_v3.py", "owner_v3.py",
                 "test_recovery.py", "prepare_recovery.py"):
        path = s.ROOT / name
        sources[str(path)] = s.sha(path)
    output = s.ROOT / "outputs/attempt-002"
    python = "/project/alex_phd/envs/prime-rl-5990b1b/bin/python"
    ready = {
        "status": "CPU_READY_RECOVERY_FOR_MAIN_ACCEPTANCE_NOT_LAUNCHED",
        "schema": "leaf-role-tool-contract-recovery-ready-v1",
        "supersedes_for_launch": READY_V2_SHA256,
        "preserved_spec_sha256": s.sha(s.ROOT / "SPEC.json"),
        "preserved_data_sha256": s.sha(s.ROOT / "DATA.json"),
        "preserved_requests_sha256": s.sha(s.ROOT / "REQUESTS.json"),
        "preserved_prompt_ids_sha256": s.sha(s.ROOT / "PROMPT_IDS.json"),
        "recovery_sha256": s.sha(s.ROOT / "RECOVERY.json"),
        "source_sha256": sources,
        "output": str(output),
        "launch_argv": [python, str(s.ROOT / "owner_v3.py"), "run", "--output", str(output)],
        "verify_argv": [python, str(s.ROOT / "owner_v3.py"), "verify"],
        "budget": old["budget"], "same_science_no_rerolls": True,
        "failed_attempt_preserved": str(ATTEMPT1),
        "credential": old["credential"], "gpu_calls": 0, "model_calls": 0,
        "main_owns_gpu_lock_acceptance_and_launch": True,
    }
    ready["identity"] = s.digest(ready)
    s.write_once(s.ROOT / "READY_RECOVERY.json", ready)
    print(s.serialize({"ready_recovery_sha256": s.sha(s.ROOT / "READY_RECOVERY.json"),
                       "identity": ready["identity"], "tests": result.stdout.strip()}))


if __name__ == "__main__":
    main()
