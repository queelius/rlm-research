"""Frozen total32 continuation; all training inputs remain the original teacher corpus."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

from resume import file_sha


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "openai-mrcr-procedural-sft-warmstart-v1"
PARENT = SOURCE / "outputs/attempt-001/checkpoint-0004"
CORPUS = SOURCE / "TEACHER_CORPUS_V2.json"
READY = ROOT / "READY_TRAINING.json"
OUTPUT = ROOT / "outputs/attempt-001"
PYTHON = Path("/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python")
FIRST_STEP = 5
LAST_STEP = 32
OWNER_SECONDS = 1500
EXTERNAL_SECONDS = 1600
PARENT_COMMIT_SHA = "50f3767f4a9d2622991bbdf96b9885620c422f84abe16c9e4e6e397c7427bd24"
CORPUS_SHA = "e4f5a2e71a435cebb732f13ad551f74edca1b784920b80230fb5ae282e1ecf56"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


training = load("continue32_original_training", SOURCE / "training.py")
previous = sys.modules.get("training")
sys.modules["training"] = training
try:
    original_train = load("continue32_original_train", SOURCE / "train.py")
finally:
    if previous is None:
        sys.modules.pop("training", None)
    else:
        sys.modules["training"] = previous

BASE = training.BASE
BASE_MANIFEST = BASE / "local-research-manifest.json"
sha = file_sha
digest = training.digest
write_x = training.write_x


def read(path: Path):
    return json.loads(Path(path).read_text())


def recipe() -> dict:
    return {
        **training.recipe(),
        "schema": "openai-mrcr-procedural-sft-continue32-recipe-v1",
        "starting_policy": str(PARENT),
        "optimizer": "restored checkpoint4 AdamW including moments and step counters",
        "updates": LAST_STEP,
        "additional_updates": LAST_STEP - FIRST_STEP + 1,
        "first_optimizer_step": FIRST_STEP,
        "training_cap_seconds": OWNER_SECONDS,
        "selection": "fixed checkpoint-0032; no evaluation selection",
        "checkpoint_every_updates": 1,
    }


def authenticate_parent() -> dict:
    if sha(PARENT / "STEP_COMMIT.json") != PARENT_COMMIT_SHA:
        raise ValueError("immutable checkpoint4 commit changed")
    commit = read(PARENT / "STEP_COMMIT.json")
    if commit["identity"] != digest({key: value for key, value in commit.items() if key != "identity"}):
        raise ValueError("checkpoint4 commit identity differs")
    if set(commit["files_sha256"]) != set(training.REQUIRED_CHECKPOINT_FILES):
        raise ValueError("checkpoint4 file inventory differs")
    for name, expected in commit["files_sha256"].items():
        if sha(PARENT / name) != expected:
            raise ValueError("checkpoint4 file changed: " + name)
    state = read(PARENT / "state.json")
    if state["step"] != 4 or state["optimizer_steps"] != 4 or state["corpus_sha256"] != CORPUS_SHA:
        raise ValueError("checkpoint4 training lineage differs")
    if sha(CORPUS) != CORPUS_SHA:
        raise ValueError("teacher corpus changed")
    return {"checkpoint": str(PARENT), "step_commit_sha256": PARENT_COMMIT_SHA, "state": state}


def verify() -> dict:
    ready = read(READY)
    if ready["identity"] != digest({key: value for key, value in ready.items() if key != "identity"}):
        raise ValueError("continuation READY identity differs")
    for raw, expected in ready["closure_sha256"].items():
        if sha(Path(raw)) != expected:
            raise ValueError("continuation source/input changed: " + raw)
    if ready["recipe"] != recipe() or training.validate_corpus(read(CORPUS)) != ready["corpus"]:
        raise ValueError("continuation recipe/corpus contract differs")
    return ready


def plan() -> dict:
    return {
        "command": [str(PYTHON), str(ROOT / "train.py"), "run", "--output", str(OUTPUT), "--seconds", str(OWNER_SECONDS)],
        "owner_seconds": OWNER_SECONDS,
        "external_seconds": EXTERNAL_SECONDS,
        "first_step": FIRST_STEP,
        "last_step": LAST_STEP,
        "additional_optimizer_steps": LAST_STEP - FIRST_STEP + 1,
        "parent_checkpoint": str(PARENT),
        "output": str(OUTPUT),
        "gpu_authority": "MAIN",
    }
