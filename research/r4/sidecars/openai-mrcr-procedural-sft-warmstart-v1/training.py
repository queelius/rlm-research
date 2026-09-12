"""Fixed-dose contracts shared by the procedural SFT trainer and evaluator."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
BASE = Path(
    "/project/alex_phd/research-cache/models/"
    "Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554"
)
OLD_LEARNING = SIDE / "root-complete-demonstration-sft-v1/learning.py"
OLD_LEARNING_SHA256 = "28d090c9e4ee4b3a57e56b5deda2a1634bd31fb70473348a22b05c836c1f25aa"
REQUIRED_CHECKPOINT_FILES = (
    "adapter_model.safetensors",
    "adapter_config.json",
    "optimizer.pt",
    "rng.pt",
    "EVAL_BINDING.json",
    "state.json",
)


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def write_x(path: Path, value) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def learning():
    if sha(OLD_LEARNING) != OLD_LEARNING_SHA256:
        raise ValueError("reused causal SFT objective changed")
    spec = importlib.util.spec_from_file_location("procedural_sft_pinned_learning", OLD_LEARNING)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def recipe() -> dict:
    return {
        "schema": "openai-mrcr-procedural-sft-recipe-v1",
        "starting_policy": "Qwen3-4B-Instruct-2507-no-research-adapter",
        "adapter": {
            "type": "LoRA",
            "rank": 8,
            "alpha": 16,
            "dropout": 0.0,
            "bias": "none",
            "target_modules": [
                "q_proj",
                "k_proj",
                "v_proj",
                "o_proj",
                "gate_proj",
                "up_proj",
                "down_proj",
            ],
        },
        "optimizer": "fresh AdamW",
        "learning_rate": 1e-4,
        "weight_decay": 0.0,
        "clip_grad_norm": 1.0,
        "seed": 2026091401,
        "updates": 4,
        "examples_per_update": 32,
        "action_weight": 1.0,
        "terminal_weight": 0.1,
        "loss": "per-example token-mean CE, mean across all32; action and terminal separate",
        "selection": "fixed checkpoint-0004; no evaluation selection",
        "training_cap_seconds": 600,
    }


def validate_corpus(corpus: dict) -> dict:
    episodes = corpus.get("episodes")
    if corpus.get("schema") != "openai-mrcr-procedural-sft-teacher-corpus-v1":
        raise ValueError("unexpected teacher corpus schema")
    if not isinstance(episodes, list) or len(episodes) != 32:
        raise ValueError("all32 teacher episodes are required")
    if len({episode.get("episode_id") for episode in episodes}) != 32:
        raise ValueError("teacher episode IDs are not unique")
    action_tokens = 0
    terminal_tokens = 0
    maximum = 0
    for episode in episodes:
        turns = episode.get("turns")
        if not isinstance(turns, list) or [turn.get("kind") for turn in turns] != [
            "root_action",
            "terminal",
        ]:
            raise ValueError("each teacher requires one root action and one terminal target")
        for turn in turns:
            ids = turn.get("input_ids")
            prompt = turn.get("prompt_length")
            target = len(ids) - prompt if isinstance(ids, list) and isinstance(prompt, int) else -1
            if (
                target <= 0
                or len(ids) > 8192
                or ids[-1] != 151645
                or turn.get("target_tokens") != target
                or turn.get("labels") != [-100] * prompt + ids[prompt:]
                or turn.get("loss_mask") != [0] * prompt + [1] * target
            ):
                raise ValueError("invalid exact causal teacher boundary")
            maximum = max(maximum, len(ids))
            if turn["kind"] == "root_action":
                action_tokens += target
            else:
                terminal_tokens += target
    return {
        "episodes": 32,
        "root_action_target_tokens": action_tokens,
        "terminal_target_tokens": terminal_tokens,
        "maximum_sequence_tokens": maximum,
    }


def commit_checkpoint(checkpoint: Path, state: dict) -> dict:
    checkpoint = Path(checkpoint)
    state_path = checkpoint / "state.json"
    if not state_path.exists():
        write_x(state_path, state)
    elif json.loads(state_path.read_text()) != state:
        raise ValueError("checkpoint state differs")
    files = {}
    for name in REQUIRED_CHECKPOINT_FILES:
        path = checkpoint / name
        if not path.is_file():
            raise ValueError("checkpoint file missing: " + str(path))
        files[name] = sha(path)
    commit = {
        "schema": "openai-mrcr-procedural-sft-step-commit-v1",
        "step": state["step"],
        "optimizer_steps": state["optimizer_steps"],
        "files_sha256": files,
    }
    commit["identity"] = digest(commit)
    write_x(checkpoint / "STEP_COMMIT.json", commit)
    return commit


def result_for(output: Path) -> dict:
    output = Path(output)
    commits = []
    for step in range(1, 5):
        checkpoint = output / f"checkpoint-{step:04d}"
        path = checkpoint / "STEP_COMMIT.json"
        if not path.is_file():
            raise ValueError(f"checkpoint-{step:04d} is not committed")
        commit = json.loads(path.read_text())
        if commit.get("identity") != digest(
            {key: value for key, value in commit.items() if key != "identity"}
        ):
            raise ValueError(f"checkpoint-{step:04d} commit identity changed")
        if commit.get("step") != step or commit.get("optimizer_steps") != step:
            raise ValueError(f"checkpoint-{step:04d} step mismatch")
        for name, expected in commit.get("files_sha256", {}).items():
            if sha(checkpoint / name) != expected:
                raise ValueError(f"checkpoint-{step:04d} file changed: {name}")
        commits.append({"path": str(path), "sha256": sha(path), "identity": commit["identity"]})
    return {
        "schema": "openai-mrcr-procedural-sft-result-v1",
        "status": "COMPLETED_FOUR_UPDATES",
        "optimizer_steps": 4,
        "selection": recipe()["selection"],
        "primary_checkpoint": str(output / "checkpoint-0004"),
        "evaluation_binding": str(output / "checkpoint-0004/EVAL_BINDING.json"),
        "step_commits": commits,
    }
