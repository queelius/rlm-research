"""Thin exact-held16 facade for the fixed token-TIS branches."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
SOURCE_EVAL = SIDE / "openai-mrcr-short-root-shaped-eval-v1"
TRAINING = SIDE / "openai-mrcr-short-root-token-tis-two-lr-v1"
TRAIN_OUTPUT = TRAINING / "outputs/attempt-001"
TRAIN_INPUTS = SIDE / "openai-mrcr-short-root-shaped-rl-v1/TRAIN_INPUTS.json"
READY = ROOT / "CPU_READY.json"
OWNER_SECONDS = 650
SCIENCE_SECONDS = 500
BASE_ALIAS = "Qwen3-4B-Instruct-2507-token-tis-eval-zero"
BRANCH_ALIASES = {
    "lr1e-5": "Qwen3-4B-Instruct-2507-mrcr-token-tis-low-step1",
    "lr1e-4": "Qwen3-4B-Instruct-2507-mrcr-token-tis-high-step1",
}


def _load_old():
    path = SOURCE_EVAL / "study.py"
    spec = importlib.util.spec_from_file_location("token_tis_held_old_study", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


old = _load_old()
SOURCE = old.SOURCE
DATA = old.DATA
RENDER_SOURCE = old.RENDER_SOURCE
EVAL_SOURCE = old.EVAL_SOURCE
BASE = old.BASE
NATIVE = old.NATIVE
TRAIN_PYTHON = old.TRAIN_PYTHON
RUNTIME = old.RUNTIME
ROLE_SOURCE = old.ROLE_SOURCE
DUAL_SERVICE = old.DUAL_SERVICE
INPUTS = old.INPUTS

sha = old.sha
digest = old.digest
read = old.read
write_x = old.write_x
records = old.records
schedule = old.schedule
input_dir = old.input_dir
environment = old.environment
environment_config = old.environment_config
official_grade = old.official_grade
dependencies = old.dependencies


def verify_frozen_inputs():
    source_ready = read(SOURCE_EVAL / "CPU_READY.json")
    for raw, expected in source_ready["closure_sha256"].items():
        if sha(Path(raw)) != expected:
            raise ValueError("source held16 closure changed: " + raw)
    if len(schedule("held")) != 16:
        raise ValueError("held16 schedule changed")
    if sha(TRAIN_INPUTS) != "0ff08ed62bc99fd054693b0f383f42a42c10227f4bffc14d753d97448293ea2b":
        raise ValueError("token-TIS training inputs changed")
    return source_ready
