import asyncio
import importlib.util
import json
from pathlib import Path

import httpx
from tokenizers import Tokenizer


ROOT = Path(__file__).resolve().parent


def load(name):
    path = ROOT / f"{name}.py"
    assert path.exists(), f"missing implementation: {path.name}"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_selection_is_exact_and_label_blind():
    prepare = load("prepare")
    confidence = {f"r{i:015x}": float(i % 3) for i in range(64)}
    selected = prepare.select_confidence("episode", confidence, 16)
    uniform = prepare.select_uniform("episode", list(confidence), 16)
    assert len(selected) == len(set(selected)) == 16
    assert len(uniform) == len(set(uniform)) == 16
    assert set(selected) <= set(confidence)
    assert set(uniform) <= set(confidence)
    assert selected == prepare.select_confidence("episode", dict(reversed(list(confidence.items()))), 16)


def test_merge_has_no_fallback_or_partial_salvage():
    protocol = load("protocol")
    baseline = {"r1": "entity", "r2": "location"}
    valid = [{"score": {"available": True, "complete_map": True, "labels": {"r1": "location"}}}]
    assert protocol.merge_selected(baseline, valid) == {
        "status": "valid", "available": True, "valid": True,
        "labels": {"r1": "location", "r2": "location"},
    }
    unavailable = [{"score": {"available": False, "complete_map": False, "labels": None}}]
    assert protocol.merge_selected(baseline, unavailable) == {
        "status": "null", "available": False, "valid": False, "labels": None,
    }
    invalid = [{"score": {"available": True, "complete_map": False, "labels": {"r1": "location"}}}]
    assert protocol.merge_selected(baseline, invalid) == {
        "status": "observed_invalid", "available": True, "valid": False, "labels": None,
    }


def test_prepared_inputs_have_exact_shape():
    prepare = load("prepare")
    value = prepare.build(write=False)
    assert value["alignment"] == {"calls": 40, "labels": 1280, "excluded": 0, "boundary_crossings": 0}
    assert len(value["plan"]) == len(value["requests"]) == 24
    assert {row["selection_arm"] for row in value["plan"]} == {"confidence", "uniform"}
    assert sum(row["n"] for row in value["plan"] if row["selection_arm"] == "confidence") == 320
    assert sum(row["n"] for row in value["plan"] if row["selection_arm"] == "uniform") == 320
    assert all(row["n"] in (16, 32) for row in value["plan"])


def test_actual_collector_entry_reaches_nonempty_fake_transport(tmp_path, monkeypatch):
    collect = load("collect")
    prepared = load("prepare").build(write=False)
    coordinate = prepared["plan"][0]
    body = prepared["requests"][coordinate["id"]]
    labels = {identifier: "entity" for identifier in coordinate["ids"]}
    content = json.dumps(labels, separators=(",", ":"))
    tokenizer = Tokenizer.from_file(str(load("prepare").TOKENIZER))
    completion_ids = tokenizer.encode(content + "<|im_end|>", add_special_tokens=False).ids
    raw = {"model": body["model"], "request_id": "cpu-fixture", "choices": [{
        "finish_reason": "stop", "token_ids": completion_ids,
        "logprobs": {"content": [{"token": f"token_id:{token}", "logprob": 0.0,
                                    "top_logprobs": [{"token": f"token_id:{token}", "logprob": 0.0}]}
                                   for token in completion_ids]},
    }], "usage": {"prompt_tokens": len(body["token_ids"]), "completion_tokens": len(completion_ids),
                    "prompt_tokens_details": {"cached_tokens": 0}}}
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json=raw))
    values = {"PLAN.json": [coordinate], "REQUESTS.json": {coordinate["id"]: body},
              "HOST_GOLD.json": {coordinate["context_id"]: {"labels": labels}},
              "PUBLIC.json": [], "BASELINE.json": {},
              "endpoint.json": {"host": "fixture", "port": 1, "api_key_env": "FIXTURE_KEY"}}
    monkeypatch.setenv("FIXTURE_KEY", "x")
    monkeypatch.setattr(collect.s, "verify", lambda: {"identity": "fixture"})
    original_read = collect.s.read
    monkeypatch.setattr(collect.s, "read", lambda path: values[Path(path).name]
                        if Path(path).name in values else original_read(path))
    monkeypatch.setattr(collect, "summarize", lambda *args: [])
    result = asyncio.run(collect.run(Path("endpoint.json"), tmp_path / "rollout", 9999999999.0, transport))
    assert result["cost"]["attempted"] == 1
    assert result["rows"][0]["score"]["complete_map"] is True


def test_owner_entry_uses_actual_collector_and_no_fallback(tmp_path):
    owner = load("owner")
    argv = owner.collector_argv(tmp_path, tmp_path / "rollout", 123.0)
    assert argv[1] == str(ROOT / "collect.py")
    assert argv[-1] == "123.0"
    assert owner.s.binding()["batch_granularity"]["planned"] == 24


def test_actual_owner_execute_reaches_collector_argv_and_releases(tmp_path, monkeypatch):
    owner = load("owner")
    prepared = load("prepare").build(write=False)
    coordinate = prepared["plan"][0]
    attempt = tmp_path / "attempt"
    seen = {}

    class Suite:
        def start_service(self, stage, binding, deadline):
            seen["binding"] = binding

        def command(self, stage, name, argv, timeout, deadline):
            seen["argv"] = argv
            directory = attempt / "rollout/calls" / coordinate["id"]
            directory.mkdir(parents=True)
            owner.s.write(directory / "RESULT.json", {"coordinate": coordinate,
                "score": {"available": False, "complete_map": False, "labels": None,
                           "strict_correct": None, "canonical_id_matches": None,
                           "output_order_equal": None, "invalid_reason": None},
                "error": "CPU owner seam; no physical model call"})

        def release_service(self, stage):
            seen["released"] = True

    monkeypatch.setattr(owner.s, "ATTEMPT", attempt)
    monkeypatch.setattr(owner.s, "verify", lambda: {"identity": "fixture"})
    monkeypatch.setattr(owner.s, "dependencies", lambda: Suite())
    original_read = owner.s.read
    monkeypatch.setattr(owner.s, "read", lambda path: [coordinate]
                        if Path(path).name == "PLAN.json" else original_read(path))
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "fixture-gpu")
    monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY", "fixture-key")
    result = owner.execute(attempt)
    assert result["complete"] and result["released"] and result["runtime_fallback"] is False
    assert seen["argv"][1] == str(ROOT / "collect.py")
    assert seen["released"] is True
