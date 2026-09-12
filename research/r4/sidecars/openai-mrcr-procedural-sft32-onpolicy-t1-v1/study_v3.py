"""Additive attempt-003 binding for the T1 role-audit repair."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("mrcr_t1_v2_study_for_v3", ROOT / "study_v2.py")
_source = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_source)
for _name in dir(_source):
    if not _name.startswith("_") and _name != "READY":
        globals()[_name] = getattr(_source, _name)

READY = ROOT / "READY_V3.json"

