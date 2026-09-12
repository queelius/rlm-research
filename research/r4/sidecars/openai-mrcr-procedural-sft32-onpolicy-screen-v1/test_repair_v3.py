from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(f"g4_repair_test_{name}", ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_all_executable_collector_layers_use_v3_verifier():
    study = load("study_v3")
    old = {name: sys.modules.get(name) for name in ("study", "checkpoint")}
    sys.modules["study"] = study
    sys.modules["checkpoint"] = load("checkpoint_v3")
    try:
        collect = load("collect_v3")
    finally:
        for name, value in old.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value
    expected = collect.verify_ready()
    assert collect.source.verify_ready() == expected
    assert collect.source.source.verify_ready() == expected
    assert collect.source.run.__globals__["source"].run.__globals__["verify_ready"]() == expected


def test_v3_owner_actual_verify_and_attempt003():
    owner = load("owner_v3")
    assert owner.verify()["schema"].endswith("ready-v3")
    assert owner.OUTPUT == owner.study.ROOT / "outputs/attempt-003"
    assert owner.COLLECTOR.name == "collect_v3.py"
