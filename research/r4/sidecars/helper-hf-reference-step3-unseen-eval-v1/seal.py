"""CPU-only seal for the reference checkpoint-3 control."""

import json
import os
import subprocess
import time

import study


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "": raise ValueError("CPU-only seal")
    path = study.ROOT / "READY.json"
    if path.exists(): raise FileExistsError(path)
    tests = subprocess.run([str(study.NATIVE), "-m", "pytest", "-q", "test_reference_step3.py"],
        cwd=study.ROOT, capture_output=True, text=True, timeout=180,
        env={**os.environ, "CUDA_VISIBLE_DEVICES": ""})
    study.write_x(study.ROOT / "CPU_TESTS.json", {"returncode": tests.returncode,
        "stdout": tests.stdout, "stderr": tests.stderr})
    if tests.returncode: raise ValueError("tests failed")
    receipt = study.qualify(); source_ready = study.SOURCE_EVAL / "READY.json"
    files = [study.ROOT / name for name in ("study.py", "owner.py", "test_reference_step3.py",
        "SATURATION_ESCAPE_PROPOSAL.md", "seal.py", "CPU_TESTS.json")]
    files += [source_ready, study.SOURCE_EVAL / "fourstep_panel_study.py"]
    value = {"schema": "helper-hf-reference-step3-unseen-ready-v1",
        "status": "CPU_READY_REFERENCE_MATCHED_THREE_UPDATE_CONTROL", "created_epoch": time.time(),
        "question": "At an equal three applied updates, how does reference T1/LR1e-5 compare with stopped LR10x?",
        "interpretation": "Matched-update reference checkpoint; not the reference fixed-fourstep primary and not selected by evaluation.",
        "command": [str(study.NATIVE), str(study.ROOT / "owner.py"), "run", "--outer-seconds", "600"],
        "inner_cap_seconds": 600, "external_timeout_seconds": 700,
        "inventory": {"trec_test": 128, "ag_news_test": 128, "predictions": 256,
            "physical_calls": 64, "batch_size": 4, "root_calls": 0, "training_updates": 0},
        "checkpoint": receipt["checkpoint"], "checkpoint_state_sha256": receipt["checkpoint_state_sha256"],
        "final_checkpoint_state_sha256": receipt["final_checkpoint_state_sha256"],
        "training_result_sha256": receipt["training_result_sha256"],
        "schedule_sha256": study.digest(study.schedule()),
        "source_eval_ready": str(source_ready), "source_eval_ready_sha256": study.sha(source_ready),
        "closure_sha256": {str(file): study.sha(file) for file in files}, "cpu_tests": tests.stdout.strip()}
    value["identity"] = study.digest(value); study.write_x(path, value)
    print(json.dumps({"path": str(path), "sha256": study.sha(path), "identity": value["identity"]}, sort_keys=True))


if __name__ == "__main__": main()
