import asyncio
import importlib.util
import json
from pathlib import Path

import httpx
from tokenizers import Tokenizer

ROOT = Path(__file__).parent


def load(name):
    spec = importlib.util.spec_from_file_location("ta_" + name, ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def test_task_aware_selection_and_overlap_are_frozen_without_gold():
    value = load("prepare").build(write=False)
    assert len(value["plan"]) == 48
    assert sum(x["n"] for x in value["plan"]) == 1280
    assert {x["selection_arm"] for x in value["plan"]} == {"confidence", "task_aware"}
    assert {x["sample"] for x in value["plan"]} == {"A", "B"}
    assert sum(len(x["overlap"]) for x in value["selections"]) == 164
    assert value["overlap_fraction"] == 164 / 320 < .90
    assert all("gold" not in json.dumps(x).lower() for x in value["requests"].values())


def test_single_and_agreement_have_exact_failure_semantics():
    p = load("protocol")
    baseline = {"r1": "entity", "r2": "location"}
    good_a = [{"score": {"available": True, "complete_map": True,
                          "labels": {"r1": "human being"}}, "coordinate": {"sample": "A"}}]
    good_b = [{"score": {"available": True, "complete_map": True,
                          "labels": {"r1": "entity"}}, "coordinate": {"sample": "B"}}]
    assert p.derive_single(baseline, good_a)["labels"]["r1"] == "human being"
    agreed = p.derive_agreement(baseline, good_a, good_b)
    assert agreed["labels"] == baseline and agreed["abstentions"] == 1
    unavailable = [{"score": {"available": False, "complete_map": False, "labels": None},
                    "coordinate": {"sample": "B"}}]
    assert p.derive_agreement(baseline, good_a, unavailable)["status"] == "null"
    invalid = [{"score": {"available": True, "complete_map": False, "labels": None},
                "coordinate": {"sample": "B"}}]
    assert p.derive_agreement(baseline, good_a, invalid)["status"] == "observed_invalid"


def test_nonempty_actual_collector_transport(tmp_path, monkeypatch):
    collect, prepare = load("collect"), load("prepare")
    built = prepare.build(write=False); coordinate = built["plan"][0]; body = built["requests"][coordinate["id"]]
    labels = {identifier: "entity" for identifier in coordinate["ids"]}
    tokenizer = Tokenizer.from_file(str(prepare.TOKENIZER))
    completion = tokenizer.encode(json.dumps(labels, separators=(",", ":")) + "<|im_end|>", add_special_tokens=False).ids
    raw = {"model": body["model"], "request_id": "cpu-fixture", "choices": [{"index": 0,
        "finish_reason": "stop", "token_ids": completion, "logprobs": {"content": [
        {"token": f"token_id:{t}", "logprob": 0.0, "top_logprobs": []} for t in completion]}}],
        "usage": {"prompt_tokens": len(body["token_ids"]), "completion_tokens": len(completion),
                  "prompt_tokens_details": {"cached_tokens": 0}}}
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json=raw))
    values = {"PLAN.json": [coordinate], "REQUESTS.json": {coordinate["id"]: body},
              "PUBLIC.json": [], "HOST_GOLD.json": {coordinate["context_id"]: {"labels": labels}}, "BASELINE.json": {},
              "endpoint.json": {"host": "fixture", "port": 1, "api_key_env": "FIXTURE_KEY"}}
    monkeypatch.setenv("FIXTURE_KEY", "x"); monkeypatch.setattr(collect.s, "verify", lambda: {"identity": "fixture"})
    old = collect.s.read; monkeypatch.setattr(collect.s, "read", lambda path: values[Path(path).name]
        if Path(path).name in values else old(path)); monkeypatch.setattr(collect, "summarize", lambda *args: [])
    result = asyncio.run(collect.run(Path("endpoint.json"), tmp_path / "rollout", 9999999999., transport))
    assert result["cost"]["attempted"] == 1 and result["rows"][0]["score"]["complete_map"]


def test_owner_wires_48_call_collector():
    owner = load("owner")
    argv = owner.collector_argv(Path("stage"), Path("output"), 123.)
    assert argv[1] == str(ROOT / "collect.py")
    assert owner.s.binding()["batch_granularity"]["planned"] == 48


def test_actual_owner_entry_reaches_collector_and_releases(tmp_path, monkeypatch):
    owner, prepare = load("owner"), load("prepare")
    coordinate = prepare.build(write=False)["plan"][0]; attempt = tmp_path / "attempt"; seen = {}
    class Suite:
        def start_service(self, stage, binding, deadline): seen["binding"] = binding
        def command(self, stage, name, argv, timeout, deadline):
            seen["argv"] = argv; d = attempt / "rollout/calls" / coordinate["id"]; d.mkdir(parents=True)
            owner.s.write(d / "RESULT.json", {"coordinate": coordinate,
                "score": {"available": False, "complete_map": False, "labels": None,
                "strict_correct": None, "canonical_id_matches": None, "output_order_equal": None,
                "invalid_reason": None}, "error": "CPU seam; no physical call"})
        def release_service(self, stage): seen["released"] = True
    monkeypatch.setattr(owner.s, "ATTEMPT", attempt); monkeypatch.setattr(owner.s, "verify", lambda: {"identity":"fixture"})
    monkeypatch.setattr(owner.s, "dependencies", lambda: Suite()); old=owner.s.read
    monkeypatch.setattr(owner.s,"read",lambda path:[coordinate] if Path(path).name=="PLAN.json" else old(path))
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES","fixture-gpu");monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY","fixture")
    result=owner.execute(attempt)
    assert result["complete"] and result["released"] and seen["released"]
    assert seen["argv"][1] == str(ROOT / "collect.py") and seen["binding"]["batch_granularity"]["planned"] == 48
