"""Thin binding to the exact original procedural-SFT evaluation inputs/runtime."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SIDE = ROOT.parent
SOURCE_EVAL = SIDE / "openai-mrcr-procedural-sft-eval-v1"
TRAINING = SIDE / "openai-mrcr-procedural-sft-continue32-v1"
TRAIN_OUTPUT = TRAINING / "outputs/attempt-001"
READY = ROOT / "CPU_READY.json"
ADAPTED_ALIAS = "Qwen3-4B-Instruct-2507-mrcr-procedural-sft-step32"


def _load_old():
    path = SOURCE_EVAL / "study.py"
    spec = importlib.util.spec_from_file_location("procedural_sft_continue32_eval_source", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


old = _load_old()
for _name in dir(old):
    if not _name.startswith("_") and _name not in {"ROOT", "READY", "TRAINING", "TRAIN_OUTPUT", "ADAPTED_ALIAS"}:
        globals()[_name] = getattr(old, _name)

# Deliberately delegate these functions rather than rebuilding coordinates. This preserves
# exact original task IDs, prefixes, source contexts, seeds, and runtime alias patches.
schedule = old.schedule
records = old.records
input_dir = old.input_dir
environment = old.environment
dependencies = old.dependencies
source = old.source
load = old.load
official_grade = old.official_grade

