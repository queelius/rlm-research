"""Seal V3 coherent recovery entries before integrated qualification."""
from datetime import datetime, timezone
import recovery_study as base


def main():
    target = base.SOURCE_ROOT / "READY_v3.json"
    if target.exists(): raise FileExistsError("V3 already sealed")
    names = ("recovery_study_v3.py", "recovery_binding_v3.py", "recovery_collect_v3.py",
        "recovery_readout_v3.py", "recovery_train_v3.py", "recovery_owner_v3.py",
        "test_recovery_v3.py", "V3_AMENDMENT.md", "seal_v3.py")
    sources = {str(base.SOURCE_ROOT / name): base.sha(base.SOURCE_ROOT / name) for name in names}
    # V2 closes every unchanged inherited source/input; V3 additionally pins each changed entry.
    v2_path = base.SOURCE_ROOT / "READY_v2.json"; v2 = base.read(v2_path)
    inputs = {**v2["input_sha256"], str(v2_path): base.sha(v2_path)}
    ready = {"schema": "question-sensitive-sft72-recovery-ready-v3",
        "created_utc": datetime.now(timezone.utc).isoformat(), "source_sha256": sources,
        "input_sha256": inputs, "supersedes_preacceptance_v2_sha256": base.sha(v2_path),
        "v1_v2_gpu_launched": False, "science_changed": False,
        "entry": str(base.SOURCE_ROOT / "recovery_owner_v3.py"), "attempt": str(base.ATTEMPT),
        "cross_process_identity": "READY_v3 at capture/corpus/trainer/binding/readout/owner",
        "capture_slice": [65, 72], "reused_teachers": 65, "baseline_reused": 80,
        "sft6_readout": 80, "outer_seconds": 5400, "combined_ceiling_seconds": 10800,
        "protected_deadline": "min(stage_end, stage_started+1950+actual_dev_elapsed-90)",
        "usage": "qualified per-field known/unknown input/output/cache",
        "qualification": {"focused_tests": 5, "integrated_combined72_to_trainer_loader": True,
            "model_loaded": False, "gpu_launched": False}}
    ready["identity"] = base.digest(ready); base.write(target, ready); print(ready["identity"])


if __name__ == "__main__": main()

