from pathlib import Path
import importlib.machinery as machinery
import importlib.util as util
import json
import os
import subprocess
import sys
import tempfile
from unittest.mock import patch

import httpx


def test_owner_exact_namespace_and_clock():
    import owner
    import study as s

    argv = owner.collector_argv(s.ATTEMPT / "owned-service", s.ATTEMPT, 1234.5)
    assert owner.validate_argv(argv)["output"] == s.ATTEMPT / "rollout"
    assert owner.CLOCK == {"outer": 1800, "work": 1650, "owned": 1770, "startup": 180, "release": 90, "harvest": 30, "finalize": 30, "margin": 30}


def test_actual_nonempty_transport_authenticates_native_response(tmp_path):
    import asyncio
    import collect
    import protocol as p
    import study as s

    row = p.plan()[0]; body = s.read(s.ROOT / "REQUESTS.json")[row["id"]]; prompts = s.read(s.ROOT / "PROMPT_IDS.json"); context = p.contexts()[row["context_index"]]
    labels = [record["gold_label"] for record in context["records"]]
    content = s.serialize(labels if row["output"] == "labels_only" else [{"row": index, "label": label} for index, label in enumerate(labels)])
    tokenizer = s.tokenizer(); completion_ids = tokenizer.encode(content, add_special_tokens=False) + [151645]
    raw = {"model": body["model"], "prompt_token_ids": prompts[row["id"]], "choices": [{"index": 0, "message": {"role": "assistant", "content": content, "tool_calls": None}, "finish_reason": "stop", "token_ids": completion_ids, "logprobs": {"content": [{"token": "x", "logprob": -1.0, "bytes": None, "top_logprobs": []} for _ in completion_ids]}}], "usage": {"prompt_tokens": len(prompts[row["id"]]), "completion_tokens": len(completion_ids), "total_tokens": len(prompts[row["id"]]) + len(completion_ids), "prompt_tokens_details": {"cached_tokens": 0}}}
    def handler(request):
        assert json.loads(request.content) == body
        return httpx.Response(200, json=raw)
    endpoint = tmp_path / "endpoint.json"; s.write(endpoint, {"host": "fixture", "port": 1, "api_key_env": "STRICT_RLM_CALIBRATION_API_KEY", "model": s.MODEL})
    original_read = s.read
    def read(path):
        path = Path(path)
        if path == s.ROOT / "PLAN.json": return [row]
        return original_read(path)
    with patch.object(s, "verify", return_value={"identity": "cpu"}), patch.object(s, "read", side_effect=read), patch.object(s.service, "validate_descriptor", return_value=None), patch.dict(os.environ, {"STRICT_RLM_CALIBRATION_API_KEY": "fixture"}):
        result = asyncio.run(collect.run(endpoint, tmp_path / "rollout", __import__("time").time() + 60, httpx.MockTransport(handler)))
    saved = s.read(tmp_path / "rollout/calls" / row["id"] / "RESULT.json")
    assert result["available"] == 1 and saved["native_verified"] and saved["score"]["contract_valid"]


def test_actual_owned_wrapper_reaches_registered_launcher():
    import owner
    import service_wrapper
    import study as s

    observed = {}
    class Loader:
        def create_module(self, spec): return None
        def exec_module(self, module):
            module.PRIME_ENV = Path("/fixture/prime"); module._port_free = lambda port: True; module._environment = lambda: {"PATH": "/usr/bin", "LD_LIBRARY_PATH": ""}; module._server_environment = lambda environment, replica: dict(environment); module._wait_endpoint_model = lambda endpoint, process, alias, timeout: observed.update(alias=alias)
    original = util.spec_from_file_location
    def spec(name, path): return machinery.ModuleSpec(name, Loader()) if name == "base_service_environment" else original(name, path)
    def spawn(command, **kwargs): observed["command"] = command; return type("Process", (), {"pid": 424242})()
    with tempfile.TemporaryDirectory() as directory:
        stage = Path(directory) / "owned-service"; stage.mkdir(); s.write(stage / "BINDING.json", owner.binding())
        with patch.object(util, "spec_from_file_location", spec), patch.object(subprocess, "Popen", spawn), patch.dict(os.environ, {"CUDA_VISIBLE_DEVICES": "fixture", "STRICT_RLM_CALIBRATION_API_KEY": "fixture"}), patch.object(sys, "argv", [str(s.ROOT / "service_wrapper.py"), "--binding", str(stage / "BINDING.json"), "--run-dir", str(stage / "service")]): service_wrapper.main()
        start = s.read(stage / "service/SERVER_START.json")
    assert observed["alias"] == s.MODEL["alias"]
    assert observed["command"][:2] == ["/fixture/prime/bin/inference", "@"]
    assert start["launcher_sha256"] == s.sha(s.ROOT / "service_wrapper.py")
