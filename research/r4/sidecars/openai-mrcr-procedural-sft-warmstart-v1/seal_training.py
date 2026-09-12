"""Seal the already-approved fixed procedural SFT command after focused CPU tests."""

import json
import os
from pathlib import Path
import subprocess
import time

import training


ROOT = Path(__file__).resolve().parent
TRAIN_PYTHON = Path(
    "/project/alex_phd/repos/rlm-bootstrap/.worktrees/"
    "a100-lora-roundtrip/gpu/training/.venv/bin/python"
)
NATIVE_PYTHON = Path("/project/alex_phd/envs/prime-rl-5990b1b/bin/python")


def run_test(python: Path, target: str) -> dict:
    process = subprocess.run(
        [str(python), "-m", "pytest", "-q", target],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        env={**os.environ, "CUDA_VISIBLE_DEVICES": ""},
    )
    return {
        "argv": [str(python), "-m", "pytest", "-q", target],
        "returncode": process.returncode,
        "stdout": process.stdout,
        "stderr": process.stderr,
    }


def seal() -> dict:
    tests = {
        "teacher": run_test(NATIVE_PYTHON, "test_teacher.py"),
        "training": run_test(TRAIN_PYTHON, "test_train.py"),
    }
    if any(value["returncode"] for value in tests.values()):
        raise ValueError("focused CPU test failed")
    training.write_x(ROOT / "CPU_TESTS_TRAINING.json", tests)
    smoke = json.loads((ROOT / "CPU_TEACHER_CONTAINER_SMOKE.json").read_text())
    if not (
        smoke.get("passed")
        and smoke.get("first_provider_prefix_equal_corpus")
        and smoke.get("terminal_provider_prefix_equal_corpus")
        and smoke.get("provider_requests") == smoke.get("native_returned") == 2
    ):
        raise ValueError("actual container/provider teacher-prefix smoke did not pass")
    corpus = json.loads((ROOT / "TEACHER_CORPUS_V2.json").read_text())
    summary = training.validate_corpus(corpus)
    closure = {}
    for path in [
        ROOT / "DESIGN.md",
        ROOT / "EVALUATION_INTERFACE.md",
        ROOT / "teacher.py",
        ROOT / "training.py",
        ROOT / "train.py",
        ROOT / "prepare.py",
        ROOT / "seal_training.py",
        ROOT / "test_teacher.py",
        ROOT / "test_train.py",
        ROOT / "cpu_teacher_container_smoke.py",
        ROOT / "CPU_READY_TEACHER_V2.json",
        ROOT / "CPU_TEACHER_CONTAINER_SMOKE.json",
        ROOT / "cpu-teacher-container-smoke/EPISODE.json",
        ROOT / "cpu-teacher-container-smoke/PROVIDER_REQUESTS.json",
        ROOT / "CPU_TESTS_TRAINING.json",
        ROOT / "TEACHER_AUDIT_V2.json",
        ROOT / "TEACHER_CORPUS_V2.json",
        ROOT / "RENDERER_FIXTURE_V2.json",
        training.OLD_LEARNING,
        training.BASE / "local-research-manifest.json",
    ]:
        closure[str(path)] = training.sha(path)
    value = {
        "schema": "openai-mrcr-procedural-sft-training-ready-v1",
        "status": "CPU_READY_CONDITIONAL_ON_MAIN_POST_SHORT32_GPU_DECISION",
        "created_epoch": time.time(),
        "identity_basis": "immutable all32 teacher and fixed four-update recipe; no evaluation selection",
        "recipe": training.recipe(),
        "corpus": summary,
        "teacher_exact": 32,
        "teacher_failures": 0,
        "actual_container_teacher_prefixes_verified": 2,
        "heldout_records_used": 0,
        "optimizer_steps_completed": 0,
        "gpu_calls": 0,
        "closure_sha256": closure,
        "fixed_argv": [
            str(TRAIN_PYTHON),
            str(ROOT / "train.py"),
            "run",
            "--output",
            str(ROOT / "outputs/attempt-001"),
            "--seconds",
            "600",
        ],
        "verify_argv": [str(TRAIN_PYTHON), str(ROOT / "train.py"), "verify"],
        "training_cap_seconds": 600,
        "external_cap_seconds": 700,
        "gpu_launch_authority": "MAIN only",
        "evaluation": "conditional interface only; heldout evaluator not yet sealed",
    }
    value["identity"] = training.digest(value)
    training.write_x(ROOT / "READY_TRAINING.json", value)
    return value


if __name__ == "__main__":
    print(json.dumps(seal(), sort_keys=True))
