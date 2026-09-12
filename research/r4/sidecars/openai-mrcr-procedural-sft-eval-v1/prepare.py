"""Seal conditional fixed-checkpoint train and heldout readouts; no GPU calls."""

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
        raise FileExistsError("evaluation CPU_READY_V2 already exists")
    if study.sha(study.READY_V1) != "4c13ad207ee16ee293fae224127e310b61c88c9f8eaf5fab3ae1f0ce5316a9fe":
        raise ValueError("preserved initial CPU_READY changed")
    for value in owner.STAGES.values():
        if value["output"].exists():
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
        study.ROOT / "CPU_TESTS_V2.json",
        {"argv": command, "returncode": tested.returncode, "stdout": tested.stdout, "stderr": tested.stderr},
    )
    if tested.returncode:
        raise ValueError("focused evaluator tests failed")
    suite = study.dependencies()
    hooks = collect.role_hooks()
    dependency = {
        "suite": str(Path(suite.__file__).resolve()),
        "service_wrapper": str(Path(suite.SERVE).resolve()),
        "service_interfaces": {
            name: callable(getattr(suite, name, None))
            for name in ("start_service", "release_service", "command")
        },
        "role_hooks": str(Path(hooks.__file__).resolve()),
        "role_route_callable": callable(getattr(hooks, "route_native", None)),
    }
    if not all(dependency["service_interfaces"].values()) or not dependency["role_route_callable"]:
        raise ValueError("actual dependency interface incomplete")
    paths = list(study.ROOT.glob("*.py")) + [
        study.ROOT / "DESIGN.md",
        study.ROOT / "CPU_TESTS_V2.json",
        study.ROOT / "TRAINING_ENVIRONMENT_V2.json",
        study.TRAINING / "READY_TRAINING.json",
        study.TRAINING / "TEACHER_CORPUS_V2.json",
        study.TRAINING / "training.py",
        study.DATA / "DATA_READY_V2.json",
        study.DATA / "MODEL_INPUTS_V2.json",
        study.DATA / "official_score.py",
        study.SOURCE / "READY_V2.json",
        study.SOURCE / "causal_map_v2.py",
        study.SOURCE / "classify_v2.py",
        study.ROLE_SOURCE,
        study.ROLE_SOURCE.parent / "credit_data.py",
        study.ROLE_SOURCE.parent.parent / "leaf-role-routing-v1/source/routing.py",
        study.DUAL_SERVICE,
        study.BASE / "local-research-manifest.json",
    ]
    for phase in ("train", "held"):
        directory = study.input_dir(phase)
        paths += [directory / name for name in ("tasks.json", "PUBLIC.json", "HOST_GOLD.json", "PREFIXES.json")]
        paths += sorted((directory / "contexts").glob("*.json"))
    closure = {}
    for parent_ready_path in (
        study.SOURCE / "READY_V2.json",
        study.TRAINING / "READY_TRAINING.json",
    ):
        for raw, expected in study.read(parent_ready_path)["closure_sha256"].items():
            if raw in closure and closure[raw] != expected:
                raise ValueError("parent closures disagree: " + raw)
            closure[raw] = expected
    closure.update({str(path): study.sha(path) for path in paths})
    closure[str(study.READY_V1)] = study.sha(study.READY_V1)
    stage_commands = {
        name: [
            str(study.NATIVE),
            str(study.ROOT / "owner.py"),
            "run",
            "--stage",
            name,
            "--output",
            str(value["output"]),
            "--outer-seconds",
            str(study.OWNER_SECONDS),
        ]
        for name, value in owner.STAGES.items()
    }
    ready = {
        "schema": "openai-mrcr-procedural-sft-evaluation-cpu-ready-v2",
        "status": "CPU_READY_CONDITIONAL_ON_COMPLETED_TRAINING_AND_TRAIN_GATE",
        "supersedes": {"path": str(study.READY_V1), "sha256": study.sha(study.READY_V1)},
        "created_epoch": time.time(),
        "training_ready_sha256": study.sha(study.TRAINING / "READY_TRAINING.json"),
        "training_ready_identity": study.read(study.TRAINING / "READY_TRAINING.json")["identity"],
        "inputs": inputs,
        "checkpoint_seal_argv": [
            str(study.TRAIN_PYTHON),
            str(study.ROOT / "seal_checkpoint.py"),
        ],
        "stage_argv": stage_commands,
        "stage_order": ["train", "held-base", "held-checkpoint4"],
        "held_gate": {
            "all32_train_available": True,
            "raw_exact_at_least": 8,
            "distinct_exact_contexts_at_least": 4,
            "no_intermediate_checkpoint_selection": True,
        },
        "held_pairing": "same all16 x2 coordinates and seeds; base then checkpoint4",
        "policy": {
            "base": "released weights through authenticated all-zero LoRA transport",
            "checkpoint4": "fixed procedural root adapter",
            "child_both_arms": "released weights through same authenticated all-zero LoRA",
        },
        "sampling": {"temperature": 0.5, "max_tokens": 2048, "retries": 0, "workers": 4},
        "caps": {"science_each": 600, "owner_each": 900, "external_each": 1000},
        "heldout_used_in_training": False,
        "heldout_model_queries_in_preparation": 0,
        "optimizer_steps_in_evaluator": 0,
        "gpu_calls_in_preparation": 0,
        "dependency_qualification": dependency,
        "environment_receipt_sha256": study.sha(study.ROOT / "TRAINING_ENVIRONMENT_V2.json"),
        "focused_tests": tested.stdout.strip(),
        "closure_sha256": closure,
        "launch_authority": "MAIN only under shared GPU flock",
    }
    ready["identity"] = study.digest(ready)
    study.write_x(study.READY, ready)
    print(json.dumps({"ready_sha256": study.sha(study.READY), "identity": ready["identity"], "tests": tested.stdout.strip()}, sort_keys=True))


if __name__ == "__main__":
    main()
