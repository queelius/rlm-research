import importlib.abc
import importlib.machinery
import importlib.util
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class HelperLoader(importlib.abc.Loader):
    def create_module(self, spec):
        return None

    def exec_module(self, module):
        module.PRIME_ENV = Path("/fixture-prime")
        module._port_free = lambda port: True
        module._environment = lambda: {"PATH": os.environ["PATH"], "LD_LIBRARY_PATH": ""}
        module._server_environment = lambda environment, rank: dict(environment)
        module._wait_endpoint_model = lambda endpoint, process, alias, timeout: None


def test_actual_wrapper_reaches_popen_without_gpu_work(tmp_path, monkeypatch):
    owner = load("owner")
    wrapper = load("service_wrapper")
    binding_path = tmp_path / "binding.json"
    owner.s.write(binding_path, owner.binding())
    calls = []

    class Process:
        pid = 424242

    monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: calls.append((args, kwargs)) or Process())
    original_spec = importlib.util.spec_from_file_location

    def fake_spec(name, location, *args, **kwargs):
        if name == "base_service_environment":
            return importlib.machinery.ModuleSpec(name, HelperLoader())
        return original_spec(name, location, *args, **kwargs)

    monkeypatch.setattr(importlib.util, "spec_from_file_location", fake_spec)
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "fixture-gpu")
    monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY", "fixture-key")
    monkeypatch.setattr(
        sys,
        "argv",
        [str(ROOT / "service_wrapper.py"), "--binding", str(binding_path), "--run-dir", str(tmp_path / "run")],
    )
    wrapper.main()
    assert len(calls) == 1
    assert calls[0][0][0][0] == "/fixture-prime/bin/inference"
    assert (tmp_path / "run/SERVER_READY.json").exists()

