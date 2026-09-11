"""Seal additive V2 after focused CPU qualification."""
from datetime import datetime, timezone
import recovery_study as s


def main():
    target = s.SOURCE_ROOT / "READY_v2.json"
    if target.exists(): raise FileExistsError("V2 already sealed")
    source_names = (
        "recovery_study.py", "recovery_collect.py", "recovery_readout.py", "recovery_train.py",
        "recovery_binding.py", "recovery_owner.py", "prepare.py", "test_recovery.py", "DESIGN.md", "PLAN.md",
        "recovery_binding_v2.py", "recovery_readout_v2.py", "recovery_owner_v2.py", "test_recovery_v2.py",
        "V2_AMENDMENT.md", "seal_v2.py")
    sources = [s.SOURCE_ROOT / name for name in source_names]
    v1 = s.read(s.SOURCE_ROOT / "READY.json")
    ready = {"schema": "question-sensitive-sft72-recovery-ready-v2",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "supersedes_preacceptance_ready_sha256": s.sha(s.SOURCE_ROOT / "READY.json"),
        "v1_gpu_launched": False, "science_changed": False,
        "source_sha256": {str(path): s.sha(path) for path in sources},
        "input_sha256": {**v1["input_sha256"], str(s.SOURCE_ROOT / "READY.json"): s.sha(s.SOURCE_ROOT / "READY.json")},
        "entry": str(s.SOURCE_ROOT / "recovery_owner_v2.py"), "attempt": str(s.ATTEMPT),
        "capture_slice": [65, 72], "reused_teachers": 65, "baseline_reused": 80,
        "sft6_readout": 80, "outer_seconds": 5400, "combined_ceiling_seconds": 10800,
        "qualification": {"focused_tests": 6, "test_command":
            "python -m pytest -q -p no:cacheprovider test_recovery.py test_recovery_v2.py",
            "binding_lazy_import_fixed": True}}
    ready["identity"] = s.digest(ready); s.write(target, ready); print(ready["identity"])


if __name__ == "__main__": main()

