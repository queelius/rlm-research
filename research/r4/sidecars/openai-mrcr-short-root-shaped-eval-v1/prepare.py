"""CPU-only seal for the conditional two-arm heldout evaluation."""

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
    if study.READY.exists():
        raise FileExistsError("evaluation READY already exists")
    if any(path.exists() for path in owner.STAGES.values()):
        raise FileExistsError("fixed evaluation output is not unused")
    inputs = study.prepare_inputs()
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
        {"argv": command, "returncode": tested.returncode, "stdout": tested.stdout, "stderr": tested.stderr},
    )
    if tested.returncode:
        raise ValueError("focused evaluator tests failed")
    module = collect.source_module()
    env = study.environment("held")
    task_count = sum(1 for _ in env.taskset)
    suite = study.dependencies()
    dependency = {
        "collector_source": str(Path(module.__file__)),
        "collector_run_callable": callable(getattr(module, "run", None)),
        "collector_inspect_trace_callable": callable(getattr(module, "inspect_trace", None)),
        "real_environment_tasks": task_count,
        "suite": str(Path(suite.__file__).resolve()),
        "service_wrapper": str(Path(suite.SERVE).resolve()),
        "service_interfaces": {
            name: callable(getattr(suite, name, None))
            for name in ("start_service", "release_service", "command")
        },
    }
    if (
        not dependency["collector_run_callable"]
        or not dependency["collector_inspect_trace_callable"]
        or dependency["real_environment_tasks"] != 16
        or not all(dependency["service_interfaces"].values())
    ):
        raise ValueError("actual evaluation dependency boundary incomplete")
    paths = list(study.ROOT.glob("*.py")) + [
        study.ROOT / "DESIGN.md",
        study.ROOT / "CPU_TESTS.json",
        study.TRAINING / "RUN_READY.json",
        study.TRAINING / "TRAIN_INPUTS.json",
        study.TRAINING / "DECISION_ADDENDUM.md",
        study.DATA / "DATA_READY_V2.json",
        study.DATA / "MODEL_INPUTS_V2.json",
        study.DATA / "official_score.py",
        study.SOURCE / "READY_V2.json",
        study.SOURCE / "causal_map_v2.py",
        study.SOURCE / "classify_v2.py",
        study.EVAL_SOURCE / "collect.py",
        study.EVAL_SOURCE / "study.py",
        study.RENDER_SOURCE / "teacher.py",
        study.ROLE_SOURCE,
        study.ROLE_SOURCE.parent / "credit_data.py",
        study.ROLE_SOURCE.parent.parent / "leaf-role-routing-v1/source/routing.py",
        study.DUAL_SERVICE,
        study.BASE / "local-research-manifest.json",
    ]
    directory = study.input_dir("held")
    paths += [directory / name for name in ("tasks.json", "PUBLIC.json", "HOST_GOLD.json", "PREFIXES.json")]
    paths += sorted((directory / "contexts").glob("*.json"))
    closure = {}
    for parent_ready_path in (study.SOURCE / "READY_V2.json", study.TRAINING / "RUN_READY.json"):
        for raw, expected in study.read(parent_ready_path)["closure_sha256"].items():
            if raw in closure and closure[raw] != expected:
                raise ValueError("parent closures disagree: " + raw)
            closure[raw] = expected
    closure.update({str(path): study.sha(path) for path in paths})
    stage_commands = {
        stage: [
            str(study.NATIVE),
            str(study.ROOT / "owner.py"),
            "run",
            "--stage",
            stage,
            "--output",
            str(output),
            "--outer-seconds",
            str(study.OWNER_SECONDS),
        ]
        for stage, output in owner.STAGES.items()
    }
    ready = {
        "schema": "openai-mrcr-shaped-root-heldout-evaluation-cpu-ready-v1",
        "status": "CPU_READY_CONDITIONAL_ON_EXACT_ONE_UPDATE",
        "created_epoch": time.time(),
        "training_ready_sha256": study.sha(study.TRAINING / "RUN_READY.json"),
        "training_ready_identity": study.read(study.TRAINING / "RUN_READY.json")["identity"],
        "inputs": inputs,
        "checkpoint_seal": "automatic inside first arm owner after exact UPDATED result",
        "stage_argv": stage_commands,
        "stage_order": ["base", "updated"],
        "pairing": "same all16 held coordinates and fresh seeds; one rollout per arm",
        "policy": {
            "base": "released weights through authenticated all-zero LoRA transport",
            "updated": "fixed shaped-root checkpoint-0001",
            "child_both_arms": "released weights through same authenticated all-zero LoRA",
        },
        "sampling": {"temperature": 0.5, "max_tokens": 2048, "max_total_turns": 6, "retries": 0, "workers": 4},
        "metrics": {
            "primary": "paired raw exact",
            "diagnostic": ["raw official similarity", "raw similarity>=0.90", "shaped reward"],
            "newline_or_output_repair": None,
        },
        "positive_screen": {"updated_only_raw_exact_wins_at_least": 2, "raw_exact_losses": 0, "all32_available_authentic": True},
        "weak_result_scope": "retires only fixed LR1e-5 checkpoint as positive endpoint",
        "postupdate_likelihood_shift_measured": False,
        "caps": {"science_each": study.SCIENCE_SECONDS, "owner_each": study.OWNER_SECONDS, "external_each": 700},
        "heldout_used_in_training": False,
        "heldout_model_queries_in_preparation": 0,
        "optimizer_steps_in_evaluator": 0,
        "gpu_calls_in_preparation": 0,
        "dependency_qualification": dependency,
        "focused_tests": tested.stdout.strip(),
        "closure_sha256": closure,
        "launch_authority": "MAIN only under shared GPU flock",
    }
    ready["identity"] = study.digest(ready)
    study.write_x(study.READY, ready)
    print(json.dumps({"ready_sha256": study.sha(study.READY), "identity": ready["identity"], "tests": tested.stdout.strip()}, sort_keys=True))


if __name__ == "__main__":
    main()
