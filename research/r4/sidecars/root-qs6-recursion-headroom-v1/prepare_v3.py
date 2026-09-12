"""Seal the final fresh-process argv correction, preserving READY V1/V2."""

import time

import study


def main():
    path = study.ROOT / "READY_V3.json"
    if path.exists():
        raise ValueError("READY_V3 already exists")
    parent = study.read(study.ROOT / "READY_V2.json")
    closure = dict(parent["closure_sha256"])
    for name in ("READY_V2.json", "study_v3.py", "owner_v3.py", "collect_v3.py", "prepare_v3.py",
                 "test_owner_v3.py", "audit_v3.py", "CPU_PATH_AUDIT_V3_FINAL.json"):
        item = study.ROOT / name
        closure[str(item)] = study.sha(item)
    ready = {
        "schema": "root-qs6-recursion-headroom-ready-v3",
        "status": "CPU_READY_FOR_MAIN_GPU_LAUNCH",
        "created_epoch": time.time(),
        "parent_ready_v2_sha256": study.sha(study.ROOT / "READY_V2.json"),
        "repaired_defect": "parent owner hardcoded collect.py for the fresh subprocess",
        "old_ready_v1_v2_must_not_launch": True,
        "fixed_argv": [str(study.NATIVE), str(study.ROOT / "owner_v3.py"), "run",
                       "--output", str(study.ATTEMPT), "--outer-seconds",
                       str(study.OUTER_SECONDS)],
        "closure_sha256": closure,
    }
    ready["identity"] = study.digest({k: value for k, value in ready.items() if k != "identity"})
    study.write(path, ready)
    print(study.sha(path), ready["identity"])


if __name__ == "__main__":
    main()
