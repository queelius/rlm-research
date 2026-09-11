"""Seal additive V2 after the task-ledger visibility correction."""
import os
import subprocess
import time

import bv_study_v2 as s


def main():
    if (s.ROOT / "READY_v2.json").exists():
        raise FileExistsError("V2 already sealed")
    started = time.time()
    s.write(s.ROOT / "BINDING_sft24_v2.json", s.binding())
    tests = ["test_v2.py", "test_inputs.py", "test_entry.py"]
    argv = [
        str(s.NATIVE), "-m", "pytest", "-q", "-p", "no:cacheprovider", *tests,
        "--basetemp", str(s.ROOT / "qualification-v2-final"),
    ]
    result = subprocess.run(
        argv,
        cwd=s.ROOT,
        env={**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True,
        text=True,
        timeout=240,
    )
    s.write(
        s.ROOT / "CPU_REPORT_v2.json",
        {
            "argv": argv,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "scientific_model_calls": 0,
            "gpu_calls": 0,
            "authored_native_root_calls": 2,
            "task_cwd_raw_ledger": False,
            "existing_session_raw_log_harvested_post_rollout": True,
            "explicit_session_log_access_caveat": True,
            "v1_preserved_and_rejected_before_launch": True,
            "elapsed_seconds": time.time() - started,
        },
    )
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    sources = {
        **s.v1_ready["source_sha256"],
        str(s.ROOT / "READY.json"): s.V1_READY_SHA,
    }
    inputs = {**s.v1_ready["input_sha256"]}
    for name in (
        "bv_overlay_v2.py", "bv_study_v2.py", "bv_collect_v2.py", "bv_owner_v2.py",
        "test_v2.py", "AMENDMENT_V2.md", "seal_v2.py", "CPU_REPORT_v2.json",
        "BINDING_sft24_v2.json",
    ):
        path = s.ROOT / name
        sources[str(path)] = s.sha(path)
    inputs.update(
        {
            str(path): s.sha(path)
            for path in (s.ROOT / "qualification-v2-final").rglob("*")
            if path.is_file()
        }
    )
    for path, pin in {**sources, **inputs}.items():
        s.dose.check(path, pin)
    ready = {
        "schema": "bounded-observation-view-ready-v2",
        "status": "CPU_READY_MAIN_ACCEPTANCE_REQUIRED",
        "supersedes_unlaunched_ready_sha256": s.V1_READY_SHA,
        "source_sha256": sources,
        "input_sha256": inputs,
        "owner_argv": [
            str(s.NATIVE), str(s.ROOT / "bv_owner_v2.py"), "run", "--output", str(s.ATTEMPT)
        ],
        "verify_argv": [str(s.NATIVE), str(s.ROOT / "bv_owner_v2.py"), "verify"],
        "attempt": "attempt-002",
        "planned_full": 32,
        "work_seconds": 1650,
        "owned_seconds": 1770,
        "outer_seconds": 1800,
        "startup_seconds": 180,
        "collection_seconds": 1440,
        "release_seconds": 120,
        "harvest_seconds": 30,
        "outer_margin_seconds": 30,
        "scientific_inputs_unchanged_from_v1": True,
        "task_cwd_raw_ledger": False,
        "session_tree_harvest_after_rollout": True,
        "passive_policy_view_only": True,
        "session_log_explicit_access_caveat": True,
        "view_cap_is_retained_payload_bytes_excluding_marker_overhead": True,
        "main_launch_only": True,
        "created_epoch": time.time(),
    }
    ready["identity"] = s.digest(ready)
    s.write(s.ROOT / "READY_v2.json", ready)
    s.verify()
    print(
        {
            "ready_sha256": s.sha(s.ROOT / "READY_v2.json"),
            "identity": ready["identity"],
            "sources": len(sources),
            "inputs": len(inputs),
            "tests": result.stdout,
            "elapsed_seconds": time.time() - started,
        }
    )


if __name__ == "__main__":
    main()
