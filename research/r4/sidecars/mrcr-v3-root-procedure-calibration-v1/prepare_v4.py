"""Seal the runtime-only V4 repair after focused CPU checks."""

import json
import os
import subprocess
import time

import study as base
import study_v4


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("CPU-only preparation requires CUDA_VISIBLE_DEVICES empty")
    ready_path = base.ROOT / "READY_V4.json"
    audit_path = base.ROOT / "CPU_AUDIT_V4.json"
    if ready_path.exists() or audit_path.exists():
        raise FileExistsError("V4 seal outputs must be unused")
    runtime = study_v4.verify_allocation_runtime()
    smoke_path = base.ROOT / "CPU_RUNTIME_SMOKE_V4.json"
    smoke = base.read(smoke_path)
    if not (
        smoke["image"] == study_v4.IMAGE
        and smoke["wrapper"] == str(study_v4.RUNTIME_BIN / "docker")
        and smoke["container_stopped"] is True
        and smoke["gpu_calls"] == 0
        and smoke["source_queries_sha256"] == smoke["runtime_api_read_sha256"]
        == smoke["in_container_python_read_sha256"]
    ):
        raise ValueError("real allocation-runtime smoke did not authenticate full-query readback")
    env = {**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"}
    test = subprocess.run(
        [str(base.NATIVE), "-m", "pytest", "-q", "test_repair_v4.py"],
        cwd=base.ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    child = subprocess.run(
        [
            str(base.NATIVE),
            "-c",
            (
                "import collect_v4,study_v4;"
                "e=collect_v4.environment(study_v4.INPUTS);t=list(e.taskset);"
                "assert len(t)==32;"
                "assert e.config.agent.runtime.image==study_v4.IMAGE;"
                "assert all(x.data.document_sha256 for x in t);"
                "print(study_v4.IMAGE)"
            ),
        ],
        cwd=base.ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    audit = {
        "schema": "mrcr-v4-runtime-repair-cpu-audit-v1",
        "root_cause": (
            "V3 selected localhost/verifiers-rlm-python:3.11-slim-single-id-v1 through "
            "the generic rootless store; that store did not contain the tag and attempted a "
            "localhost registry pull."
        ),
        "repair": {
            "image": study_v4.IMAGE,
            "wrapper": str(study_v4.RUNTIME_BIN / "docker"),
            "private_store": runtime["private_store"],
            "scientific_inputs_unchanged_from_ready_v3": True,
        },
        "pytest": {"returncode": test.returncode, "stdout": test.stdout, "stderr": test.stderr},
        "fresh_collector_process": {
            "returncode": child.returncode,
            "stdout": child.stdout,
            "stderr": child.stderr,
            "tasks": 32,
        },
        "real_sandbox_smoke": smoke,
        "gpu_visible": False,
        "model_calls": 0,
    }
    base.write_x(audit_path, audit)
    if test.returncode or child.returncode:
        raise ValueError("V4 focused CPU qualification failed")
    files = [
        base.ROOT / "READY_V3.json",
        base.ROOT / "SPEC_V3.json",
        base.ROOT / "study_v4.py",
        base.ROOT / "collect_v4.py",
        base.ROOT / "owner_v4.py",
        base.ROOT / "runtime_smoke_v4.py",
        base.ROOT / "test_repair_v4.py",
        base.ROOT / "prepare_v4.py",
        smoke_path,
        audit_path,
        study_v4.RUNTIME / "CPU_READY.json",
        study_v4.RUNTIME_BIN / "docker",
    ]
    closure = {str(path): base.sha(path) for path in files}
    ready = {
        "schema": "mrcr-v3-root-procedure-calibration-ready-v4-runtime-repair",
        "status": "CPU_READY_FOR_MAIN_GPU_LAUNCH",
        "created_epoch": time.time(),
        "parent_ready_v3_sha256": base.sha(base.ROOT / "READY_V3.json"),
        "failed_attempt_003_terminal_sha256": base.sha(
            base.ROOT / "outputs/attempt-003/OWNER_TERMINAL.json"
        ),
        "repair_boundary": (
            "Only sandbox image identity and Docker CLI/store binding changed; exact V3 "
            "32-coordinate science, full-query files, model binding, seeds, scoring, and caps remain."
        ),
        "fixed_argv": [
            str(base.NATIVE),
            str(base.ROOT / "owner_v4.py"),
            "run",
            "--output",
            str(study_v4.ATTEMPT),
            "--outer-seconds",
            "900",
        ],
        "external_cap_seconds": 1000,
        "planned_episodes": 32,
        "optimizer_steps": 0,
        "runtime": {
            "image": study_v4.IMAGE,
            "wrapper": str(study_v4.RUNTIME_BIN / "docker"),
            "private_store": runtime["private_store"],
            "actual_full_query_write_read_smoke": str(smoke_path),
        },
        "science": {
            "rows": 8,
            "rollouts_per_row": 4,
            "seeds": list(base.SEEDS),
            "temperature": 0.5,
            "max_tokens_per_call": 2048,
            "turn_budget": "maximum six completed turns total across root+child; depth1",
            "same_base_root_and_child": base.MODEL_ALIAS,
            "one_underlying_context": True,
            "external_object": "exact full CSV queries per row in /context.txt",
        },
        "claim_boundary": (
            "Calibration only; one underlying research-exposed context. V3 is an "
            "environment-binding failure and has no scientific outcome."
        ),
        "closure_sha256": closure,
    }
    ready["identity"] = base.digest(ready)
    base.write_x(ready_path, ready)
    print(
        json.dumps(
            {
                "ready": str(ready_path),
                "sha256": base.sha(ready_path),
                "identity": ready["identity"],
                "pytest": test.stdout.strip(),
                "collector": child.stdout.strip(),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
