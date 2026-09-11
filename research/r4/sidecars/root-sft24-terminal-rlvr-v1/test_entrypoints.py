"""Narrow actual-entry and owner composition checks; no GPU process is launched."""
import importlib.util
import os
from pathlib import Path
import runpy
import signal
import sys
import types
from unittest.mock import patch

import warm_collect as collect
import warm_owner as owner
import warm_study as study
import warm_train as train


def test_actual_cli_namespaces_and_training_runtime():
    stage = Path("/tmp/cpu-no-launch")
    collected = collect.parse_args(owner.collector_argv(stage, 1234.0)[2:])
    trained = train.parse_args(owner.trainer_argv(stage, 4321.0)[2:])
    assert collected.spec == stage / "CAPTURE_SPEC.json"
    assert collected.output == stage / "rollout" and collected.deadline == 1234.0
    assert trained.group == stage / "collection/export/GROUP.json"
    assert trained.generation == stage / "GENERATION.json" and trained.deadline == 4321.0
    assert Path(study.TRAIN).name == "python" and "bootstrap" in str(study.TRAIN)


def test_owner_composes_all_windows_updates_and_paired_final(tmp_path, monkeypatch):
    output = tmp_path / "attempt"
    starts, releases, collections, trains = [], [], [], []
    suite = types.SimpleNamespace(
        start_service=lambda stage, binding, deadline: starts.append(stage),
        release_service=lambda stage: releases.append(stage),
    )
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "CPU_INTERCEPT_ONLY")
    monkeypatch.setattr(study, "ATTEMPT", output)
    monkeypatch.setattr(study, "runtime", lambda: (None, None))
    monkeypatch.setattr(owner, "dependencies", lambda: suite)
    monkeypatch.setattr(collect, "binding_for", lambda policy: {"policy": policy})

    def collected(_suite, _service, stage, phase, _deadline, generation=None, cap=600):
        collections.append((phase, generation, cap))
        if phase.startswith("window-"):
            study.write(stage / "export/MANIFEST.json", {"phase": phase})
        return {"complete": True, "integrity_failures": [],
                "training_group_episodes": 1 if phase.startswith("window-") else 0}

    def trained(_suite, _stage, _cutoff, generation):
        trains.append(generation)
        policy = dict(generation["previous_policy"])
        policy.update(step=generation["round"], rl_step=generation["round"],
                      adapter_sha256=f"step-{generation['round']}")
        return policy

    monkeypatch.setattr(owner, "collection_stage", collected)
    monkeypatch.setattr(owner, "train_window", trained)
    result = owner.execute(output)
    assert [item[0] for item in collections[:8]] == [f"window-{i}" for i in range(1, 9)]
    assert [item[0] for item in collections[8:]] == ["readout-unchanged", "readout-trained"]
    assert len(trains) == 8 and result["selection"]["actual_optimizer_step"] == 8
    assert len(starts) == len(releases) == 10 and result["complete"]
    assert result["weak_instantiation"] is False
    signal.setitimer(signal.ITIMER_REAL, 0)


def test_actual_owner_service_entry_reaches_inference_config(tmp_path, monkeypatch):
    monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY", "CPU_FIXTURE_NOT_CREDENTIAL")
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "CPU_INTERCEPT_ONLY")
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
            saved = list(sys.path)
            try:
                with patch.object(sys, "argv", argv[1:]), patch(
                        "importlib.util.spec_from_file_location", side_effect=instrument):
                    runpy.run_path(argv[1], run_name="__main__")
            finally:
                sys.path[:] = saved
            raise InterceptedLaunch("CPU interception before model launch")
        config = study.read(Path(argv[2]))
        assert config["vllm"]["max_model_len"] == 8192
        assert config["vllm"]["max_loras"] == 2
        return types.SimpleNamespace(pid=999999, returncode=0, poll=lambda: 0)

    monkeypatch.setattr(study, "ATTEMPT", output)
    monkeypatch.setattr(suite.life.v1, "ports_free", lambda *_args: True)
    monkeypatch.setattr(suite.subprocess, "Popen", popen)
    monkeypatch.setattr(suite, "release_service", lambda stage: releases.append(stage))
    result = owner.execute(output)
    assert len([call for call in spawned if Path(call[0]).name == "inference"]) == 3
    assert len(releases) == 3 and result["released"]
    assert result["training_stop"]["type"] == "InterceptedLaunch"
    assert result["selection"]["actual_optimizer_step"] == 0
    signal.setitimer(signal.ITIMER_REAL, 0)
