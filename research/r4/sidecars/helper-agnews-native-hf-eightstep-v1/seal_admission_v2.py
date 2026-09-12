"""Seal the observed fresh-process admission regression and additive wrapper."""

import os

import core


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or (core.ROOT / "READY_V2.json").exists():
        raise ValueError("fresh CPU-only repair seal required")
    original = core.verify()
    receipt = core.read(core.ROOT / "ADMISSION_V2_CPU.json")
    if (receipt["returncode"] != 0 or not receipt["result"]["actual_initial_qualification_passed"]
            or receipt["result"]["attempt_directory_exists"]
            or receipt["result"]["admission_sha256"] != core.sha(core.ROOT / "ADMISSION.json")):
        raise ValueError("actual qualified admission receipt required")
    closure = dict(original["closure_sha256"])
    for name in ("READY.json", "owner_v2.py", "seal_admission_v2.py", "ADMISSION_REPAIR.md",
                 "ADMISSION_V2_CPU.json", "ADMISSION.json"):
        closure[str(core.ROOT / name)] = core.sha(core.ROOT / name)
    ready = {"schema": "agnews-eightstep-admission-repair-ready-v2",
        "original_ready_sha256": core.sha(core.ROOT / "READY.json"),
        "original_training_identity": original["identity"],
        "status": "CPU_QUALIFIED_ADMISSION_REPAIR_MAIN_LAUNCH_ONLY",
        "repair": "scoped ag_study alias spans actual original complete admission qualification",
        "optimizer_or_probability_changes": False,
        "admission_sha256": core.sha(core.ROOT / "ADMISSION.json"),
        "owner_seconds": 5000, "external_seconds": 5200,
        "output": str(core.ATTEMPT),
        "command": [str(core.original.NATIVE), str(core.ROOT / "owner_v2.py"), "run",
                    "--owner-seconds", "5000", "--admission-json", str(core.ROOT / "ADMISSION.json")],
        "closure_sha256": closure, "GPU_launched": False}
    ready["identity"] = core.digest(ready)
    core.write_x(core.ROOT / "READY_V2.json", ready)
    print({"ready_sha256": core.sha(core.ROOT / "READY_V2.json"), "identity": ready["identity"],
           "closure_files": len(closure), "command": ready["command"]})


if __name__ == "__main__":
    main()
