import asyncio
import importlib.util
import json
import os
import runpy
import sys
import time
import types
from pathlib import Path
from unittest.mock import patch

import httpx

import collect
import owner
import study as s


def test_actual_nonempty_native_transport_writes_authenticated_result(tmp_path):
    plan = s.read(s.ROOT / "inputs/PLAN.json")[:1]
    bodies = s.read(s.ROOT / "inputs/REQUESTS.json")
    gold = s.read(s.ROOT / "inputs/HOST_GOLD.json")
    coordinate, body = plan[0], bodies[plan[0]["id"]]
    renderer, tokenizer = s.renderer()
    output_label = "entity" if coordinate["interface"] == "full6" else "other"
    content = json.dumps({rid: output_label for rid in coordinate["ids"]}, separators=(",", ":"))
    completion_ids = tokenizer.encode(content, add_special_tokens=False) + [151645]
    raw = {
        "model": body["model"],
        "request_id": "cpu-query-conditioned-native",
        "choices": [{"token_ids": completion_ids, "logprobs": {"content": [{"logprob": -1.0} for _ in completion_ids]}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": len(body["token_ids"]), "completion_tokens": len(completion_ids), "prompt_tokens_details": {"cached_tokens": 0}},
    }

    def handler(request):
        assert request.headers["x-science-call"] == coordinate["id"]
        assert json.loads(request.content) == body
        return httpx.Response(200, json=raw)

    endpoint = tmp_path / "endpoint.json"
    s.write(endpoint, {"host": "fixture", "port": 1, "api_key_env": "STRICT_RLM_CALIBRATION_API_KEY"})
    original_read = s.read

    def read(path):
        path = Path(path)
        if path == s.ROOT / "inputs/PLAN.json":
            return plan
        if path == s.ROOT / "inputs/REQUESTS.json":
            return bodies
        if path == s.ROOT / "inputs/HOST_GOLD.json":
            return gold
        return original_read(path)

    with patch.object(s, "verify", return_value={"identity": "cpu-fixture"}), patch.object(s, "read", side_effect=read), patch.dict("os.environ", {"STRICT_RLM_CALIBRATION_API_KEY": "cpu-fixture"}):
        result = asyncio.run(collect.run(endpoint, tmp_path / "rollout", time.time() + 60, httpx.MockTransport(handler)))
    assert result["cost"]["attempted"] == result["cost"]["responses"] == result["cost"]["choice_bearing_completions"] == 1
    assert result["rows"][0]["score"]["available"]
    assert result["rows"][0]["score"]["complete_map"]
    assert result["rows"][0]["native"]["provider_request_id"] == "cpu-query-conditioned-native"


def test_owner_binds_exact_service_identity_and_collector_namespace():
    with patch.dict("os.environ", {"STRICT_RLM_CALIBRATION_API_KEY": "cpu-fixture"}):
        suite = s.dependencies()
    binding = s.binding()
    argv = owner.collector_argv(Path("/owned"), Path("/output"), 123.0)
    assert suite.SERVE.is_file()
    assert suite.life.ALLOCATION_SERVICE == suite.SERVE
    assert binding["study"] == binding["campaign_id"] == s.ROOT.name
    assert binding["batch_granularity"]["planned"] == 192
    assert Path(argv[1]).resolve() == (s.ROOT / "collect.py").resolve()
    assert argv[-2:] == ["--deadline", "123.0"]


def test_actual_owner_reaches_registered_service_entry_before_model_launch(tmp_path):
    class InterceptedLaunch(BaseException):
        pass

    with patch.dict(os.environ, {"STRICT_RLM_CALIBRATION_API_KEY": "cpu-fixture"}):
        suite = s.dependencies()
    spawned = []
    spec_loader = importlib.util.spec_from_file_location

    def instrumented_spec(name, path, *args, **kwargs):
        spec = spec_loader(name, path, *args, **kwargs)
        if name == "dual_lora_owned_launcher":
            execute = spec.loader.exec_module

            def load_helper(module):
                execute(module)
                module._port_free = lambda port: True
                module._wait_endpoint_model = lambda *args, **kwargs: None
                module._load_adapter = lambda descriptor: None
                module._stop = lambda process: None

            spec.loader.exec_module = load_helper
        return spec

    def popen(argv, **kwargs):
        spawned.append(argv)
        if len(spawned) == 1:
            assert Path(argv[1]) == suite.SERVE
            previous = list(sys.path)
            try:
                with patch.object(sys, "argv", argv[1:]), patch("importlib.util.spec_from_file_location", side_effect=instrumented_spec):
                    runpy.run_path(argv[1], run_name="__main__")
            finally:
                sys.path[:] = previous
            raise InterceptedLaunch()
        assert Path(argv[0]).name == "inference" and argv[1] == "@"
        return types.SimpleNamespace(pid=999999, returncode=0, poll=lambda: 0)

    output = tmp_path / "attempt"
    with patch.dict(os.environ, {"CUDA_VISIBLE_DEVICES": "CPU_INTERCEPT_ONLY", "STRICT_RLM_CALIBRATION_API_KEY": "cpu-fixture"}), patch.object(s, "ATTEMPT", output), patch.object(s, "verify", return_value={"identity": "cpu-fixture"}), patch.object(s, "dependencies", return_value=suite), patch.object(suite.life.v1, "ports_free", return_value=True), patch.object(suite.subprocess, "Popen", side_effect=popen), patch.object(suite, "release_service", return_value=None):
        result = owner.execute(output)
    assert not result["complete"] and result["error"][0]["type"] == "InterceptedLaunch"
    assert len(spawned) == 2
    binding = s.read(output / "owned-service/BINDING.json")
    start = s.read(output / "owned-service/service/SERVER_START.json")
    assert binding["study"] == s.ROOT.name
    assert start["launcher_sha256"] == s.sha(suite.SERVE)
