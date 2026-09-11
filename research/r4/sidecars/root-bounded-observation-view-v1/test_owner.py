"""CPU-only proof of the actual owner to qualified service entry."""
import importlib.util
import os
from pathlib import Path
import runpy
import sys
import types
from unittest.mock import patch


def test_actual_owner_service_entry(tmp_path):
    import bv_owner as o
    import bv_study as s

    class InterceptedLaunch(BaseException):
        pass

    spawned = []
    original_spec = importlib.util.spec_from_file_location

    def instrument(name, path, *args, **kwargs):
        spec = original_spec(name, path, *args, **kwargs)
        if name == "dual_lora_owned_launcher":
            execute = spec.loader.exec_module

            def load(module):
                execute(module)
                module._port_free = lambda port: True
                module._wait_endpoint_model = lambda *a, **k: None
                module._load_adapter = lambda descriptor: None
                module._stop = lambda process: None

            spec.loader.exec_module = load
        return spec

    output = tmp_path / "attempt"
    stage = output / "service-sft24"
    with patch.dict(os.environ, {"STRICT_RLM_CALIBRATION_API_KEY": "CPU_FIXTURE"}):
        suite = o.dependencies()

    def popen(argv, **kwargs):
        spawned.append(argv)
        if len(spawned) == 1:
            assert len(s.read(output / "PLANNED_EVALUATION.json")["full"]) == 32
            previous = list(sys.path)
            try:
                with patch.object(sys, "argv", argv[1:]), patch(
                    "importlib.util.spec_from_file_location", side_effect=instrument
                ):
                    runpy.run_path(argv[1], run_name="__main__")
            finally:
                sys.path[:] = previous
            raise InterceptedLaunch()
        config = s.read(argv[2])
        assert Path(argv[0]).name == "inference"
        assert config["vllm"]["max_model_len"] == 8192
        return types.SimpleNamespace(pid=999999, returncode=0, poll=lambda: 0)

    releases = []
    with (
        patch.dict(
            os.environ,
            {
                "CUDA_VISIBLE_DEVICES": "CPU_INTERCEPT_ONLY",
                "STRICT_RLM_CALIBRATION_API_KEY": "CPU_FIXTURE",
            },
        ),
        patch.object(s, "ATTEMPT", output),
        patch.object(s, "verify", return_value={"identity": "CPU"}),
        patch.object(o, "dependencies", return_value=suite),
        patch.object(suite.life.v1, "ports_free", return_value=True),
        patch.object(suite.subprocess, "Popen", side_effect=popen),
        patch.object(suite, "release_service", side_effect=lambda path: releases.append(path)),
    ):
        result = o.execute(output)

    assert not result["complete"] and result["released"]
    assert len(spawned) == 2 and releases == [stage]
    endpoint = s.read(stage / "service/endpoint-original.json")
    assert endpoint["adapter"]["model_sha256"] == s.selected()["adapter_sha256"]
    assert endpoint["role_binding_sha256"] == s.sha(stage / "BINDING.json")
    assert len(result["readout_inventory"]) == 32


def test_physical_failure_remains_null_and_counted(tmp_path):
    import bv_owner as o
    import bv_study as s

    plan = s.read(s.ROOT / "inputs/EVALUATION_PLAN.json")
    row = plan["full"][0]["coordinate"]
    directory = tmp_path / "sft24/free" / row["id"]
    s.write(directory / "physical/0001.json", {"physical_request_attempt": True, "status": 400})
    inventory = o.harvest(tmp_path, plan)
    assert len(inventory) == 32
    assert inventory[0]["available"] is False and inventory[0]["reward"] is None
    assert inventory[0]["cause"] == "attempted_interrupted_no_result"
    assert o.ledger(tmp_path)["full_native"]["physical_requests_attempted"] == 1
