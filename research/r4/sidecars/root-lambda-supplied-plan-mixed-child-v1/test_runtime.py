import asyncio
import importlib.util
import json
import os
import runpy
import sys
import types
from pathlib import Path
from unittest.mock import patch

import httpx

import collect
import owner
import protocol as p
import study as s


def test_nonempty_native_transport_reaches_public_reducer(tmp_path):
    plan = s.read(s.ROOT / "inputs/PLAN.json"); row = plan[0]
    bodies = s.read(s.ROOT / "inputs/REQUESTS.json"); body = bodies[row["id"]]
    host = s.read(s.ROOT / "inputs/HOST_GOLD.json")
    _, tokenizer = s.renderer(); labels = host[row["context_id"]]["labels"]
    content = json.dumps({identifier: labels[identifier] for identifier in row["ids"]},
                         separators=(",", ":"))
    completion_ids = tokenizer.encode(content, add_special_tokens=False) + [151645]
    raw = {"model": body["model"], "request_id": "supplied-plan-fixture",
           "choices": [{"token_ids": completion_ids,
                        "logprobs": {"content": [{"logprob": -1.0}
                                                  for _ in completion_ids]},
                        "finish_reason": "stop"}],
           "usage": {"prompt_tokens": len(body["token_ids"]),
                     "completion_tokens": len(completion_ids),
                     "prompt_tokens_details": {"cached_tokens": 0}}}
    def handler(request):
        assert json.loads(request.content) == body
        return httpx.Response(200, json=raw)
    endpoint = tmp_path / "endpoint.json"
    s.write(endpoint, {"host": "fixture", "port": 1,
                       "api_key_env": "STRICT_RLM_CALIBRATION_API_KEY"})
    original = s.read
    def read(path):
        if Path(path) == s.ROOT / "inputs/PLAN.json": return [row]
        if Path(path) == s.ROOT / "inputs/PUBLIC.json":
            return [value for value in original(path) if value["id"] == row["context_id"]]
        return original(path)
    with patch.object(s, "verify", return_value={"identity": "cpu"}), \
            patch.object(s, "read", side_effect=read), \
            patch.dict(os.environ, {"STRICT_RLM_CALIBRATION_API_KEY": "fixture"}):
        result = asyncio.run(collect.run(endpoint, tmp_path / "rollout",
                                         __import__("time").time() + 60,
                                         httpx.MockTransport(handler)))
    assert result["rows"][0]["score"]["complete_map"]
    assert result["rows"][0]["native"]["provider_request_id"] == "supplied-plan-fixture"
    # One of several planned episode batches is not silently treated as a complete final.
    episode = result["episode_summary"]["episodes"][0]
    assert episode["predicted_map_coverage"] == 32 and not episode["final_valid"]


def test_owner_reaches_registered_service_entry_before_inference_launch(tmp_path):
    class Intercepted(BaseException): pass
    with patch.dict(os.environ, {"STRICT_RLM_CALIBRATION_API_KEY": "fixture"}):
        suite = s.dependencies()
    spawned = []; original_spec = importlib.util.spec_from_file_location
    def instrumented(name, path, *args, **kwargs):
        spec = original_spec(name, path, *args, **kwargs)
        if name == "dual_lora_owned_launcher":
            execute = spec.loader.exec_module
            def wrapped(module):
                execute(module); module._port_free = lambda port: True
                module._wait_endpoint_model = lambda *args, **kwargs: None
                module._load_adapter = lambda descriptor: None; module._stop = lambda process: None
            spec.loader.exec_module = wrapped
        return spec
    def popen(argv, **kwargs):
        spawned.append(argv)
        if len(spawned) == 1:
            assert Path(argv[1]) == suite.SERVE
            with patch.object(sys, "argv", argv[1:]), \
                    patch("importlib.util.spec_from_file_location", side_effect=instrumented):
                runpy.run_path(argv[1], run_name="__main__")
            raise Intercepted()
        return types.SimpleNamespace(pid=999999, returncode=0, poll=lambda: 0)
    output = tmp_path / "attempt"
    with patch.dict(os.environ, {"CUDA_VISIBLE_DEVICES": "CPU_INTERCEPT_ONLY",
                                 "STRICT_RLM_CALIBRATION_API_KEY": "fixture"}), \
            patch.object(s, "ATTEMPT", output), \
            patch.object(s, "verify", return_value={"identity": "cpu"}), \
            patch.object(s, "dependencies", return_value=suite), \
            patch.object(suite.life.v1, "ports_free", return_value=True), \
            patch.object(suite.subprocess, "Popen", side_effect=popen), \
            patch.object(suite, "release_service", return_value=None):
        result = owner.execute(output)
    assert result["error"][0]["type"] == "Intercepted" and len(spawned) == 2
    start = s.read(output / "owned-service/service/SERVER_START.json")
    assert start["launcher_sha256"] == s.sha(suite.SERVE)
