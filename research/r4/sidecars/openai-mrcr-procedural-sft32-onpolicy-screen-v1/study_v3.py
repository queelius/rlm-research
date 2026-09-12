"""Additive V3 receipt binding; scientific inputs remain V1-identical."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("sft32_onpolicy_v2_study_for_v3", ROOT / "study_v2.py")
_source_module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(_source_module)
for name in dir(_source_module):
    if not name.startswith("_") and name != "READY":
        globals()[name] = getattr(_source_module, name)
READY = ROOT / "CPU_READY_V3.json"

