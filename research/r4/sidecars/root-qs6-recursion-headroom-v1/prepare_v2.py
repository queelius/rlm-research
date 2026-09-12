"""Seal the additive task-table/export correction without changing READY V1."""

import os
import subprocess
import time

import collect_v2
import study


def main():
    ready_path = study.ROOT / "READY_V2.json"
    if ready_path.exists() or (study.ROOT / "TASKS_V2.json").exists():
        raise ValueError("V2 seal already exists")
    study.write(study.ROOT / "TASKS_V2.json", collect_v2.task_tables())
    collect_v2.task_tables.cache_clear()
    # Validate the frozen table through the actual patched collector lookup.
    for block_index, mode in ((0, "no_child"), (1, "enabled")):
        collect_v2.activate(block_index, mode)
        table = collect_v2.terminal_study.read(study.SOURCE_INPUTS / "TASKS.json")
        if table != collect_v2.task_tables()["modes"][mode]:
            raise ValueError("collector/export TASKS seam differs from frozen V2 table")
    prior = os.environ.get("STRICT_RLM_CALIBRATION_API_KEY")
    os.environ["STRICT_RLM_CALIBRATION_API_KEY"] = "cpu-structure-only"
    try:
        child = subprocess.run(
            [str(study.NATIVE), "-c",
             "import collect_v2 as c; c.activate(0,'no_child'); "
             "m=c.qualified.qualified.impl; r,a=m.s.runtime(); "
             "assert r.ROOT==c.study.ALLOCATION_RUNTIME; "
             "assert a.SERVICE==c.study.ALLOCATION_RUNTIME/'service_wrapper_v2.py'; "
             "assert m.verify_spec is c.verify_spec"],
            cwd=study.ROOT, env={**os.environ, "CUDA_VISIBLE_DEVICES": "",
                                "PYTHONDONTWRITEBYTECODE": "1"},
            text=True, capture_output=True, timeout=60)
        if child.returncode:
            raise RuntimeError(child.stdout + child.stderr)
    finally:
        if prior is None: os.environ.pop("STRICT_RLM_CALIBRATION_API_KEY", None)
        else: os.environ["STRICT_RLM_CALIBRATION_API_KEY"] = prior
    v1 = study.read(study.ROOT / "READY.json")
    paths = {**v1["closure_sha256"]}
    for name in ("collect_v2.py", "study_v2.py", "owner_v2.py", "prepare_v2.py",
                 "test_prefix_export_v2.py", "TASKS_V2.json"):
        path = study.ROOT / name
        paths[str(path)] = study.sha(path)
    ready = {
        "schema": "root-qs6-recursion-headroom-ready-v2",
        "status": "CPU_READY_FOR_MAIN_GPU_LAUNCH",
        "created_epoch": time.time(),
        "parent_ready_sha256": study.sha(study.ROOT / "READY.json"),
        "repaired_defect": "collector/export previously read old TASKS prefixes after the common prompt changed",
        "old_ready_must_not_launch": True,
        "fixed_argv": [str(study.NATIVE), str(study.ROOT / "owner_v2.py"), "run",
                       "--output", str(study.ATTEMPT), "--outer-seconds", str(study.OUTER_SECONDS)],
        "closure_sha256": paths,
    }
    ready["identity"] = study.digest({k: value for k, value in ready.items() if k != "identity"})
    study.write(ready_path, ready)
    print(study.sha(ready_path), ready["identity"])


if __name__ == "__main__":
    main()
