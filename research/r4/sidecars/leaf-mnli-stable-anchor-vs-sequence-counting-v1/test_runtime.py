import hashlib
import importlib.machinery as machinery
import importlib.util as util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch

import httpx

import collect
import owner
import protocol as p
import study as s


ROOT = Path(__file__).resolve().parent


def test_owner_targets_exact_local_attempt_and_collector():
    stage = s.ATTEMPT / "owned-service"
    argv = owner.collector_argv(stage, s.ATTEMPT, 12345.0)
    parsed = owner.validate_argv(argv)
    assert argv[1] == str(ROOT / "collect.py")
    assert parsed["output"] == s.ATTEMPT / "rollout"
    assert parsed["endpoint"] == stage / "service/endpoint-original.json"
    assert parsed["deadline"] == 12345.0


def test_actual_collector_entry_summarizes_all_192_null_slots():
    rows = p.plan()
    result = collect.summarize(
        [
            {
                "coordinate": row,
                "physical_attempt": False,
                "usage_observed": None,
                "score": p.null_row(row, "fixture"),
            }
            for row in rows
        ]
    )
    assert len(rows) == 192
    assert len(result["cells"]) == 12
    assert all(cell["planned"] == 16 for cell in result["cells"].values())
    assert result["costs"]["physical_requests"] == 0


def test_actual_nonempty_transport_authenticates_keyed_native_response(tmp_path):
    import asyncio

    row = next(row for row in p.plan() if row["anchor"] == "opaque")
    body = s.read(s.ROOT / "REQUESTS.json")[row["id"]]
    prompts = s.read(s.ROOT / "PROMPT_IDS.json")
    context = p.contexts()[row["context_index"]]
    keys = p.anchor_values(context, "opaque")
    content = s.serialize(
        [
            {"key": key, "label": record["gold_label"]}
            for key, record in zip(keys, context["records"], strict=True)
        ]
    )
    tokenizer = s.tokenizer()
    completion_ids = tokenizer.encode(content, add_special_tokens=False) + [151645]
    raw = {
        "model": body["model"],
        "prompt_token_ids": prompts[row["id"]],
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": content,
                    "tool_calls": None,
                },
                "finish_reason": "stop",
                "token_ids": completion_ids,
                "logprobs": {
                    "content": [
                        {"token": "x", "logprob": -1.0, "bytes": None, "top_logprobs": []}
                        for _ in completion_ids
                    ]
                },
            }
        ],
        "usage": {
            "prompt_tokens": len(prompts[row["id"]]),
            "completion_tokens": len(completion_ids),
            "total_tokens": len(prompts[row["id"]]) + len(completion_ids),
            "prompt_tokens_details": {"cached_tokens": 0},
        },
    }

    def handler(request):
        assert json.loads(request.content) == body
        return httpx.Response(200, json=raw)

    endpoint = tmp_path / "endpoint.json"
    s.write(
        endpoint,
        {
            "host": "fixture",
            "port": 1,
            "api_key_env": "STRICT_RLM_CALIBRATION_API_KEY",
            "model": s.MODEL,
        },
    )
    original_read = s.read

    def read(path):
        if Path(path) == s.ROOT / "PLAN.json":
            return [row]
        return original_read(path)

    with (
        patch.object(s, "verify", return_value={"identity": "cpu"}),
        patch.object(s, "read", side_effect=read),
        patch.object(s.service, "validate_descriptor", return_value=None),
        patch.object(collect.module, "summarize", return_value={"fixture": True}),
        patch.dict(os.environ, {"STRICT_RLM_CALIBRATION_API_KEY": "fixture"}),
    ):
        result = asyncio.run(
            collect.run(
                endpoint,
                tmp_path / "rollout",
                time.time() + 60,
                httpx.MockTransport(handler),
            )
        )
    saved = s.read(tmp_path / "rollout/calls" / row["id"] / "RESULT.json")
    assert result["available"] == 1
    assert saved["native_verified"] and saved["score"]["contract_valid"]
    assert saved["score"]["strict_correct"] == 48


def test_service_wrapper_enters_actual_ancestral_launcher_in_cpu_fixture(tmp_path):
    probe = tmp_path / "probe.json"
    fixture = tmp_path / "fixture.py"
    fixture.write_text(
        "import json,runpy,sys\n"
        "from pathlib import Path\n"
        "target=Path(sys.argv[1]);out=Path(sys.argv[2])\n"
        "import study as local\n"
        "def fake_load(name,path,pin=None,aliases_map=None):\n"
        " out.write_text(json.dumps({'name':name,'path':str(path),'pin':pin,'aliases':sorted((aliases_map or {}).keys())}))\n"
        " class W:\n"
        "  __file__=''\n"
        "  @staticmethod\n"
        "  def main(): return None\n"
        " return W\n"
        "local.prior.load=fake_load\n"
        "runpy.run_path(str(target),run_name='__main__')\n"
    )
    env = {**os.environ, "PYTHONPATH": str(ROOT), "CUDA_VISIBLE_DEVICES": ""}
    result = subprocess.run(
        [sys.executable, str(fixture), str(ROOT / "service_wrapper.py"), str(probe)],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stderr
    captured = json.loads(probe.read_text())
    target = s.PRIOR.parent / "leaf-mnli-positional-anchor-binding-v1/service_wrapper_v2.py"
    assert captured["path"] == str(target)
    assert captured["pin"] == hashlib.sha256(target.read_bytes()).hexdigest()


def test_actual_owned_wrapper_reaches_registered_popen():
    import service_wrapper

    observed = {}

    class Loader:
        def create_module(self, spec):
            return None

        def exec_module(self, module):
            module.PRIME_ENV = Path("/fixture/prime")
            module._port_free = lambda port: True
            module._environment = lambda: {"PATH": "/usr/bin", "LD_LIBRARY_PATH": ""}
            module._server_environment = lambda environment, replica: dict(environment)
            module._wait_endpoint_model = (
                lambda endpoint, process, alias, timeout: observed.update(alias=alias)
            )

    original = util.spec_from_file_location

    def spec(name, path):
        if name == "base_service_environment":
            return machinery.ModuleSpec(name, Loader())
        return original(name, path)

    def spawn(command, **kwargs):
        observed["command"] = command
        return type("Process", (), {"pid": 424242})()

    with tempfile.TemporaryDirectory() as directory:
        stage = Path(directory) / "owned-service"
        stage.mkdir()
        s.write(stage / "BINDING.json", owner.binding())
        with (
            patch.object(util, "spec_from_file_location", spec),
            patch.object(subprocess, "Popen", spawn),
            patch.dict(
                os.environ,
                {
                    "CUDA_VISIBLE_DEVICES": "fixture",
                    "STRICT_RLM_CALIBRATION_API_KEY": "fixture",
                },
            ),
            patch.object(
                sys,
                "argv",
                [
                    str(ROOT / "service_wrapper.py"),
                    "--binding",
                    str(stage / "BINDING.json"),
                    "--run-dir",
                    str(stage / "service"),
                ],
            ),
        ):
            service_wrapper.main()
        start = s.read(stage / "service/SERVER_START.json")
    assert observed["alias"] == s.MODEL["alias"]
    assert observed["command"][:2] == ["/fixture/prime/bin/inference", "@"]
    assert start["launcher_sha256"] == s.sha(ROOT / "service_wrapper.py")
