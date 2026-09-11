import json
import importlib.machinery
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def test_full_service_entry_uses_qualified_service_through_prelaunch(tmp_path, monkeypatch):
    import service_wrapper_v5 as wrapper
    import study as s

    binding = {"schema": "released-base-single-model-binding-v1", "model": "qwen3",
               "checkpoint": s.MODEL, "weights_sha256": s.sha(ROOT / "WEIGHTS.json"),
               "adapter": None}
    binding_path = tmp_path / "BINDING.json"
    binding_path.write_text(json.dumps(binding))
    run_dir = tmp_path / "service"
    observed = {}

    class Loader:
        def create_module(self, spec):
            return None

        def exec_module(self, module):
            module.PRIME_ENV = Path("/fixture/prime")
            module._port_free = lambda port: True
            module._environment = lambda: {"PATH": "/usr/bin", "LD_LIBRARY_PATH": ""}
            module._server_environment = lambda environment, replica: dict(environment)
            module._wait_endpoint_model = lambda endpoint, process, alias, timeout: observed.update(
                endpoint=endpoint, alias=alias, timeout=timeout)

    original_spec = wrapper.importlib.util.spec_from_file_location
    monkeypatch.setattr(wrapper.importlib.util, "spec_from_file_location",
        lambda name, path: importlib.machinery.ModuleSpec(name, Loader())
        if name == "base_service_environment" else original_spec(name, path))

    class Process:
        pid = 424242

    monkeypatch.setattr(wrapper.subprocess, "Popen",
                        lambda command, **kwargs: observed.update(command=command, kwargs=kwargs) or Process())
    monkeypatch.setattr(sys, "argv", [str(ROOT / "service_wrapper_v5.py"),
                        "--binding", str(binding_path), "--run-dir", str(run_dir)])
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "fixture-gpu")
    monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY", "fixture-not-secret")
    wrapper.main()
    assert observed["alias"] == s.MODEL["alias"]
    assert observed["command"] == ["/fixture/prime/bin/inference", "@",
                                    str(run_dir / "inference.json")]
    assert s.read(run_dir / "BINDING.json") == binding
    assert s.read(run_dir / "endpoint-original.json")["base_model"] == s.MODEL
    assert s.read(run_dir / "ALLOCATION_DRIVER.json")["qualified_service_sha256"] == \
        wrapper.QUALIFIED_SERVICE_SHA256


def test_attempt003_owner_lifecycle_and_driver_namespaces_compose():
    import owner_v4
    import service_wrapper_v5

    suite = owner_v4.module.load_suite()
    expected = ROOT / "outputs/attempt-003"
    assert owner_v4.module.ATTEMPT == expected
    assert suite.SERVE == Path(service_wrapper_v5.__file__)
    argv = owner_v4.module.collector_argv(ROOT / "stage", expected, 1234.5)
    assert argv[1] == str(ROOT / "driver_v4.py")
    assert argv[6] == str(expected / "rollout")
    with pytest.raises(ValueError):
        owner_v4.module.collector_argv(ROOT / "stage", ROOT / "outputs/attempt-002", 1234.5)
