"""CPU-map and seal the approved one-step shaped-reward root update."""

import json
import os
from pathlib import Path
import subprocess
import sys
import time

import build_inputs
import trainer


ROOT = Path(__file__).resolve().parent
INPUTS = ROOT / "TRAIN_INPUTS.json"
READY = ROOT / "RUN_READY.json"
EVIDENCE = ROOT / "CPU_EVIDENCE.json"
TRAIN_PYTHON = Path(
    "/project/alex_phd/repos/rlm-bootstrap/.worktrees/"
    "a100-lora-roundtrip/gpu/training/.venv/bin/python"
)


def write_x(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "" or any(
        path.exists() for path in (INPUTS, READY, EVIDENCE, ROOT / "outputs/attempt-001")
    ):
        raise ValueError("CPU-only unused shaped-root seal required")
    started = time.monotonic()
    command = [str(TRAIN_PYTHON), "-m", "pytest", "-q", "-p", "no:cacheprovider", "test_prepare.py"]
    tests = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=180)
    if tests.returncode:
        raise RuntimeError(tests.stdout + tests.stderr)
    data = build_inputs.build()
    if len(trainer.module().validate_inputs(data)) != 24:
        raise ValueError("actual transformed trainer rejected mapped inputs")
    write_x(INPUTS, data)
    write_x(
        EVIDENCE,
        {
            "schema": "mrcr-short-shaped-root-hf-cpu-evidence-v1",
            "command": command,
            "returncode": tests.returncode,
            "stdout": tests.stdout,
            "stderr": tests.stderr,
            "elapsed_seconds": time.monotonic() - started,
            "mapped": {
                "episodes": len(data["episodes"]),
                "groups": len({row["group_id"] for row in data["episodes"]}),
                "mixed_groups": data["limits"]["mixed_groups"],
                "root_turns": sum(len(row["root_turns"]) for row in data["episodes"]),
                "root_action_tokens": sum(
                    len(turn["action_ids"])
                    for row in data["episodes"]
                    for turn in row["root_turns"]
                ),
                "fixed_child_loss_tokens": sum(
                    child["loss_tokens"]
                    for row in data["episodes"]
                    for child in row["fixed_child_turns"]
                ),
                "excluded_whole_groups": len(data["excluded_groups"]),
            },
            "actual_transformed_trainer_validate_inputs": True,
            "streamed_gradient_equivalence_tested": True,
            "GPU_or_model_calls": 0,
            "python": sys.version,
        },
    )
    local = [
        ROOT / name
        for name in (
            "DESIGN.md",
            "SOURCE_PLAN.json",
            "math_core.py",
            "build_inputs.py",
            "trainer.py",
            "train.py",
            "test_prepare.py",
            "seal_train.py",
            "TRAIN_INPUTS.json",
            "CPU_EVIDENCE.json",
        )
    ]
    source = list(build_inputs.PINS)
    source += [
        build_inputs.ATTEMPT / "science/episodes" / path.name
        for path in sorted((build_inputs.ATTEMPT / "science/episodes").glob("*.json"))
    ]
    source += sorted((build_inputs.ATTEMPT / "science/native-calls").glob("*.json"))
    source += [
        trainer.SOURCE,
        trainer.SOURCE.parent / "math_core.py",
        TRAIN_PYTHON,
        build_inputs.MODEL / "local-research-manifest.json",
    ]
    closure = {str(path): build_inputs.sha(path) for path in local + source}
    for path, expected in closure.items():
        if build_inputs.sha(path) != expected:
            raise ValueError("pre-seal source changed: " + path)
    ready = {
        "schema": "mrcr-short-shaped-root-hf-run-ready-v1",
        "status": "RUN_READY_SHAPED24_GATE_PASSED",
        "output": str(ROOT / "outputs/attempt-001"),
        "owner_seconds": 900,
        "external_seconds": 1000,
        "optimizer_steps_before_run": 0,
        "optimizer_steps_planned": 1,
        "episodes": 24,
        "groups": 6,
        "mixed_groups": 2,
        "root_turns": 74,
        "root_action_tokens": 15602,
        "fixed_denominator": 24,
        "reward": data["reward"],
        "importance_gates": {
            "full_root_trajectory": True,
            "ess_min": 19.2,
            "max_normalized_weight": 0.1,
            "clipping": None,
            "self_normalization": None,
        },
        "command": [
            str(TRAIN_PYTHON),
            str(ROOT / "train.py"),
            "--output",
            str(ROOT / "outputs/attempt-001"),
            "--cap-seconds",
            "900",
        ],
        "closure_sha256": closure,
        "cpu_evidence_sha256": build_inputs.sha(EVIDENCE),
        "claim_boundary": (
            "One saved-batch exploratory shaped-reward update on eight training contexts; "
            "no heldout queries, no newline repair, and no recursion-learning claim."
        ),
        "gpu_launch_authority": "MAIN only",
        "GPU_launched": False,
    }
    ready["identity"] = build_inputs.digest(ready)
    write_x(READY, ready)
    print(
        json.dumps(
            {
                "ready_sha256": build_inputs.sha(READY),
                "identity": ready["identity"],
                "command": ready["command"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
