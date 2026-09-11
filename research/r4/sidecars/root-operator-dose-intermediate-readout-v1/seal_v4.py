"""Additive V4 seal after physical-only disk-union review."""
import os
from pathlib import Path
import subprocess
import time

import id_study as study


def main():
    target = study.ROOT / "READY_v4.json"
    if target.exists():
        raise FileExistsError("READY_v4 already sealed")
    started = time.time()
    argv = [str(study.NATIVE), "-m", "pytest", "-q", "-p", "no:cacheprovider",
            "test_selection.py", "test_inputs.py", "test_binding_owner.py", "test_entry.py",
            "test_native.py", "test_execute_v4.py", "test_service_v4.py", "--basetemp",
            str(study.ROOT / "qualification-v4-001")]
    test = subprocess.run(argv, cwd=study.ROOT,
                          env={**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"},
                          text=True, capture_output=True, timeout=240)
    report = {
        "argv": argv, "returncode": test.returncode, "stdout": test.stdout,
        "stderr": test.stderr, "elapsed_seconds": time.time() - started,
        "gpu_calls": 0, "scientific_model_calls": 0,
        "correction_scope": ["physical-only free union", "complete evidence pins", "HTTP success semantics"],
        "scientific_inputs_changed": False,
        "actual_service_to_inference_popen_intercepted": True,
    }
    study.write(study.ROOT / "CPU_REPORT_v4.json", report)
    if test.returncode:
        raise RuntimeError(test.stdout + test.stderr)
    old = study.read(study.ROOT / "READY_v3.json")
    sources = dict(old["source_sha256"])
    sources.update({str(path): study.sha(path) for path in (
        study.ROOT / "READY_v3.json", study.ROOT / "id_owner_v4.py",
        study.ROOT / "test_execute_v4.py", study.ROOT / "test_service_v4.py",
        study.ROOT / "V4_CORRECTION.md", study.ROOT / "seal_v4.py",
        study.ROOT / "CPU_REPORT_v4.json")})
    ready = {key: value for key, value in old.items() if key != "identity"}
    ready.update({
        "schema": "operator-dose-intermediate-readout-ready-v4",
        "status": "CPU_READY_V4_NOT_LAUNCHED",
        "supersedes_ready_sha256": study.sha(study.ROOT / "READY_v3.json"),
        "correction": "complete physical disk union and HTTP-success-aware raw response accounting",
        "scientific_inputs_unchanged": True,
        "source_sha256": sources,
        "owner_argv": [str(study.NATIVE), str(study.ROOT / "id_owner_v4.py"), "run",
                       "--output", str(study.ATTEMPT)],
        "verify_argv": [str(study.NATIVE), str(study.ROOT / "id_owner_v4.py"), "verify"],
    })
    ready["identity"] = study.digest(ready)
    study.write(target, ready)
    for path, pin in {**ready["source_sha256"], **ready["input_sha256"]}.items():
        study.base.dose.check(path, pin)
    print({"ready_v4_sha256": study.sha(target), "identity": ready["identity"],
           "source_pins": len(sources), "input_pins": len(ready["input_sha256"]),
           "cpu_report_v4_sha256": study.sha(study.ROOT / "CPU_REPORT_v4.json"),
           "tests": test.stdout, "elapsed_seconds": time.time() - started})


if __name__ == "__main__":
    main()
