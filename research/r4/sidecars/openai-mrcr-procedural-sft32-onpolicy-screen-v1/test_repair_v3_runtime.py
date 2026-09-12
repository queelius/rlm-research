from __future__ import annotations

import asyncio
import importlib.util
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(f"g4_runtime_test_{name}", ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_actual_run_crosses_inner_verify_before_cpu_sentinel(tmp_path, monkeypatch):
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
    endpoint = tmp_path / "endpoint.json"
    endpoint.write_text(json.dumps({"cpu": "sentinel"}))

    class ReachedAfterVerify(Exception):
        pass

    inner = collect.source.source

    def binding(arm):
        assert arm == "checkpoint32"
        raise ReachedAfterVerify

    monkeypatch.setattr(inner.checkpoint, "binding", binding)
    with pytest.raises(ReachedAfterVerify):
        asyncio.run(collect.run("train", "checkpoint32", endpoint, tmp_path / "unused", 10**10))
