"""Seal one of two fixed credit assignments after the shared rollout batch qualifies."""

from datetime import datetime, timezone
import importlib.metadata
import inspect
import json
from pathlib import Path
import subprocess
import sys


def prepare(study):
    assert study.CREDIT_MODE in ("local", "joint")
    assert not study.READY.exists() and not study.OUTPUT.exists()
    data = study.read(study.INPUTS); rows = study.validate_inputs(data)
    qualification = study.read(study.SHARED / "DATA_QUALIFICATION.json")
    assert qualification["train_inputs_sha256"] == study.sha(study.INPUTS)
    assert qualification["episodes"] == 64 and qualification["groups"] == 16
    gate = qualification["sufficient_observed_contrast_gate"]
    assert qualification["active_local_groups"] >= gate["active_groups_min"]
    assert qualification["credit_modes_differ_groups"] >= gate["differing_groups_min"]
    assert qualification["full_valid_variable_groups"] >= gate["full_valid_variable_groups_min"]
    rollout_ready = study.read(study.ROLLOUT / "CPU_READY.json")
    closure = dict(rollout_ready["closure_sha256"])
    closure.update(study.read(study.FLAT / "READY.json")["closure_sha256"])
    paths = list(study.ROOT.glob("*.py")) + list(study.ROOT.glob("*.md"))
    paths += list(study.SHARED.glob("*.py")) + [study.INPUTS,
        study.SHARED / "DATA_QUALIFICATION.json", study.ROLLOUT / "CPU_READY.json",
        study.ROLLOUT / "outputs/attempt-001/OWNER_TERMINAL.json",
        study.ROLLOUT / "outputs/attempt-001/RESULT.json", study.FLAT / "READY.json",
        study.CONFIG_SOURCE, study.PYTHON, study.PYTHON.parent.parent / "pyvenv.cfg"]
    import peft.mapping_func, peft.tuners.lora.layer, torch.optim.adamw, torch.utils.checkpoint
    import transformers.models.qwen3.modeling_qwen3
    for module in (peft.mapping_func, peft.tuners.lora.layer, torch.optim.AdamW,
                   torch.utils.checkpoint, transformers.models.qwen3.modeling_qwen3):
        paths.append(Path(inspect.getfile(module)))
    for path in paths: closure[str(path)] = study.sha(path)
    closure.update(data["source_pins"])
    for path, expected in closure.items(): assert study.sha(path) == expected, path
    active = sum(any(any(coeff[j] * row[study.CREDIT_MODE + "_advantages"][j] != 0
                         for j in range(row["candidate_count"]))
                     for coeff in row["credit_coefficients"]) for row in rows)
    invalid = sum(not row["semantic_valid"] for row in rows)
    ready = {"schema": "b05-vector-credit-ready-v1",
        "status": "CPU_READY_MAIN_REVIEW_NOT_GPU_ADMITTED", "created_utc": datetime.now(timezone.utc).isoformat(),
        "credit_mode": study.CREDIT_MODE, "reward": study.REWARD_DESCRIPTION,
        "only_between_arm_difference": "candidate-local versus response-joint advantage assignment",
        "shared_input_sha256": study.sha(study.INPUTS), "same64_native_actions": True,
        "start": "released base; fresh seeded zero-B LoRA config only", "no_prior_adapter_loaded": True,
        "init_seed": study.INIT_SEED, "training_seed": study.SEED, "numpy_seed": study.NP_SEED,
        "learning_rate": 1e-4, "optimizer_steps": 1, "groups": 16, "group_size": 4,
        "denominator": 64, "per_candidate_weight": "1/candidate_count",
        "active_gradient_actions": active, "invalid_actions_zero_mask": invalid,
        "invalid_reward_policy": "zero candidate/response reward; retained /64 and enters peer RLOO baseline",
        "token_mask": "native boolean overlap only; punctuation/EOS zero; cross-decision tokens zero",
        "boundary_overlap_policy": "whole single-decision native token weight1; inseparable comma/space explicit; no retokenization",
        "token_TIS_cap": 2.0, "token_TIS_biased": True, "sequence_IS_unbiased": False,
        "gradient_clip": 1.0, "KL": None, "fresh_AdamW": True, "weight_decay": 0.0,
        "science_seconds": 900, "owner_seconds": 1000, "external_seconds": 1100,
        "output": str(study.OUTPUT), "expected_checkpoint": str(study.OUTPUT / "checkpoint-0001"),
        "argv": [str(study.PYTHON), str(study.ROOT / "owner.py"), "run"],
        "launch_authority": "MAIN only", "optimizer_blocked_until_MAIN_admission": True,
        "no_best_checkpoint_or_accuracy_selection": True, "held_queries": 0,
        "packages": {name: importlib.metadata.version(name) for name in
                     ("torch", "transformers", "peft", "safetensors")},
        "python": sys.version, "closure_sha256": dict(sorted(closure.items()))}
    ready["identity"] = study.digest(ready); study.write_x(study.READY, ready)
    command = [str(study.PYTHON), "-m", "pytest", "-q", "-p", "no:cacheprovider",
               str(study.SHARED / "test_credit.py"), str(study.ROOT / "test_arm.py")]
    result = subprocess.run(command, cwd=study.ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    receipt = {"schema": "b05-vector-credit-entry-proof-v1", "credit_mode": study.CREDIT_MODE,
        "command": command, "returncode": result.returncode, "stdout": result.stdout,
        "stderr": result.stderr, "actual_train_preflight_unmocked": True,
        "actual_GPU_guard_reached": True, "output_absent": not study.OUTPUT.exists(),
        "ready_sha256": study.sha(study.READY), "identity": ready["identity"],
        "closure_files": len(closure), "GPU_calls": 0, "model_calls": 0}
    assert receipt["output_absent"]
    study.write_x(study.ROOT / "ENTRY_PROOF.json", receipt)
    print(json.dumps(receipt, indent=2))
