"""V3 binding to the unchanged authenticated checkpoint32 receipt."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import study_v3 as study


ROOT = Path(__file__).resolve().parent
previous = sys.modules.get("study")
sys.modules["study"] = study
try:
    spec = importlib.util.spec_from_file_location("sft32_onpolicy_v1_checkpoint_for_v3", ROOT / "checkpoint.py")
    source = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(source)
finally:
    if previous is None:
        sys.modules.pop("study", None)
    else:
        sys.modules["study"] = previous
RECEIPT = source.RECEIPT
verify_checkpoint = source.verify_checkpoint
binding = source.binding

