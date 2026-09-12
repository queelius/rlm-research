"""Use the already authenticated base-zero and checkpoint32 bindings."""

from __future__ import annotations

import importlib.util
import sys

import study


def _source_modules():
    source_study_path = study.CHECKPOINT_EVAL / "study.py"
    spec = importlib.util.spec_from_file_location("mrcr_long_checkpoint_source_study", source_study_path)
    source_study = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(source_study)
    previous = sys.modules.get("study")
    sys.modules["study"] = source_study
    try:
        path = study.CHECKPOINT_EVAL / "checkpoint.py"
        spec = importlib.util.spec_from_file_location("mrcr_long_checkpoint_source", path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
    finally:
        if previous is None:
            sys.modules.pop("study", None)
        else:
            sys.modules["study"] = previous
    return source_study, module


source_study, source = _source_modules()
RECEIPT = source.RECEIPT


def verify_checkpoint():
    return source.verify_checkpoint()


def binding(arm: str):
    value = source.binding(arm)
    if value["role_map"]["root"] != (study.BASE_ALIAS if arm == "base" else study.ADAPTED_ALIAS):
        raise ValueError("checkpoint source aliases changed")
    return value
