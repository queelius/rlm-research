"""Exact checkpoint32 authentication reused without relaxing its lineage checks."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import study


SOURCE = study.CHECKPOINT_EVAL / "checkpoint.py"
eval_study_spec = importlib.util.spec_from_file_location(
    "sft32_onpolicy_checkpoint_eval_study", study.CHECKPOINT_EVAL / "study.py"
)
eval_study = importlib.util.module_from_spec(eval_study_spec)
assert eval_study_spec.loader is not None
eval_study_spec.loader.exec_module(eval_study)
previous = sys.modules.get("study")
sys.modules["study"] = eval_study
try:
    spec = importlib.util.spec_from_file_location("sft32_onpolicy_checkpoint_source", SOURCE)
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
