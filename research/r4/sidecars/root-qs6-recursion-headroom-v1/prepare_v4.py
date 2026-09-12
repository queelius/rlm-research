"""Seal V4 after a fresh-process dependency and two-mode request-prep qualification."""

import json
import os
import subprocess
import time

import study


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "": raise ValueError("CPU-only preparation")
    ready_path = study.ROOT / "READY_V4.json"
    if ready_path.exists(): raise FileExistsError(ready_path)
    env = {**os.environ, "CUDA_VISIBLE_DEVICES": "",
        "STRICT_RLM_CALIBRATION_API_KEY": "cpu-fixture-not-used"}
    tests = subprocess.run([str(study.NATIVE), "-m", "pytest", "-q", "test_owner_v4.py"],
        cwd=study.ROOT, env=env, capture_output=True, text=True, timeout=90)
    audit = {"schema": "root-qs6-recursion-headroom-cpu-path-audit-v4",
        "returncode": tests.returncode, "stdout": tests.stdout, "stderr": tests.stderr,
        "gpu_visible": False, "service_started": False,
        "boundaries": ["fresh process dependencies()", "no_child prepare_spec", "enabled prepare_spec"]}
    audit_path = study.ROOT / "CPU_PATH_AUDIT_V4.json"; study.write(audit_path, audit)
    if tests.returncode: raise ValueError("V4 qualification failed")
    parent = study.ROOT / "READY_V3.json"; closure = dict(study.read(parent)["closure_sha256"])
    names = ("READY_V3.json", "study_v4.py", "owner_v4.py", "test_owner_v4.py",
        "prepare_v4.py", "CPU_PATH_AUDIT_V4.json")
    closure.update({str(study.ROOT / name): study.sha(study.ROOT / name) for name in names})
    recovery = study.RECOVERY
    for name in ("owner_v7.py", "study.py", "study_v2.py", "study_v3.py", "study_v4.py",
            "study_v5.py", "study_v6.py", "study_v7.py"):
        closure[str(recovery / name)] = study.sha(recovery / name)
    value = {"schema": "root-qs6-recursion-headroom-ready-v4",
        "status": "CPU_READY_FOR_MAIN_GPU_LAUNCH", "created_epoch": time.time(),
        "parent_ready_v3_sha256": study.sha(parent),
        "repaired_defect": "Isolate the complete recovery owner/study ancestor chain from local generic module aliases.",
        "preserved_failed_attempt": str(study.ROOT / "outputs/attempt-001"),
        "fixed_argv": [str(study.NATIVE), str(study.ROOT / "owner_v4.py"), "run",
            "--output", str(study.ROOT / "outputs/attempt-002"), "--outer-seconds", str(study.OUTER_SECONDS)],
        "science_unchanged": {"planned_episodes": 96, "blocks": list(study.BLOCK_MODES),
            "seeds": [row["seed"] for block in study.make_blocks() for row in block],
            "outer_seconds": study.OUTER_SECONDS, "owned_seconds": study.OWNED_SECONDS,
            "admission_trigger": study.ADMISSION_TRIGGER},
        "qualification": "Fresh Python process loaded dependencies() and prepared authenticated no_child and enabled request specs.",
        "closure_sha256": closure}
    value["identity"] = study.digest({k: v for k, v in value.items() if k != "identity"})
    study.write(ready_path, value)
    print(json.dumps({"path": str(ready_path), "sha256": study.sha(ready_path),
        "identity": value["identity"]}, sort_keys=True))


if __name__ == "__main__": main()
