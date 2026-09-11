from pathlib import Path
import importlib.machinery as machinery
import importlib.util as util
import os
import subprocess
import sys
import tempfile
from unittest.mock import patch


def test_absent_labels_prompt_reuses_prior_natural_instruction():
    import protocol as p

    context = p.contexts()[0]
    row = next(row for row in p.plan() if row["context_index"] == 0 and row["arm"] == "wrong_absent_labels_only")
    actual = p.request(context, row)
    prior = p.prior.request(context, {"arm": "wrong_labels_only", "seed": row["seed"]})
    assert actual["messages"] == prior["messages"]
    assert "gold_label" not in actual["messages"][1]["content"]
    assert actual["tools"] if "tools" in actual else True


def test_owner_to_collector_uses_exact_attempt_namespace_and_clock():
    import owner
    import study as s

    stage = s.ATTEMPT / "owned-service"
    argv = owner.collector_argv(stage, s.ATTEMPT, 1234.5)
    value = owner.validate_argv(argv)
    assert value["endpoint"] == stage / "service/endpoint-original.json"
    assert value["output"] == s.ATTEMPT / "rollout"
    assert value["deadline"] == 1234.5
    assert owner.CLOCK == {"outer": 1800, "work": 1650, "owned": 1770, "startup": 180, "release": 90, "harvest": 30, "finalize": 30, "margin": 30}


def test_collector_is_bound_to_96_frozen_coordinates():
    import collect
    import protocol as p

    rows = [{"coordinate": row, "score": collect.scoring.missing(p.contexts()[row["context_index"]]), "physical_attempt": False, "usage_observed": None} for row in p.plan()]
    summary = collect.summarize(rows)
    assert len(summary["cells"]) == 12
    assert summary["primary"]["planned_late_labels"] == 768
    assert summary["costs"]["physical_requests"] == 0


def test_full_service_entry_reaches_launcher():
    import owner
    import service_wrapper
    import study as s

    observed = {}

    class Loader:
        def create_module(self, spec):
            return None

        def exec_module(self, module):
            module.PRIME_ENV = Path("/fixture/prime")
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
        output = Path(directory) / "attempt-001"
        stage = output / "owned-service"
        stage.mkdir(parents=True)
        s.write(stage / "BINDING.json", owner.binding())
        with patch.object(util, "spec_from_file_location", spec), patch.object(subprocess, "Popen", spawn), patch.dict(os.environ, {"CUDA_VISIBLE_DEVICES": "fixture", "STRICT_RLM_CALIBRATION_API_KEY": "fixture"}), patch.object(sys, "argv", [str(s.ROOT / "service_wrapper.py"), "--binding", str(stage / "BINDING.json"), "--run-dir", str(stage / "service")]):
            service_wrapper.main()
    assert observed["alias"] == s.MODEL["alias"]
    assert observed["command"][:2] == ["/fixture/prime/bin/inference", "@"]
