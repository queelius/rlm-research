"""Actual owner-to-service composition, with external process creation intercepted."""
import importlib.util
import os
from pathlib import Path
import runpy
import sys
import types
from unittest.mock import patch

import id_owner_v3 as owner
import id_study as study


def test_actual_owner_service_entry_reaches_inference_config(tmp_path, monkeypatch):
    monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY", "CPU_FIXTURE_NOT_CREDENTIAL")
    suite = owner.dependencies()
    output = tmp_path / "attempt"
    spawned, releases = [], []
    original_spec = importlib.util.spec_from_file_location

    class InterceptedLaunch(Exception):
        pass

    def instrument(name, path, *args, **kwargs):
        spec = original_spec(name, path, *args, **kwargs)
        if name == "dual_lora_owned_launcher":
            execute = spec.loader.exec_module

            def load(module):
                execute(module)
                module._port_free = lambda _port: True
                module._wait_endpoint_model = lambda *_args, **_kwargs: None
                module._load_adapter = lambda _descriptor: None
                module._stop = lambda _process: None

            spec.loader.exec_module = load
        return spec

    def popen(argv, **kwargs):
        spawned.append(list(argv))
        if Path(argv[0]).name != "inference":
            with patch.object(sys, "argv", argv[1:]), patch(
                    "importlib.util.spec_from_file_location", side_effect=instrument):
                runpy.run_path(argv[1], run_name="__main__")
            raise InterceptedLaunch("CPU process interception")
        config = study.read(argv[2])
        assert config["vllm"]["max_model_len"] == 8192
        assert config["vllm"]["max_loras"] == 2
        return types.SimpleNamespace(pid=999999, returncode=0, poll=lambda: 0)

    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "CPU_INTERCEPT_ONLY")
    monkeypatch.setattr(study, "ATTEMPT", output)
    monkeypatch.setattr(owner, "verify_v2", lambda: {"identity": "cpu"})
    monkeypatch.setattr(owner, "training_receipt", lambda: {"cpu": True})
    monkeypatch.setattr(suite.life.v1, "ports_free", lambda *_args: True)
    monkeypatch.setattr(suite.subprocess, "Popen", popen)
    monkeypatch.setattr(suite, "release_service", lambda path: releases.append(path))
    result = owner.execute(output)
    assert len([item for item in spawned if Path(item[0]).name == "inference"]) == 4
    assert releases == [output / f"service-{policy}" for policy in
                        ("sft18", "sft24", "sft12", "sft6")]
    assert result["released"] and not result["complete"]
