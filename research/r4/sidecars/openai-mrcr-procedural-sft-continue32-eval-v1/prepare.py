"""CPU-only seal for the fixed checkpoint32 train/held readout."""

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
    if study.READY.exists() or any(value["output"].exists() for value in owner.STAGES.values()):
        raise FileExistsError("READY or fixed output already exists")
    training_ready_path = study.TRAINING / "READY_TRAINING.json"
    training_ready = study.read(training_ready_path)
    source_ready_path = study.SOURCE_EVAL / "CPU_READY_V2.json"
    source_ready = study.read(source_ready_path)
    if study.schedule("train") != study.old.schedule("train") or study.schedule("held") != study.old.schedule("held"):
        raise ValueError("delegated original schedules differ")
    command = [str(study.NATIVE), "-m", "pytest", "-q", "test_eval.py"]
    tested = subprocess.run(command, cwd=study.ROOT,
        env={**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True, text=True, timeout=120, check=False)
    study.write_x(study.ROOT / "CPU_TESTS.json",
                  {"argv": command, "returncode": tested.returncode,
                   "stdout": tested.stdout, "stderr": tested.stderr})
    if tested.returncode:
        raise ValueError("focused continuation evaluator tests failed")
    suite = study.dependencies()
    hooks = collect.role_hooks()
    dependency = {
        "suite": str(Path(suite.__file__).resolve()),
        "service_wrapper": str(Path(suite.SERVE).resolve()),
        "service_interfaces": {name: callable(getattr(suite, name, None))
                               for name in ("start_service", "release_service", "command")},
        "role_hooks": str(Path(hooks.__file__).resolve()),
        "installed_hooks_callable": callable(getattr(hooks, "installed_hooks", None)),
        "runtime_bin": str(study.source().RUNTIME_BIN),
    }
    if not all(dependency["service_interfaces"].values()) or not dependency["installed_hooks_callable"]:
        raise ValueError("actual inherited dependency interface differs")
    paths = list(study.ROOT.glob("*.py")) + [study.ROOT / "DESIGN.md", study.ROOT / "RUNBOOK.md",
        study.ROOT / "CPU_TESTS.json", source_ready_path,
        study.SOURCE_EVAL / "study.py", study.SOURCE_EVAL / "checkpoint.py",
        study.SOURCE_EVAL / "collect.py", study.SOURCE_EVAL / "owner.py", training_ready_path]
    closure = {}
    for parent in (source_ready, training_ready):
        for raw, expected in parent["closure_sha256"].items():
            if raw in closure and closure[raw] != expected:
                raise ValueError("parent closures disagree: " + raw)
            closure[raw] = expected
    closure.update({str(path): study.sha(path) for path in paths})
    stage_argv = {
        name: [str(study.NATIVE), str(study.ROOT / "owner.py"), "run", "--stage", name,
               "--output", str(value["output"]), "--outer-seconds", str(study.OWNER_SECONDS)]
        for name, value in owner.STAGES.items()
    }
    ready = {
        "schema": "openai-mrcr-procedural-sft-continue32-evaluation-cpu-ready-v1",
        "status": "CPU_READY_CONDITIONAL_ON_COMMITTED_CHECKPOINT32_AND_TRAIN32_GATE",
        "created_epoch": time.time(),
        "training_ready_sha256": study.sha(training_ready_path),
        "training_ready_identity": training_ready["identity"],
        "source_evaluator_ready_sha256": study.sha(source_ready_path),
        "checkpoint_seal_argv": [str(study.TRAIN_PYTHON), str(study.ROOT / "seal_checkpoint.py")],
        "stage_argv": stage_argv,
        "stage_order": ["train32", "held-base", "held-checkpoint32"],
        "inputs": {
            "train": {"episodes": 32, "schedule_sha256": study.digest(study.schedule("train"))},
            "held": {"episodes": 32, "records": 16,
                     "schedule_sha256": study.digest(study.schedule("held"))},
        },
        "exact_coordinate_reuse": {"train": True, "held": True,
                                   "source": str(study.SOURCE_EVAL / "inputs")},
        "checkpoint": {"fixed_step": 32, "additional_updates": 28,
                       "resume_parent_step": 4, "selection": False,
                       "adam_and_rng_continuation_required": True},
        "held_gate": {"all32_train_available": True, "raw_exact_at_least": 8,
                      "distinct_exact_contexts_at_least": 4,
                      "no_intermediate_checkpoint_selection": True},
        "held_pairing": "same original held16 x2 coordinates/seeds; base then checkpoint32",
        "sampling": {"temperature": 0.5, "max_tokens": 2048, "max_total_turns": 6,
                     "retries": 0, "workers": 4},
        "caps": {"science_each": 600, "owner_each": 900, "external_each": 1000},
        "held_panel_prior_exposure": "same panel declared for checkpoint4 procedural-SFT evaluation; no checkpoint4 held calls occurred",
        "heldout_model_queries_in_preparation": 0,
        "optimizer_steps_in_evaluator": 0,
        "dependency_qualification": dependency,
        "focused_tests": tested.stdout.strip(),
        "closure_sha256": closure,
        "launch_authority": "MAIN only under shared GPU flock",
    }
    ready["identity"] = study.digest(ready)
    study.write_x(study.READY, ready)
    print(json.dumps({"ready": str(study.READY), "sha256": study.sha(study.READY),
                      "identity": ready["identity"], "tests": tested.stdout.strip()}, sort_keys=True))


if __name__ == "__main__":
    main()

