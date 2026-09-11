"""Freeze post-failure boundary and additive recovery READY; CPU only."""
from datetime import datetime, timezone
import recovery_study as s


def main():
    target = s.SOURCE_ROOT / "inputs/RECOVERY_BOUNDARY.json"
    if target.exists() or (s.SOURCE_ROOT / "READY.json").exists():
        raise FileExistsError("one-time recovery freeze")
    rows = s.capture_boundary(); pins = {}
    for row in rows:
        directory = s.ORIGINAL_ATTEMPT / "capture" / row["id"]
        if directory.exists():
            for path in sorted(directory.rglob("*.json")): pins[str(path)] = s.sha(path)
    receipt = {"created_utc": datetime.now(timezone.utc).isoformat(), "rows": rows,
        "counts": {"reuse_authenticated_teacher": 65,
                   "retry_after_pre_request_deadline_failure": 1,
                   "first_attempt_after_original_unstarted": 6},
        "original_artifact_sha256": pins,
        "selection": "fixed plan prefix/tail from serial deadline; no outcome/gold/success selection",
        "index65_dispatch_evidence": "zero physical, role-audit, and typed-audit records; FAILURE during deadline cancellation/cleanup",
        "original_calls_preserved_and_charged": True}
    s.write(target, receipt)
    sources = [s.SOURCE_ROOT / name for name in (
        "recovery_study.py", "recovery_collect.py", "recovery_readout.py", "recovery_train.py",
        "recovery_binding.py", "recovery_owner.py", "prepare.py", "test_recovery.py", "DESIGN.md", "PLAN.md")]
    inherited = [s.ORIGINAL / name for name in ("READY.json", "inputs/TRAIN_PLAN.json",
        "inputs/DEV_PLAN.json", "inputs/FREE_PLAN.json", "inputs/EVALUATION_PLAN.json",
        "inputs/START_BINDING.json", "inputs/NATIVE_TEMPLATE.json")]
    inputs = {str(p): s.sha(p) for p in [target, *inherited]}
    inputs.update(pins)
    ready = {"schema": "question-sensitive-sft72-recovery-ready-v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_sha256": {str(p): s.sha(p) for p in sources}, "input_sha256": inputs,
        "original_ready_sha256": s.sha(s.ORIGINAL / "READY.json"),
        "attempt": str(s.ATTEMPT), "capture_slice": [65, 72], "reused_teachers": 65,
        "new_or_explicit_retry_teachers": 7, "readout": {"baseline_reused": 80, "sft6_new": 80},
        "budgets_seconds": {"outer": 5400, "owned": 5370, "work": 5220,
                            "capture": 600, "training": 2100, "sft6": 2100, "finalize": 420,
                            "cleanup_reserve": 150, "outer_margin": 30, "combined_ceiling": 10800},
        "gpu_launched_by_author": False}
    ready["identity"] = s.digest(ready); s.write(s.SOURCE_ROOT / "READY.json", ready)
    print(ready["identity"])


if __name__ == "__main__": main()

