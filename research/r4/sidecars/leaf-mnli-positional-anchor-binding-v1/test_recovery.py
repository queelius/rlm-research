"""Observed launcher-identity failure and additive attempt-002 regressions."""

import importlib.machinery as machinery
import importlib.util as util
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch


def test_recovery_owner_targets_attempt002_and_v2_entries():
    import owner_v2 as owner
    import recovery_study as s

    stage = s.ATTEMPT / "owned-service"
    argv = owner.collector_argv(stage, s.ATTEMPT, 1234.5)
    value = owner.validate_argv(argv)
    assert argv[1] == str(s.ROOT / "collect_v2.py")
    assert value["output"] == s.ATTEMPT / "rollout"
    assert s.ATTEMPT == s.ROOT / "outputs/attempt-002"
    suite = owner.suite()
    assert suite.SERVE == s.ROOT / "service_wrapper_v2.py"
    assert suite.life.ALLOCATION_SERVICE == suite.SERVE


def test_actual_service_entry_is_accepted_by_registered_lifecycle():
    import owner_v2 as owner
    import recovery_study as s
    import service_wrapper_v2

    observed = {}

    class Loader:
        def create_module(self, spec):
            return None

        def exec_module(self, module):
            module.PRIME_ENV = s.NATIVE.parent.parent
            module._port_free = lambda port: True
            module._environment = lambda: {"PATH": "/usr/bin", "LD_LIBRARY_PATH": ""}
            module._server_environment = lambda environment, replica: dict(environment)
            module._wait_endpoint_model = lambda endpoint, process, alias, timeout: observed.update(alias=alias)

    original = util.spec_from_file_location

    def spec(name, path):
        return machinery.ModuleSpec(name, Loader()) if name == "base_service_environment" else original(name, path)

    def spawn(command, **kwargs):
        observed["command"] = command
        return type("Process", (), {"pid": 424242})()

    with tempfile.TemporaryDirectory() as directory:
        stage = Path(directory) / "owned-service"
        stage.mkdir(parents=True)
        binding = owner.binding()
        s.write(stage / "BINDING.json", binding)
        request_command = [str(s.NATIVE), str(s.ROOT / "service_wrapper_v2.py"), "--binding", str(stage / "BINDING.json"), "--run-dir", str(stage / "service")]
        s.write(stage / "SERVICE_REQUEST.json", {"command": request_command, "gpu": "fixture", "suite_manifest_sha256": "fixture"})
        with patch.object(util, "spec_from_file_location", spec), patch.object(subprocess, "Popen", spawn), patch.dict(os.environ, {"CUDA_VISIBLE_DEVICES": "fixture", "STRICT_RLM_CALIBRATION_API_KEY": "fixture"}), patch.object(sys, "argv", request_command[1:]):
            service_wrapper_v2.main()

        start = s.read(stage / "service/SERVER_START.json")
        assert start["launcher_sha256"] == s.sha(s.ROOT / "service_wrapper_v2.py")
        suite = owner.suite()
        actual = {"pid": start["pid"], "uid": os.getuid(), "pgid": start["pid"], "start_ticks": 123, "started_epoch": start["started"], "argv": start["command"]}
        with patch.object(suite.life, "observe", lambda pid: actual), patch.object(suite.life, "snapshot_descendants", lambda service, parent: None):
            registered = suite.life.claim_service(stage / "service")
        assert registered["server_start_sha256"] == s.sha(stage / "service/SERVER_START.json")
        assert s.read(stage / "SERVICE_OWNER_V2.json")["binding_sha256"] == s.sha(stage / "service/BINDING.json")


def test_attempt001_records_no_scientific_request():
    import recovery_study as s

    terminal = s.read(s.ROOT / "outputs/attempt-001/OWNER_TERMINAL.json")
    assert terminal["collector_status"] is None
    assert terminal["complete"] is False
    assert list((s.ROOT / "outputs/attempt-001").glob("rollout/calls/*/REQUEST.json")) == []
