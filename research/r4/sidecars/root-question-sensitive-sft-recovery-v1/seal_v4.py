"""Seal the owner-only V4 amendment; V3 remains the cross-process science identity."""
from datetime import datetime, timezone
import recovery_study_v3 as s


def main():
    target = s.SOURCE_ROOT / "READY_v4.json"
    if target.exists(): raise FileExistsError("V4 already sealed")
    names = ("recovery_owner_v4.py", "test_recovery_v4.py", "V4_AMENDMENT.md", "seal_v4.py")
    v3 = s.SOURCE_ROOT / "READY_v3.json"
    ready = {"schema": "question-sensitive-sft72-recovery-owner-amendment-v4",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_sha256": {str(s.SOURCE_ROOT / name): s.sha(s.SOURCE_ROOT / name) for name in names},
        "input_sha256": {str(v3): s.sha(v3)},
        "entry": str(s.SOURCE_ROOT / "recovery_owner_v4.py"), "attempt": str(s.ATTEMPT),
        "science_identity": s.verify()["identity"], "science_changed": False,
        "v1_v2_v3_gpu_launched": False,
        "fix": "service-local status explicitly passed to readout deadline computation",
        "qualification": {"test": "test_recovery_v4.py", "actual_owner_flow": True,
            "simulated_nonzero_capture_training_startup_dev_elapsed": True, "dev_failure_retained": True}}
    ready["identity"] = s.digest(ready); s.write(target, ready); print(ready["identity"])


if __name__ == "__main__": main()

