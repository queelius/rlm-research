from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent


def load(name: str):
    path = ROOT / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"g4_repair_test_{name}", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_actual_fresh_collector_verify_accepts_flat_v2_receipt() -> None:
    study = load("study_v2")
    previous = {name: sys.modules.get(name) for name in ("study", "checkpoint")}
    sys.modules["study"] = study
    sys.modules["checkpoint"] = load("checkpoint_v2")
    try:
        collect = load("collect_v2")
    finally:
        for name, value in previous.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value
    ready = collect.verify_ready()
    assert ready["schema"] == "openai-mrcr-procedural-sft32-onpolicy-screen-ready-v2"
    assert ready["inputs"]["schedule_sha256"] == study.digest(study.schedule("train"))
    assert collect.source.verify_ready() == ready


def test_actual_fresh_owner_verify_and_attempt002_binding() -> None:
    owner = load("owner_v2")
    ready = owner.verify()
    assert ready["identity"] == owner.study.read(owner.study.READY)["identity"]
    assert owner.OUTPUT == owner.study.ROOT / "outputs/attempt-002"
    assert owner.COLLECTOR == owner.study.ROOT / "collect_v2.py"
