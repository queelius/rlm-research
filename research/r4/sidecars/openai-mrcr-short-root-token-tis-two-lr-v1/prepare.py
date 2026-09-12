"""Seal the fixed CPU-qualified token-TIS two-LR trainer."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "openai-mrcr-short-root-shaped-rl-v1"
MODEL_MANIFEST = Path(
    "/project/alex_phd/research-cache/models/"
    "Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554/"
    "local-research-manifest.json"
)
PYTHON = Path(
    "/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/"
    "gpu/training/.venv/bin/python"
)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(name):
    path = ROOT / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"token_tis_prepare_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    study = load("study")
    data = study.read(study.INPUTS)
    episodes = study.validate_inputs(data)
    if study.OUTPUT.exists():
        raise ValueError("attempt-001 output already exists")
    sources = [
        ROOT / "math_core.py",
        ROOT / "study.py",
        ROOT / "trainer.py",
        ROOT / "owner.py",
        ROOT / "prepare.py",
        ROOT / "test_token_tis.py",
        ROOT / "DESIGN.md",
        ROOT / "QUESTION.yaml",
        ROOT / "RUNBOOK.md",
        ROOT / "READY_SUPERSESSION.md",
        ROOT / "CPU_READY.json",
        study.INPUTS,
        study.SOURCE_READY,
        SOURCE / "trainer.py",
        SOURCE.parent / "mrcr-root-hf-one-update-preflight-v1/train.py",
        SOURCE.parent / "mrcr-root-hf-one-update-preflight-v1/math_core.py",
        MODEL_MANIFEST,
        PYTHON,
    ]
    closure = {str(path): sha(path) for path in sources}
    plan = {
        "schema": "mrcr-short-root-token-tis-two-lr-ready-v2",
        "status": "CPU_READY_TOKEN_TIS_TWO_LR_V2",
        "output": str(study.OUTPUT),
        "command": [
            str(study.PYTHON),
            str(ROOT / "owner.py"),
            "run",
            "--output",
            str(study.OUTPUT),
            "--cap-seconds",
            str(study.CAP_SECONDS),
        ],
        "cap_seconds": study.CAP_SECONDS,
        "external_cap_seconds": study.EXTERNAL_CAP_SECONDS,
        "episodes": len(episodes),
        "groups": len({row["group_id"] for row in episodes}),
        "root_turns": sum(len(row["root_turns"]) for row in episodes),
        "root_action_tokens": sum(
            len(turn["old_logprobs"]) for row in episodes for turn in row["root_turns"]
        ),
        "branches": [
            {"name": name, "learning_rate": rate, "optimizer_steps": 1}
            for name, rate in study.BRANCHES
        ],
        "same_initial_lora": True,
        "same_saved_clipped_gradient": True,
        "optimizer": "independent fresh AdamW per branch, weight_decay=0",
        "objective": "detached min(exp(HF-native),2) token-TIS sequence-SUM/24",
        "token_tis_cap": study.TOKEN_TIS_CAP,
        "self_normalized": False,
        "surrogate_unbiased": False,
        "full_trajectory_ess_is_gate": False,
        "finite_and_support_checks_are_gate": True,
        "pre_and_post_token_logprobs_persisted": True,
        "new_generation_calls": 0,
        "heldout_queries": 0,
        "selection": "both fixed branches retained; no best-checkpoint choice",
        "source_failed_trial_preserved": str(SOURCE / "outputs/attempt-001"),
        "source_failed_trial_result_sha256": sha(SOURCE / "outputs/attempt-001/RESULT.json"),
        "literature_scope": {
            "verl_rollout_correction_docs_commit": "10db40d0da4d59150bb389960b77585f81a89b8d",
            "token_tis_default_cap_from_docs": 2.0,
            "trust_region_masking_arxiv": "2512.23075",
            "interpretation": "token clipping is a biased surrogate, not sequence-level correction",
        },
        "closure_sha256": closure,
        "gpu_launched": False,
        "credentials_required": False,
    }
    canonical = json.dumps(plan, sort_keys=True, separators=(",", ":")).encode()
    plan["identity"] = hashlib.sha256(canonical).hexdigest()
    path = ROOT / "CPU_READY_V2.json"
    if path.exists():
        raise ValueError("CPU_READY already exists")
    study.write_x(path, plan)
    print(json.dumps({"path": str(path), "sha256": sha(path), "identity": plan["identity"]}))


if __name__ == "__main__":
    main()
