"""CPU-only conditional seal of the three fixed held16 readout arms."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import time

import collect
import owner
import study


def main():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "":
        raise ValueError("CPU-only preparation requires hidden CUDA")
    if study.READY.exists() or any(path.exists() for path in owner.STAGES.values()):
        raise FileExistsError("READY or fixed output already exists")
    source_ready = study.verify_frozen_inputs()
    command = [str(study.NATIVE), "-m", "pytest", "-q", "test_eval.py"]
    tested = subprocess.run(
        command,
        cwd=study.ROOT,
        env={**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    study.write_x(
        study.ROOT / "CPU_TESTS.json",
        {
            "argv": command,
            "returncode": tested.returncode,
            "stdout": tested.stdout,
            "stderr": tested.stderr,
        },
    )
    if tested.returncode:
        raise ValueError("focused held16 tests failed")
    module = collect.source_module()
    environment = study.environment("held")
    tasks = sum(1 for _ in environment.taskset)
    suite = study.dependencies()
    dependency = {
        "collector_source": str(Path(module.__file__)),
        "collector_run_callable": callable(getattr(module, "run", None)),
        "collector_trace_callable": callable(getattr(module, "inspect_trace", None)),
        "real_environment_tasks": tasks,
        "service_wrapper": str(Path(suite.SERVE).resolve()),
        "service_interfaces": {
            name: callable(getattr(suite, name, None))
            for name in ("start_service", "release_service", "command")
        },
    }
    if (
        not dependency["collector_run_callable"]
        or not dependency["collector_trace_callable"]
        or tasks != 16
        or not all(dependency["service_interfaces"].values())
    ):
        raise ValueError("actual held16 dependency boundary differs")
    paths = [
        *study.ROOT.glob("*.py"),
        study.ROOT / "DESIGN.md",
        study.ROOT / "RUNBOOK.md",
        study.ROOT / "CPU_TESTS.json",
        study.TRAINING / "CPU_READY_V2.json",
        study.TRAIN_INPUTS,
        study.SOURCE_EVAL / "CPU_READY.json",
        study.SOURCE_EVAL / "study.py",
        study.SOURCE_EVAL / "checkpoint.py",
        study.SOURCE_EVAL / "collect.py",
        study.SOURCE_EVAL / "owner.py",
    ]
    for name in ("tasks.json", "PUBLIC.json", "HOST_GOLD.json", "PREFIXES.json"):
        paths.append(study.input_dir("held") / name)
    paths.extend(sorted((study.input_dir("held") / "contexts").glob("*.json")))
    closure = dict(source_ready["closure_sha256"])
    training_ready = study.read(study.TRAINING / "CPU_READY_V2.json")
    for raw, expected in training_ready["closure_sha256"].items():
        if raw in closure and closure[raw] != expected:
            raise ValueError("parent closures disagree: " + raw)
        closure[raw] = expected
    closure.update({str(path): study.sha(path) for path in paths})
    plan = owner.plan()
    ready = {
        "schema": "mrcr-token-tis-held16-three-arm-cpu-ready-v1",
        "status": "CPU_READY_CONDITIONAL_ON_TWO_INDEPENDENT_STEP1_BRANCHES",
        "created_epoch": time.time(),
        "training_ready_sha256": study.sha(study.TRAINING / "CPU_READY_V2.json"),
        "training_ready_identity": training_ready["identity"],
        "stage_argv": plan["stage_argv"],
        "stage_order": ["base", "lr1e-5", "lr1e-4"],
        "inputs": {
            "episodes_each": 16,
            "schedule_sha256": study.digest(study.schedule("held")),
            "source_held_ready_sha256": study.sha(study.SOURCE_EVAL / "CPU_READY.json"),
            "reused_exact_coordinates": True,
        },
        "checkpoint_gate": "both exact independent step1 branches + 10x relation",
        "checkpoint_selection": False,
        "sampling": {
            "temperature": 0.5,
            "max_tokens": 2048,
            "max_total_turns": 6,
            "retries": 0,
            "workers": 4,
        },
        "metrics": {
            "primary": "paired raw exact",
            "diagnostic": [
                "raw official similarity",
                "similarity>=0.90",
                "shaped reward",
                "availability",
                "native calls and tokens",
            ],
            "newline_or_output_repair": None,
        },
        "caps": {"science_each": 500, "owner_each": 650, "external_each": 700},
        "held_panel_prior_exposure": "procedural-SFT evaluation used these contexts separately",
        "gpu_calls_in_preparation": 0,
        "optimizer_steps_in_evaluator": 0,
        "dependency_qualification": dependency,
        "focused_tests": tested.stdout.strip(),
        "closure_sha256": closure,
        "launch_authority": "MAIN only",
    }
    ready["identity"] = study.digest(ready)
    study.write_x(study.READY, ready)
    print(
        json.dumps(
            {
                "ready": str(study.READY),
                "sha256": study.sha(study.READY),
                "identity": ready["identity"],
                "tests": tested.stdout.strip(),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
