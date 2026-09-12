"""Immutable inputs and contracts for the MRCR token-TIS two-dose probe."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "openai-mrcr-short-root-shaped-rl-v1"
INPUTS = SOURCE / "TRAIN_INPUTS.json"
SOURCE_READY = SOURCE / "RUN_READY.json"
CPU_READY = ROOT / "CPU_READY_V2.json"
OUTPUT = ROOT / "outputs/attempt-001"
BASE = Path(
    "/project/alex_phd/research-cache/models/"
    "Qwen--Qwen3-4B-Instruct-2507--cdbee75f17c01a7cc42f958dc650907174af0554"
)
PYTHON = Path(
    "/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/"
    "gpu/training/.venv/bin/python"
)
CAP_SECONDS = 900
EXTERNAL_CAP_SECONDS = 1000
SEED = 202609131900
NP_SEED = SEED % (2**32)
TEMPERATURE = 0.5
TOKEN_TIS_CAP = 2.0
DENOMINATOR = 24
BRANCHES = (("lr1e-5", 1e-5), ("lr1e-4", 1e-4))
INPUT_SHA256 = "0ff08ed62bc99fd054693b0f383f42a42c10227f4bffc14d753d97448293ea2b"
SOURCE_READY_SHA256 = "0ff060b68b78753b3d44c7acc239955efb3b6c77f5c202cb16d5e59c06c8e1e5"


def sha(path: Path | str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path: Path | str):
    return json.loads(Path(path).read_text())


def write_x(path: Path | str, value) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def positions_and_targets(turn: dict) -> tuple[list[int], list[int]]:
    prompt = turn.get("prompt_ids")
    action = turn.get("action_ids")
    old = turn.get("old_logprobs")
    if not isinstance(prompt, list) or not prompt or not isinstance(action, list) or not action:
        raise ValueError("root prompt/action must be nonempty token lists")
    if not isinstance(old, list) or len(old) != len(action):
        raise ValueError("native logprobs do not cover exact action suffix")
    if any(not math.isfinite(float(value)) or float(value) > 0 for value in old):
        raise ValueError("native token logprobs must be finite nonpositive")
    full = prompt + action
    if turn.get("input_ids") != full:
        raise ValueError("physical causal input differs")
    if turn.get("labels") != [-100] * len(prompt) + action:
        raise ValueError("root prefix mask differs")
    if turn.get("loss_mask") != [0] * len(prompt) + [1] * len(action):
        raise ValueError("root loss mask differs")
    return list(range(len(prompt) - 1, len(full) - 1)), action


def validate_inputs(data: dict) -> list[dict]:
    episodes = data.get("episodes") or []
    if data.get("schema") != "mrcr-short-shaped-root-hf-training-inputs-v1":
        raise ValueError("shaped24 schema differs")
    if len(episodes) != 24 or len({row.get("group_id") for row in episodes}) != 6:
        raise ValueError("exact 24 episodes / six G4 groups required")
    if any(sum(row.get("group_id") == other.get("group_id") for other in episodes) != 4 for row in episodes):
        raise ValueError("groups are not exact G4")
    for row in episodes:
        if row.get("reward") not in (0.0, 0.5, 1.0):
            raise ValueError("frozen shaped reward differs")
        if not math.isfinite(float(row.get("advantage"))):
            raise ValueError("nonfinite frozen advantage")
        turns = row.get("root_turns") or []
        if not turns:
            raise ValueError("episode has no root action")
        for turn in turns:
            positions_and_targets(turn)
            if turn.get("depth") != 0 or turn.get("credited") is not True:
                raise ValueError("non-root action entered root loss")
        for child in row.get("fixed_child_turns") or []:
            if child.get("depth", 0) <= 0 or child.get("credited") is not False:
                raise ValueError("fixed-child audit differs")
            if child.get("loss_tokens") != 0:
                raise ValueError("fixed child received loss")
        if row.get("all_native_calls_exactly_matched") is not True:
            raise ValueError("native physical linkage differs")
    if sum(len(row["root_turns"]) for row in episodes) != 74:
        raise ValueError("exact 74 root turns required")
    if sum(len(turn["old_logprobs"]) for row in episodes for turn in row["root_turns"]) != 15602:
        raise ValueError("exact 15602 root action tokens required")
    return episodes


def load_sealed_inputs():
    if sha(INPUTS) != INPUT_SHA256 or sha(SOURCE_READY) != SOURCE_READY_SHA256:
        raise ValueError("source shaped24 inputs changed")
    ready = read(CPU_READY)
    if ready.get("status") != "CPU_READY_TOKEN_TIS_TWO_LR_V2":
        raise ValueError("CPU_READY does not authorize this probe")
    for path, expected in ready.get("closure_sha256", {}).items():
        if sha(path) != expected:
            raise ValueError("sealed closure changed: " + path)
    data = read(INPUTS)
    return ready, data, validate_inputs(data)
