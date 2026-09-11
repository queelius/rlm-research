import asyncio
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import httpx

import collect
import protocol as p
import study as s


def test_actual_root_collector_implementation_binds_in_fresh_process():
    code = "import collect; m=collect.root_implementation(); assert callable(m.run); print(m.__name__)"
    result = subprocess.run([str(s.NATIVE), "-c", code], cwd=s.ROOT, env={**os.environ, "CUDA_VISIBLE_DEVICES": ""}, capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stderr


def test_nonempty_leaf_acquisition_uses_actual_frozen_bodies(tmp_path, monkeypatch):
    requests = s.read(s.INPUTS / "LEAF_REQUESTS.json")
    prompts = s.read(s.INPUTS / "LEAF_PROMPT_IDS.json")
    reverse = {json.dumps(body, sort_keys=True): (encoding, cid) for encoding, values in requests.items() for cid, body in values.items()}
    tokenizer = s.stable.tokenizer(); eos = tokenizer.eos_token_id
    def handler(request):
        body = json.loads(request.content); encoding, cid = reverse[json.dumps(body, sort_keys=True)]
        context = next(c for c in s.read(s.INPUTS / "DATA.json")["contexts"] if c["id"] == cid)
        values = [{"key": key, "label": "neutral"} for key in p.anchor_values(context, encoding)]
        ids = tokenizer.encode(json.dumps(values, separators=(",", ":")), add_special_tokens=False) + [eos]
        raw = {"request_id": "fake-" + cid + encoding, "model": body["model"], "choices": [{"index": 0,
            "token_ids": ids, "finish_reason": "stop", "logprobs": {"content": [{"logprob": -0.1}] * len(ids)}}],
            "usage": {"prompt_tokens": len(prompts[encoding][cid]), "completion_tokens": len(ids)}}
        return httpx.Response(200, json=raw)
    endpoint = tmp_path / "endpoint.json"; endpoint.write_text(json.dumps({"host": "fake", "port": 1, "api_key_env": "BRIDGE_FAKE_KEY"}))
    monkeypatch.setenv("BRIDGE_FAKE_KEY", "x")
    maps = asyncio.run(collect.acquire(endpoint, tmp_path / "output", time.time() + 60, httpx.MockTransport(handler)))
    assert maps is not None
    assert set(maps) == set(p.ENCODINGS)
    assert all(len(value) == 48 for encoding in maps.values() for value in encoding.values())


def test_owner_argv_binds_exact_collector_entry(tmp_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location("actual_downstream_owner", s.ROOT / "owner.py")
    owner = importlib.util.module_from_spec(spec); spec.loader.exec_module(owner)
    argv = owner.collector_argv(tmp_path, tmp_path / "out", 123.0)
    assert argv[0] == str(s.NATIVE) and argv[1] == str(s.ROOT / "collect.py")
    assert "--binding" in argv and "--deadline" in argv
