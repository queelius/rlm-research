"""Reuse the already-qualified immutable base/low/high checkpoint receipt."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import study


def _load_qualified():
    path = study.QUALIFIED / "checkpoint_v4.py"
    names = ("study_v4", "study_v3", "study_v2", "study", "checkpoint")
    previous = {name: sys.modules.get(name) for name in names}
    old_path = list(sys.path)
    sys.path.insert(0, str(study.QUALIFIED))
    for name in names:
        sys.modules.pop(name, None)
    try:
        spec = importlib.util.spec_from_file_location("token_tis_seed2_qualified_checkpoint", path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path[:] = old_path
        for name, value in previous.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value


qualified = _load_qualified()
ARTIFACTS = qualified.ARTIFACTS
ZERO = qualified.ZERO
RECEIPT = qualified.RECEIPT
verify_checkpoint = qualified.verify_checkpoint
ensure_checkpoint = qualified.ensure_checkpoint
binding = qualified.binding
