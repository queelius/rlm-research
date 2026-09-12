"""Additive inherited-runtime contract repair for the fixed held16 evaluator."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE_PATH = ROOT / "study.py"


def _load_base():
    spec = importlib.util.spec_from_file_location("token_tis_held_v1_study_source", SOURCE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


base = _load_base()
for _name in dir(base):
    if not _name.startswith("_"):
        globals()[_name] = getattr(base, _name)

ROOT = Path(__file__).resolve().parent
READY = ROOT / "CPU_READY_V2.json"
load = base.old.load
source = base.old.source


def verify_frozen_inputs():
    value = base.verify_frozen_inputs()
    if not callable(load) or not callable(source) or not Path(source().RUNTIME_BIN).is_dir():
        raise ValueError("inherited collector load/source runtime contract differs")
    return value
