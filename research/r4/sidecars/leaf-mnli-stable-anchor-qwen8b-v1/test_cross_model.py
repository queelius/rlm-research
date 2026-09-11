import json
from pathlib import Path
import sys
import os
import importlib.machinery as machinery
import importlib.util as util
import subprocess
import tempfile
import time
from unittest.mock import patch

import httpx

ROOT = Path(__file__).resolve().parent
PRIOR = ROOT.parent / "leaf-mnli-stable-anchor-vs-sequence-counting-v1"
sys.path.insert(0, str(ROOT))


def test_exact_144_subset_and_same_user_messages():
    old = {row["id"]: row for row in json.loads((PRIOR / "PLAN.json").read_text())}
    plan = json.loads((ROOT / "PLAN.json").read_text())
    requests = json.loads((ROOT / "REQUESTS.json").read_text())
    prior_requests = json.loads((PRIOR / "REQUESTS.json").read_text())
    assert len(plan) == 144
    assert {row["anchor"] for row in plan} == {"labels_only", "sequential_numeric", "opaque"}
    assert all(row["seed"] == old[row["source_id"]]["seed"] for row in plan)
    for row in plan:
        assert requests[row["id"]]["messages"] == prior_requests[row["source_id"]]["messages"]
        assert requests[row["id"]]["structured_outputs"] == prior_requests[row["source_id"]]["structured_outputs"]


def test_model_and_nonthinking_template_are_explicit():
    import study as s
    assert s.MODEL["revision"] == "b968826d9c46dd6066d109eabc6255188de91218"
    assert s.MODEL["alias"] == "qwen3-8b-stable-anchor"
    body = next(iter(json.loads((ROOT / "REQUESTS.json").read_text()).values()))
    assert body["model"] == s.MODEL["alias"]
    assert body["chat_template_kwargs"] == {"enable_thinking": False}


def test_owner_exact_namespace_and_144_inventory():
    import owner
    import protocol as p
    import study as s
    stage = s.ATTEMPT / "owned-service"
    argv = owner.collector_argv(stage, s.ATTEMPT, 123.0)
    assert owner.validate_argv(argv)["output"] == s.ATTEMPT / "rollout"
    assert len(p.plan()) == 144
    assert owner.CLOCK["outer"] == 2400


def test_actual_collector_accepts_one_nonempty_native_response(tmp_path):
    import asyncio
    import collect
    import protocol as p
    import study as s
    row = next(row for row in p.plan() if row["anchor"] == "opaque")
    context = p.contexts()[row["context_index"]]
    body = s.read(ROOT / "REQUESTS.json")[row["id"]]
    prompt = s.read(ROOT / "PROMPT_IDS.json")[row["id"]]
    content = s.serialize([{"key": key, "label": record["gold_label"]} for key, record in zip(p.anchor_values(context, "opaque"), context["records"], strict=True)])
    tokenizer = s.tokenizer(); completion = tokenizer.encode(content, add_special_tokens=False) + [151645]
    raw = {"model": body["model"], "prompt_token_ids": prompt, "choices": [{"index": 0, "message": {"role": "assistant", "content": content, "tool_calls": None}, "finish_reason": "stop", "token_ids": completion, "logprobs": {"content": [{"token": "x", "logprob": -1.0, "bytes": None, "top_logprobs": []} for _ in completion]}}], "usage": {"prompt_tokens": len(prompt), "completion_tokens": len(completion), "total_tokens": len(prompt) + len(completion)}}
    endpoint = tmp_path / "endpoint.json"; s.write(endpoint, {"host": "fixture", "port": 1, "api_key_env": "STRICT_RLM_CALIBRATION_API_KEY", "model": s.MODEL})
    original = s.read
    def read(path): return [row] if Path(path) == ROOT / "PLAN.json" else original(path)
    def handler(request):
        assert json.loads(request.content) == body
        return httpx.Response(200, json=raw)
    with patch.object(s, "verify", return_value={"identity": "cpu"}), patch.object(s, "read", side_effect=read), patch.object(s.service, "validate_descriptor", return_value=None), patch.dict(os.environ, {"STRICT_RLM_CALIBRATION_API_KEY": "fixture"}):
        result = asyncio.run(collect.run(endpoint, tmp_path / "rollout", time.time() + 60, httpx.MockTransport(handler)))
    saved = original(tmp_path / "rollout/calls" / row["id"] / "RESULT.json")
    assert result["available"] == 1
    assert saved["native_verified"] and saved["score"]["contract_valid"]


def test_actual_service_wrapper_reaches_registered_8b_popen():
    import owner
    import service_wrapper
    import study as s
    observed = {}
    class Loader:
        def create_module(self, spec): return None
        def exec_module(self, module):
            module.PRIME_ENV = Path("/fixture/prime")
            module._port_free = lambda port: True
            module._environment = lambda: {"PATH": "/usr/bin", "LD_LIBRARY_PATH": ""}
            module._server_environment = lambda environment, replica: dict(environment)
            module._wait_endpoint_model = lambda endpoint, process, alias, timeout: observed.update(alias=alias)
    original = util.spec_from_file_location
    def spec(name, path): return machinery.ModuleSpec(name, Loader()) if name == "base_service_environment" else original(name, path)
    def spawn(command, **kwargs): observed["command"] = command; return type("Process", (), {"pid": 424242})()
    with tempfile.TemporaryDirectory() as directory:
        stage = Path(directory) / "owned-service"; stage.mkdir(); s.write(stage / "BINDING.json", owner.binding())
        with patch.object(util, "spec_from_file_location", spec), patch.object(subprocess, "Popen", spawn), patch.dict(os.environ, {"CUDA_VISIBLE_DEVICES": "fixture", "STRICT_RLM_CALIBRATION_API_KEY": "fixture"}), patch.object(sys, "argv", [str(ROOT / "service_wrapper.py"), "--binding", str(stage / "BINDING.json"), "--run-dir", str(stage / "service")]):
            service_wrapper.main()
        start = s.read(stage / "service/SERVER_START.json")
        inference = s.read(stage / "service/inference.json")
    assert observed["alias"] == s.MODEL["alias"]
    assert inference["vllm"]["model"] == str(s.MODEL_PATH)
    assert start["launcher_sha256"] == s.sha(ROOT / "service_wrapper.py")
