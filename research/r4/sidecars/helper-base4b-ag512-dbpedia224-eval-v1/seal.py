"""CPU-qualify and seal the true-base two-panel control."""

import os
from pathlib import Path
import subprocess
import sys
import time

import study


SOURCE_READIES = (
    study.AG_SOURCE / "READY_C32.json",
    study.DB_SOURCE / "READY_C32.json",
    study.BASE_SOURCE / "READY_REPAIR.json",
    study.SERVICE_WRAPPER.parent / "READY_ATTEMPT003.json",
)


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or study.ATTEMPT.exists():
        raise ValueError("CPU-only seal and unused attempt-001 required")
    if (study.ROOT / "READY.json").exists():
        raise FileExistsError("READY.json exists; additive reseal required")
    started = time.monotonic()
    command = [
        str(study.NATIVE),
        "-m",
        "pytest",
        "-q",
        "-p",
        "no:cacheprovider",
        "test_control.py",
    ]
    tests = subprocess.run(command, cwd=study.ROOT, text=True, capture_output=True, timeout=240)
    if tests.returncode:
        raise RuntimeError(tests.stdout + tests.stderr)
    binding = study.binding()
    suite = study.dependencies()
    if suite.SERVE != study.SERVICE_WRAPPER or suite.life.ALLOCATION_SERVICE != study.SERVICE_WRAPPER:
        raise ValueError("actual service dependency is not batch-invariant wrapper")
    if not study.exact_source_request_match():
        raise ValueError("source request equality failed")
    study.write_x(
        study.ROOT / "CPU_EVIDENCE.json",
        {
            "schema": "helper-base4b-ag512-dbpedia224-cpu-evidence-v1",
            "command": command,
            "stdout": tests.stdout,
            "stderr": tests.stderr,
            "elapsed_seconds": time.monotonic() - started,
            "tests_passed": 4,
            "actual_dependency_loaded": True,
            "service_wrapper": str(study.SERVICE_WRAPPER),
            "service_wrapper_sha256": study.sha(study.SERVICE_WRAPPER),
            "true_base_binding": binding,
            "exact_source_request_match_except_model_alias": True,
            "GPU_or_model_calls": 0,
            "python": sys.version,
        },
    )
    closure = {}
    for path in SOURCE_READIES:
        ready = study.read(path)
        closure.update(ready["closure_sha256"])
        closure[str(path)] = study.sha(path)
    closure[str(study.BASE_SOURCE / "outputs/attempt-002/RESULT.json")] = study.sha(
        study.BASE_SOURCE / "outputs/attempt-002/RESULT.json"
    )
    closure[str(study.BASE_SOURCE / "outputs/attempt-002/OWNER_TERMINAL.json")] = study.sha(
        study.BASE_SOURCE / "outputs/attempt-002/OWNER_TERMINAL.json"
    )
    for path in sorted(study.ROOT.iterdir()):
        if path.is_file() and path.suffix in (".py", ".json", ".md") and path.name != "READY.json":
            closure[str(path)] = study.sha(path)
    for path, expected in closure.items():
        if study.sha(path) != expected:
            raise ValueError("pre-seal closure differs: " + path)
    ready = {
        **study.plan(),
        "status": "CPU_QUALIFIED_MAIN_GPU_LAUNCH_REQUIRED",
        "closure_sha256": closure,
        "cpu_evidence_sha256": study.sha(study.ROOT / "CPU_EVIDENCE.json"),
        "source_ready_sha256": {str(path): study.sha(path) for path in SOURCE_READIES},
        "historical_base_result": str(
            study.BASE_SOURCE / "outputs/attempt-002/RESULT.json"
        ),
        "historical_base_result_sha256": study.sha(
            study.BASE_SOURCE / "outputs/attempt-002/RESULT.json"
        ),
        "claim_boundary": (
            "Original-model reference on two new panels; LoRA and prefix caching differ from the "
            "four trained arms, so neither bitwise output nor matched serving cost is claimed."
        ),
        "launch_authority": "MAIN only",
        "GPU_launched": False,
    }
    ready["identity"] = study.digest(ready)
    study.write_x(study.ROOT / "READY.json", ready)
    print(
        {
            "ready_sha256": study.sha(study.ROOT / "READY.json"),
            "identity": ready["identity"],
            "command": ready["command"],
        }
    )


if __name__ == "__main__":
    main()
