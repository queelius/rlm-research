"""Seal V5 after invoking the actual registry-loaded task setup in the real runtime."""

import json
import os
import subprocess
import time

import study as base
import study_v5


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("CPU-only preparation requires CUDA hidden")
    ready_path = base.ROOT / "READY_V5.json"
    audit_path = base.ROOT / "CPU_AUDIT_V5.json"
    if ready_path.exists() or audit_path.exists():
        raise FileExistsError("V5 seal outputs must be unused")
    smoke_path = base.ROOT / "CPU_ACTUAL_TASK_SETUP_SMOKE_V5.json"
    smoke = base.read(smoke_path)
    expected = smoke["task_document_sha256"]
    if not (
        smoke["task_class_module"] == "mrcr_rootless_document_baseline_v2"
        and expected == smoke["runtime_read_sha256"] == smoke["in_container_read_sha256"]
        and smoke["runtime_image"] == study_v5.IMAGE
        and smoke["container_stopped"] is True
        and smoke["model_calls"] == smoke["gpu_calls"] == 0
    ):
        raise ValueError("actual frozen task setup smoke invalid")
    env = {**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"}
    test = subprocess.run([str(base.NATIVE), "-m", "pytest", "-q", "test_repair_v5.py"],
        cwd=base.ROOT, env=env, capture_output=True, text=True, timeout=120)
    child = subprocess.run([str(base.NATIVE), "-c", (
        "import inspect,collect_v5,study_v5; e=collect_v5.environment(study_v5.INPUTS);"
        "t=list(e.taskset); assert len(t)==32;"
        "assert inspect.getsourcefile(type(t[0]).setup)==str(study_v5.ROOT/'study_v5.py');"
        "print(type(t[0]).__module__)"
    )], cwd=base.ROOT, env=env, capture_output=True, text=True, timeout=120)
    audit = {"schema": "mrcr-v5-canonical-task-setup-cpu-audit-v1",
        "root_cause": (
            "V3/V4 patched the alias class loaded as mrcr_calibration_old_task, but the "
            "SingleAgentEnv registry instantiated a separate canonical "
            "mrcr_rootless_document_baseline_v2.MRCRTask whose inherited setup only read the file."
        ),
        "repair": "patch the canonical task class after environment construction and before run_slot",
        "pytest": {"returncode": test.returncode, "stdout": test.stdout, "stderr": test.stderr},
        "fresh_collector_process": {"returncode": child.returncode, "stdout": child.stdout,
            "stderr": child.stderr},
        "actual_task_setup_smoke": smoke, "gpu_visible": False, "model_calls": 0}
    base.write_x(audit_path, audit)
    if test.returncode or child.returncode:
        raise ValueError("V5 CPU qualification failed")
    files = [base.ROOT / name for name in ("READY_V4.json", "study_v5.py", "collect_v5.py",
        "owner_v5.py", "runtime_task_setup_smoke_v5.py", "test_repair_v5.py", "prepare_v5.py",
        "CPU_ACTUAL_TASK_SETUP_SMOKE_V5.json", "CPU_AUDIT_V5.json")]
    ready = {"schema": "mrcr-v3-root-procedure-calibration-ready-v5-task-setup-repair",
        "status": "CPU_READY_FOR_MAIN_GPU_LAUNCH", "created_epoch": time.time(),
        "parent_ready_v4_sha256": base.sha(base.ROOT / "READY_V4.json"),
        "failed_attempt_004_terminal_sha256": base.sha(base.ROOT / "outputs/attempt-004/OWNER_TERMINAL.json"),
        "repair_boundary": (
            "Only the class receiving exact full-query task setup changes. V4 allocation runtime and "
            "exact V3 32 tasks, queries, prompts, seeds, model, scoring, gate, and caps remain."
        ),
        "fixed_argv": [str(base.NATIVE), str(base.ROOT / "owner_v5.py"), "run", "--output",
            str(study_v5.ATTEMPT), "--outer-seconds", "900"],
        "external_cap_seconds": 1000, "planned_episodes": 32, "optimizer_steps": 0,
        "science": {"rows": 8, "rollouts_per_row": 4, "seeds": list(base.SEEDS),
            "temperature": 0.5, "max_tokens_per_call": 2048,
            "turn_budget": "maximum six completed turns total across root+child; depth1",
            "same_base_root_and_child": base.MODEL_ALIAS, "one_underlying_context": True,
            "external_object": "exact full CSV queries per row in /context.txt"},
        "actual_process_smoke": str(smoke_path),
        "claim_boundary": "Calibration only; one underlying research-exposed context. V4 is an environment setup-dispatch failure, not a scientific null.",
        "closure_sha256": {str(path): base.sha(path) for path in files}}
    ready["identity"] = base.digest(ready)
    base.write_x(ready_path, ready)
    print(json.dumps({"ready_sha256": base.sha(ready_path), "identity": ready["identity"],
        "tests": test.stdout.strip(), "collector": child.stdout.strip()}, sort_keys=True))


if __name__ == "__main__":
    main()
