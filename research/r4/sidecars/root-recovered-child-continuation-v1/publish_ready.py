"""CPU-only publication after completed, immutable focused qualifications."""

import json
import os
import xml.etree.ElementTree as ET
from pathlib import Path

import common as a

c = a.c


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("publication must run with GPUs hidden")
    amendment = a.verify_amendment()
    policies = a.prior_policies()
    suites = ET.parse(a.ROOT / "FOCUSED_GREEN.xml").getroot()
    counters = {key: sum(int(suite.attrib.get(key, 0)) for suite in suites.iter("testsuite"))
                for key in ("tests", "errors", "failures", "skipped")}
    if counters != {"tests": 20, "errors": 0, "failures": 0, "skipped": 0}:
        raise ValueError("focused qualification counters differ")
    first = c.read(a.ROOT / "FIRST_STAGE_PROOF.json")
    trainer = c.read(a.ROOT / "TRAINER_PREFLIGHT.json")
    rows = c.read(a.ROOT / "CPU_RECLASSIFICATION.json")
    if (first["amendment_id"] != amendment["amendment_id"]
            or first["step3_policy"] != policies[3]
            or first["gpu_calls"] or first["service_starts"] or first["subprocesses_launched"]
            or trainer["exit_code"] or trainer["gpu_calls"]
            or trainer["identity"]["generation"]["previous_policy"] != policies[3]
            or trainer["identity"]["continuation"]["amendment_id"] != amendment["amendment_id"]
            or trainer["identity"]["native_replay"]["replayed"] != 32
            or trainer["identity"]["native_replay"]["selected"] != 19
            or rows["admitted_before"] != 29 or rows["admitted_after"] != 29
            or not rows["existing_row_fields_unchanged"] or rows["integrity_failures"]):
        raise ValueError("qualification identity or admission mismatch")
    result = {"amendment_id": amendment["amendment_id"], "focused_tests": counters,
              "actual_original_coordinator_first_stage": first["first_stage"],
              "actual_HF_trainer_and_native_subprocess_preflight": "passed",
              "preflight_training_group_episodes": 19, "admitted_before_and_after": 29,
              "old_stage_source_hashes_reverified": True, "old_stop_preserved": True,
              "original_validation_selection_rule_preserved": True,
              "cpu_only_preparation": True, "gpu_calls": 0,
              "publication_source_sha256": c.file_hash(Path(__file__))}
    c.write_once(a.ROOT / "QUALIFICATION.json", result)
    artifacts = ["README.md", "publish_ready.py", "QUALIFICATION.json", "FOCUSED_GREEN.xml",
                 "CPU_RECLASSIFICATION.json", "FIRST_STAGE_PROOF.json", "TRAINER_PREFLIGHT.json",
                 "prepared-round04/EPISODES.json", "prepared-round04/GROUP.json",
                 "prepared-round04/MANIFEST.json"]
    ready = {"namespace": a.ROOT.name, "status": "READY_CPU_ONLY_PARENT_LAUNCH",
             "amendment_id": amendment["amendment_id"],
             "amendment_sha256": c.file_hash(a.ROOT / "AMENDMENT.json"),
             "driver_sha256": c.file_hash(a.ROOT / "driver.py"),
             "artifact_sha256": {str(a.ROOT / name): c.file_hash(a.ROOT / name) for name in artifacts},
             "launch_command": [str(c.NATIVE_PYTHON), str(a.ROOT / "driver.py"), "run",
                                "--output", str(a.ROOT / "outputs/attempt-001")],
             "new_global_cap_seconds": a.CAP_SECONDS, "exact_starting_policy": policies[3],
             "admission_change": "none; exact29 remain admitted", "round04_rerolls": 0,
             "remaining_actual_steps": [4, 5, 6, 7, 8], "gpu_calls_during_preparation": 0}
    c.write_once(a.ROOT / "READY.json", ready)
    print(json.dumps({"ready_path": str(a.ROOT / "READY.json"),
                      "ready_sha256": c.file_hash(a.ROOT / "READY.json"),
                      "driver_sha256": ready["driver_sha256"], **result}, sort_keys=True))


if __name__ == "__main__":
    main()
