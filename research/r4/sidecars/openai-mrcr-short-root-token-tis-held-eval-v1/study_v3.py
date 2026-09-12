"""Additive V3 binding for the repaired held16 evaluator."""

from pathlib import Path

import study_v2 as _base


for _name in dir(_base):
    if not _name.startswith("_"):
        globals()[_name] = getattr(_base, _name)

ROOT = Path(__file__).resolve().parent
READY = ROOT / "CPU_READY_V3.json"
load = _base.load
source = _base.source
