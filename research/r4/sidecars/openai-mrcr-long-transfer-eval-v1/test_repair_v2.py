from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import time


ROOT = Path(__file__).resolve().parent
RUNTIME_WRAPPER = ROOT.parent / "runtime-an22-5801-v1/service_wrapper_v2.py"


def load(name):
    spec = importlib.util.spec_from_file_location(f"long_repair_test_{name}", ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_dependencies_bind_actual_dual_lora_service_at_both_boundaries():
    study = load("study_v2")
    suite = study.dependencies()
    assert suite.SERVE == RUNTIME_WRAPPER
    assert suite.life.__dict__["ALLOCATION_SERVICE"] == RUNTIME_WRAPPER


def test_actual_start_service_emits_runtime_wrapper_for_both_bindings(tmp_path, monkeypatch):
    study = load("study_v2")
    checkpoint = load("checkpoint_v2")
    suite = study.dependencies()
    observed = []

    class Process:
        pid = 424242
        returncode = 0

        def __init__(self, command, **kwargs):
            observed.append({"command": command, "kwargs": kwargs})
            service = Path(command[command.index("--run-dir") + 1])
            service.mkdir(parents=True)
            (service / "SERVER_READY.json").write_text("{}")

        def poll(self):
            return 0

    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "cpu-fixture")
    monkeypatch.setattr(suite.life.v1, "ports_free", lambda: True)
    monkeypatch.setattr(suite.subprocess, "Popen", Process)
    monkeypatch.setattr(
        suite.life,
        "observe",
        lambda pid: {"pid": pid, "pgid": pid, "uid": os.getuid(), "start_ticks": 1, "cmdline": []},
    )
    monkeypatch.setattr(suite.life, "safe_observation", lambda value: value)
    monkeypatch.setattr(suite, "observe_service", lambda directory: None)
    monkeypatch.setattr(suite, "preflight", lambda service, binding: None)
    for arm in ("base", "checkpoint32"):
        directory = tmp_path / arm
        directory.mkdir()
        binding = checkpoint.binding(arm)
        suite.start_service(directory, binding, time.time() + 10)
        request = json.loads((directory / "SERVICE_REQUEST.json").read_text())
        assert Path(request["command"][1]) == RUNTIME_WRAPPER
        assert json.loads((directory / "BINDING.json").read_text()) == binding
    assert len(observed) == 2


def test_actual_owner_v2_verify_and_additive_outputs():
    owner = load("owner_v2")
    ready = owner.verify("base")
    assert ready["schema"] == "openai-mrcr-long-transfer-evaluation-ready-v2"
    assert owner.STAGES["base"]["output"].name == "base-002"
    assert owner.STAGES["checkpoint32"]["output"].name == "checkpoint32-002"
    assert owner.COLLECTOR.name == "collect_v2.py"
