from __future__ import annotations

import asyncio
import importlib.util
import json
from pathlib import Path
import types
import pytest


ROOT = Path(__file__).resolve().parent


def load(name):
    path = ROOT / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"sft32_onpolicy_test_{name}", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_first_eight_source_order_and_fresh_grouped_schedule():
    study = load("study")
    records = study.records("train")
    source = study.model_inputs()["train"]
    assert [row["id"] for row in records] == [row["id"] for row in source[:8]]
    schedule = study.schedule("train")
    assert len(schedule) == 32
    assert [row["seed"] for row in schedule] == list(range(202609200000, 202609200032))
    assert all(row["temperature"] == 0.5 for row in schedule)
    assert all([row["repeat"] for row in schedule if row["record_id"] == item["id"]] == [0, 1, 2, 3] for item in records)
    assert len({row["id"] for row in schedule}) == 32


def test_cp32_checkpoint_binding_is_authenticated():
    checkpoint = load("checkpoint")
    receipt = checkpoint.verify_checkpoint()
    assert receipt["fixed_primary_step"] == 32
    binding = checkpoint.binding("checkpoint32")
    assert binding["role_map"]["root"].endswith("step32")
    assert binding["fixed_child"] in binding["role_map"]["children"]


def test_exact_terminal_strip_disabled_contract_is_qualified():
    study = load("study")
    hooks = study.terminal_hooks()
    contract = hooks.qualify()
    assert contract["condition"] == "terminal-strip-disabled"
    assert contract["general_lossless_parser"] is False
    assert contract["gold_dependent_repair"] is False


def test_diagnostics_preserve_program_stdout_and_raw_terminal_tokens():
    collect = load("collect")

    class Tokenizer:
        def decode(self, ids, skip_special_tokens=True):
            return "ANSWER  " if skip_special_tokens else "ANSWER  <eos>"

    raw = {
        "traces": [{
            "id": "trace", "root_reply": "ANSWER",
            "nodes": [
                {"message": {"role": "assistant", "tool_calls": [{"name": "ipython", "arguments": json.dumps({"code": "data=json.load(open('/context.json')); print(data[0])"})}]}},
                {"message": {"role": "tool", "content": "ANSWER  \n"}},
            ],
        }]
    }
    native = [{
        "index": 0, "session_id": "trace", "status": "returned", "model": "root",
        "response": {"model": "root", "finish_reason": "stop", "tokens": {
            "prompt_ids": [1, 2], "completion_ids": [3, 4], "completion_logprobs": [-0.2, -0.3],
        }},
    }]
    mapping = {"matches": [{"role": "root", "audit_index": 0, "node": 0}], "root_actions": 1}
    value = collect.mechanism_diagnostics(raw, native, mapping, {"answer": "ANSWER  "}, Tokenizer())
    assert value["first_program"]["ast_parseable"] and value["first_program"]["reads_context_json"]
    assert value["first_stdout"]["equals_gold_plus_newline"]
    turn = value["root_learning_evidence"][0]
    assert turn["prompt_ids"] == [1, 2] and turn["action_ids"] == [3, 4]
    assert turn["old_logprobs"] == [-0.2, -0.3] and turn["terminal_root_action"]
    assert value["terminal_transport"]["trace_final_equals_raw_decode_skip_special_true"] is False
    assert value["terminal_transport"]["raw_decode_skip_special_true_suffix_repr"] == "'ANSWER  '"


def test_actual_collector_reaches_fake_run_slot(tmp_path, monkeypatch):
    collect = load("collect")
    module = collect.source
    monkeypatch.setattr(module, "verify_ready", lambda: {"identity": "fake"})
    coordinate = module.study.schedule("train")[0]
    endpoint_dir = tmp_path / "service" / "service"
    endpoint_dir.mkdir(parents=True)
    binding_file = endpoint_dir.parent / "BINDING.json"
    binding_file.write_text("{}")
    endpoint = {
        "model_alias": "fake-root", "host": "127.0.0.1", "port": 1,
        "api_key_env": "SFT32_SCREEN_FAKE", "base_model": {"path": "fake-base"},
        "adapter": {"path": "fake-adapter", "model_sha256": "m", "config_sha256": "c"},
        "role_binding_sha256": module.study.sha(binding_file),
    }
    endpoint_path = endpoint_dir / "endpoint-original.json"
    endpoint_path.write_text(json.dumps(endpoint))
    monkeypatch.setenv("SFT32_SCREEN_FAKE", "cpu-fixture")
    binding = {"models": {"fake-root": {"path": "fake-adapter", "adapter_sha256": "m", "config_sha256": "c"}}, "role_map": {"root": "fake-root", "children": []}}
    monkeypatch.setattr(module.checkpoint, "binding", lambda _arm: binding)
    monkeypatch.setattr(module.checkpoint, "RECEIPT", binding_file)
    monkeypatch.setattr(module.study, "schedule", lambda phase: [coordinate])
    monkeypatch.setattr(module.study, "read", lambda path: endpoint if Path(path) == endpoint_path else ({coordinate["record_id"]: {"answer": "x", "random_string_to_prepend": "m"}} if Path(path).name == "HOST_GOLD.json" else ({coordinate["id"]: {"token_ids": [1]}} if Path(path).name == "PREFIXES.json" else json.loads(Path(path).read_text()))))

    class Data: name = coordinate["id"]
    class Task: data = Data()
    class Episode:
        group = None
        def record_run(self, _info): pass
        def to_record(self): return {"ok": True, "errors": [], "traces": [{"id": "t", "calls": []}]}
    class Serving:
        async def __aenter__(self): return self
        async def __aexit__(self, *_): return False
    class Env:
        taskset = [Task()]
        def serving(self): return Serving()
        async def run_slot(self, _slot, _context): return Episode()

    monkeypatch.setattr(module.study, "environment", lambda _phase: Env())
    monkeypatch.setattr(module, "model_context", lambda *_: object())
    monkeypatch.setattr(module, "inspect_trace", lambda *_args, **_kwargs: {
        "scientifically_available": False, "reward": None, "root_reply": None,
        "raw_exact": False, "normalized_exact": False, "root_actions_returned": 0,
        "child_actions_returned": 0, "prompt_tokens": 0, "completion_tokens": 0,
        "usage_unknown_calls": 0, "native_mapping_complete": True,
        "initial_root_prefix_verified": True, "six_total_root_child_cap_respected": True,
        "causal_mapping": {"matches": [], "root_actions": 0},
    })
    fake_hooks = types.SimpleNamespace()
    class Installed:
        def __enter__(self): return self
        def __exit__(self, *_): return False
    fake_hooks.installed_hooks = lambda *_: Installed()
    monkeypatch.setattr(module, "role_hooks", lambda: fake_hooks)
    result = asyncio.run(collect.run("train", "checkpoint32", endpoint_path, tmp_path / "out", 10**10))
    assert result == 0
    saved = json.loads((tmp_path / "out/RESULT.json").read_text())
    assert saved["recorded"] == 1 and saved["complete"]
    contract = json.loads((tmp_path / "out/TERMINAL_STRIP_CONTRACT.json").read_text())
    assert contract["condition"] == "terminal-strip-disabled"


def test_owner_is_fixed_to_one_attempt_and_cap():
    study = load("study")
    owner = load("owner")
    assert owner.OUTPUT == study.ROOT / "outputs/attempt-001"
    assert study.SCIENCE_SECONDS == 900 and study.OWNER_SECONDS == 1100
    with pytest.raises(ValueError, match="exact 1100-second"):
        owner.execute(owner.OUTPUT, 1099)
