"""CPU-only seal for the additive stopped-policy evaluator."""

import json
import os
import subprocess
import time

import study


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "": raise ValueError("CPU-only seal")
    ready_path = study.ROOT / "READY.json"
    if ready_path.exists(): raise FileExistsError(ready_path)
    tests = subprocess.run([str(study.NATIVE), "-m", "pytest", "-q", "test_step3.py"],
        cwd=study.ROOT, capture_output=True, text=True, timeout=180,
        env={**os.environ, "CUDA_VISIBLE_DEVICES": ""})
    study.write_x(study.ROOT / "CPU_TESTS.json", {"returncode": tests.returncode,
        "stdout": tests.stdout, "stderr": tests.stderr})
    if tests.returncode: raise ValueError("CPU tests failed")
    upstream_ready = study.UPSTREAM / "READY_LR10X_V3.json"
    paths = [study.ROOT / name for name in ("study.py", "owner.py", "test_step3.py", "seal.py", "CPU_TESTS.json")]
    paths += [upstream_ready, study.UPSTREAM / "arm_eval_study.py", study.UPSTREAM / "arm_eval_study_v2.py",
        study.UPSTREAM / "arm_eval_study_v3.py"]
    eligibility = study.qualify(); action = eligibility["update4_action_eligibility"]
    value = {"schema": "helper-hf-lr10x-stopped-step3-unseen-ready-v1",
        "status": "CPU_READY_CONDITIONAL_EXACT_LR10X_ZERO_ADVANTAGE_STEP3",
        "created_epoch": time.time(),
        "question": "What is the fixed256 readout of the exact checkpoint-3 policy at the mechanistic zero-advantage stop?",
        "interpretation": "Adaptive stopped-policy readout; not the prespecified fixed-fourstep primary and not checkpoint selection by evaluation.",
        "command": [str(study.NATIVE), str(study.ROOT / "owner.py"), "run", "--outer-seconds", "600"],
        "inner_cap_seconds": 600, "external_timeout_seconds": 700,
        "inventory": {"trec_test": 128, "ag_news_test": 128, "predictions": 256,
            "physical_calls": 64, "batch_size": 4, "root_calls": 0, "training_updates": 0},
        "checkpoint": eligibility["checkpoint"], "checkpoint_state_sha256": eligibility["checkpoint_state_sha256"],
        "training_result_sha256": eligibility["training_result_sha256"],
        "update4_action_evidence": {k: action[k] for k in ("fresh_actions", "probability_qualified_actions",
            "correct_actions", "wrong_actions", "all_correct_groups", "all_wrong_groups", "mixed_groups",
            "within_question_rloo_nonzero_actions", "hypothetical_other31_nonzero_actions")},
        "schedule_sha256": study.digest(study.schedule()),
        "reference_eval_ready": str(upstream_ready), "reference_eval_ready_sha256": study.sha(upstream_ready),
        "closure_sha256": {str(path): study.sha(path) for path in paths},
        "cpu_tests": tests.stdout.strip()}
    value["identity"] = study.digest(value); study.write_x(ready_path, value)
    print(json.dumps({"path": str(ready_path), "sha256": study.sha(ready_path), "identity": value["identity"]}, sort_keys=True))


if __name__ == "__main__": main()
