"""Load a fresh isolated graph of the sealed HF four-step implementation."""

import importlib.util
import sys

import study


def load():
    names = (
        "config",
        "core",
        "rng_receipts",
        "train_four",
        "runner",
        "train",
        "settings",
        "prepare",
        "policy",
        "grammar_client",
        "grammar_worker",
    )
    for name in names:
        sys.modules.pop(name, None)
    before = list(sys.path)
    try:
        sys.path.insert(0, str(study.REFERENCE))
        spec = importlib.util.spec_from_file_location(
            "other31_source_train_four", study.REFERENCE / "train_four.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path[:] = before
