"""Seal the additive collector-process import repair without changing science."""

import json
import os
import subprocess
import time

import study


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "": raise ValueError("CPU-only preparation")
    path = study.ROOT / "READY_V2.json"
    if path.exists(): raise FileExistsError(path)
    parent = study.verify_ready()
    env = {**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"}
    test = subprocess.run([str(study.NATIVE), "-m", "pytest", "-q",
        "test_calibration.py", "test_repair_v2.py"], cwd=study.ROOT, env=env,
        capture_output=True, text=True, timeout=180)
    audit = {"schema": "mrcr-v3-root-procedure-calibration-cpu-audit-v2",
        "returncode": test.returncode, "stdout": test.stdout, "stderr": test.stderr,
        "gpu_visible": False, "service_started": False,
        "repair_boundary": "fresh docker wrapper process imports local study through collector-exported PYTHONPATH"}
    study.write_x(study.ROOT / "CPU_AUDIT_V2.json", audit)
    if test.returncode: raise ValueError("V2 repair tests failed")
    files = [study.ROOT / name for name in ("READY.json", "collector_entry_v2.py", "owner_v2.py",
        "prepare_v2.py", "test_repair_v2.py", "CPU_AUDIT_V2.json")]
    closure = {str(file): study.sha(file) for file in files}
    ready = {"schema": "mrcr-v3-root-procedure-calibration-ready-v2",
        "status": "CPU_READY_FOR_MAIN_GPU_LAUNCH", "created_epoch": time.time(),
        "parent_ready_sha256": study.sha(study.ROOT / "READY.json"),
        "parent_ready_identity": parent["identity"],
        "supersedes_unlaunched_ready_v1": "Fresh-process context wrapper could not import local study without explicit PYTHONPATH.",
        "science_unchanged": {"planned_episodes": 32, "plan_sha256": study.digest(study.plan()),
            "one_underlying_context": True, "optimizer_steps": 0,
            "turn_budget": "six total root+child, depth1"},
        "fixed_argv": [str(study.NATIVE), str(study.ROOT / "owner_v2.py"), "run",
            "--output", str(study.ROOT / "outputs/attempt-002"), "--outer-seconds", "900"],
        "external_cap_seconds": 1000, "closure_sha256": closure}
    ready["identity"] = study.digest(ready); study.write_x(path, ready)
    print(json.dumps({"ready": str(path), "sha256": study.sha(path),
        "identity": ready["identity"], "tests": test.stdout.strip()}, sort_keys=True))


if __name__ == "__main__": main()

