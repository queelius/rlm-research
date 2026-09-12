"""CPU-test and conditionally seal both paired step-1 fixed-panel evaluators."""

import os
import subprocess
import time

import paired_eval_study as study


C32_READY_SHA256 = "23983b507125656d197a6b86a6bca2a945e99bf853513d3cb2be6af4a6498739"
C32_READY_IDENTITY = "8844a483f05dcd15a4bbc7776051f484522d0d6cc400c83e96c1e6d19c50cdb7"


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("seal CPU-only with the GPU hidden")
    if any(row["ready"].exists() or row["attempt"].exists() for row in study.ARMS.values()):
        raise ValueError("preserve evaluator READYs and require unused attempts")
    training_ready = study.read(study.TRAINING / "READY.json")
    if (
        study.sha(study.TRAINING / "READY.json") != study.TRAIN_READY_SHA256
        or training_ready.get("identity") != study.TRAIN_READY_IDENTITY
    ):
        raise ValueError("paired trainer READY differs")
    for raw, expected in training_ready["closure_sha256"].items():
        if study.sha(raw) != expected:
            raise ValueError("paired trainer closure changed: " + raw)
    c32_ready_path = study.C32_EVAL / "READY.json"
    c32_ready = study.read(c32_ready_path)
    if (
        study.sha(c32_ready_path) != C32_READY_SHA256
        or c32_ready.get("identity") != C32_READY_IDENTITY
    ):
        raise ValueError("source fixed-panel collector READY differs")
    for raw, expected in c32_ready["closure_sha256"].items():
        if study.sha(raw) != expected:
            raise ValueError("source collector closure changed: " + raw)
    rows = study.schedule()
    if (
        len(rows) != 64
        or len({identifier for row in rows for identifier in row["ids"]}) != 256
        or any(row["body"]["sampling_params"]["temperature"] != 0 for row in rows)
    ):
        raise ValueError("fixed unseen256 schedule differs")
    command = [str(study.NATIVE), "-m", "pytest", "-q", "test_eval.py"]
    started = time.monotonic()
    completed = subprocess.run(
        command,
        cwd=study.ROOT,
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "CUDA_VISIBLE_DEVICES": ""},
    )
    tests = {
        "schema": "helper-hf-other31-paired-eval-cpu-tests-v1",
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "elapsed_seconds": time.monotonic() - started,
        "actual_collector_build": True,
        "collector_zero_argument_verify": True,
        "actual_dependency_chain": True,
        "binding_root_and_child_seams": True,
    }
    study.write_x(study.ROOT / "CPU_TESTS.json", tests)
    if completed.returncode:
        raise RuntimeError("focused paired evaluator tests failed")
    own = [
        study.ROOT / name
        for name in (
            "paired_eval_study.py",
            "owner.py",
            "test_eval.py",
            "seal.py",
            "CPU_TESTS.json",
        )
    ]
    direct = [
        study.TRAINING / "READY.json",
        study.TRAINING / "EVALUATION_INTERFACE.md",
        study.SOURCE_EVAL / "fourstep_panel_study.py",
        study.C32_EVAL / "READY.json",
        study.C32_EVAL / "owner.py",
        study.C32_EVAL / "unseen_panel_study.py",
        study.NATIVE,
    ]
    common_closure = dict(c32_ready["closure_sha256"])
    for raw, expected in training_ready["closure_sha256"].items():
        if raw in common_closure and common_closure[raw] != expected:
            raise ValueError("trainer and evaluator source closures disagree: " + raw)
        common_closure[raw] = expected
    common_closure.update({str(path): study.sha(path) for path in own + direct})
    written = {}
    for branch in study.ARMS:
        value = {
            **study.plan(branch),
            "closure_sha256": common_closure,
            "training_ready": {
                "path": str(study.TRAINING / "READY.json"),
                "identity": training_ready["identity"],
                "sha256": study.sha(study.TRAINING / "READY.json"),
                "full_recursive_closure_verified": True,
            },
            "conditional_eligibility": (
                "Both paired branch results must be UPDATED from the exact same authenticated "
                "128-action collection; branch step1 Adam/checkpoint commit, c32 pre-step and "
                "other31 restore receipts, exact probability gates, and unchanged root binding "
                "are verified before service startup."
            ),
            "evaluation_interface": str(study.TRAINING / "EVALUATION_INTERFACE.md"),
            "panel_source": {
                "c32_ready_identity": c32_ready["identity"],
                "c32_ready_sha256": study.sha(c32_ready_path),
                "schedule_sha256": study.digest(rows),
            },
            "claim_boundary": (
                "Adaptive reuse of the fixed256 panel after one exploratory update on previously "
                "used training contexts; no checkpoint selection, pristine-generalization, "
                "independent-replication, root-performance, or novelty claim."
            ),
            "gpu_launched": False,
            "created_epoch": time.time(),
            "cpu_tests": tests["stdout"].strip(),
        }
        value["identity"] = study.digest(value)
        study.write_x(study.ready_path(branch), value)
        written[branch] = {
            "path": str(study.ready_path(branch)),
            "identity": value["identity"],
            "sha256": study.sha(study.ready_path(branch)),
        }
    for branch in study.ARMS:
        study.verify(branch, require_training=False)
    print(written)


if __name__ == "__main__":
    main()
