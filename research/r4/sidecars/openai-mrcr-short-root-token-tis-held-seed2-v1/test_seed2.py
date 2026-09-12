from __future__ import annotations

import asyncio
import importlib.util
import json
from pathlib import Path
import types


ROOT = Path(__file__).resolve().parent


def load(name: str):
    path = ROOT / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"token_tis_seed2_test_{name}", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_schedule_and_prompts_are_a_paired_seed_only_replication():
    study = load("study")
    new = study.schedule("held")
    reference = study._load_base()
    old = reference.schedule("held")
    assert len(new) == len(old) == 16
    assert [row["seed"] for row in new] == list(range(2026091900, 2026091916))
    assert [row["record_id"] for row in new] == [row["record_id"] for row in old]
    for left, right in zip(new, old, strict=True):
        for key in (
            "phase", "record_id", "source_row_sha256", "ordered_core_sha256",
            "context_sha256", "row_index", "repeat", "temperature",
        ):
            assert left[key] == right[key]
        assert left["id"] != right["id"]

    study.prepare_inputs()
    public = study.read(study.input_dir("held") / "PUBLIC.json")
    tasks = study.read(study.input_dir("held") / "tasks.json")
    prefixes = study.read(study.input_dir("held") / "PREFIXES.json")
    old_dir = reference.input_dir("held")
    old_tasks = {row["row_id"]: row for row in study.read(old_dir / "tasks.json")}
    old_prefixes = study.read(old_dir / "PREFIXES.json")
    old_schedule = {row["record_id"]: row for row in old}
    assert public["plan"] == new
    assert [row["name"] for row in tasks] == [row["id"] for row in new]
    assert set(prefixes) == {row["id"] for row in new}
    for task, coordinate in zip(tasks, new, strict=True):
        old_task = old_tasks[coordinate["record_id"]]
        old_prefix = old_prefixes[old_schedule[coordinate["record_id"]]["id"]]
        assert task["prompt"] == old_task["prompt"]
        assert prefixes[coordinate["id"]]["token_ids"] == old_prefix["token_ids"]


def test_checkpoint_facade_authenticates_all_fixed_arms():
    checkpoint = load("checkpoint")
    receipt = checkpoint.verify_checkpoint()
    assert receipt["identity"]
    for arm in ("base", "lr1e-5", "lr1e-4"):
        binding = checkpoint.binding(arm)
        assert binding["role_map"]["root"]
        assert binding["role_map"]["children"]


def test_actual_owner_verifies_new_ready():
    owner = load("owner")
    for stage in owner.STAGES:
        ready = owner.verify(stage)
        assert ready["identity"] == owner.study.read(owner.study.READY)["identity"]


def test_actual_collector_reaches_fake_full_slot(tmp_path, monkeypatch):
    collect = load("collect")
    module = collect.source_module()
    monkeypatch.setattr(module, "verify_ready", lambda: {"identity": "fake-ready"})
    coordinate = module.study.schedule("held")[0]
    endpoint_dir = tmp_path / "service" / "service"
    endpoint_dir.mkdir(parents=True)
    binding_file = endpoint_dir.parent / "BINDING.json"
    binding_file.write_text("{}")
    endpoint = {
        "model_alias": "fake-root", "host": "127.0.0.1", "port": 1,
        "api_key_env": "TOKEN_TIS_SEED2_FAKE_KEY", "base_model": {"path": "fake-base"},
        "adapter": {"path": "fake-adapter", "model_sha256": "m", "config_sha256": "c"},
        "role_binding_sha256": module.study.sha(binding_file),
    }
    endpoint_path = endpoint_dir / "endpoint-original.json"
    endpoint_path.write_text(json.dumps(endpoint))
    monkeypatch.setenv("TOKEN_TIS_SEED2_FAKE_KEY", "in-memory-only")
    binding = {
        "models": {"fake-root": {"path": "fake-adapter", "adapter_sha256": "m", "config_sha256": "c"}},
        "role_map": {"root": "fake-root", "children": []},
    }
    monkeypatch.setattr(module.checkpoint, "binding", lambda _arm: binding)
    monkeypatch.setattr(module.checkpoint, "RECEIPT", binding_file)
    monkeypatch.setattr(module.study, "schedule", lambda phase: [coordinate])
    monkeypatch.setattr(
        module.study,
        "read",
        lambda path: endpoint if Path(path) == endpoint_path else (
            {coordinate["record_id"]: {"answer": "x", "random_string_to_prepend": "m"}}
            if Path(path).name == "HOST_GOLD.json" else (
                {coordinate["id"]: {"token_ids": [1]}}
                if Path(path).name == "PREFIXES.json" else json.loads(Path(path).read_text())
            )
        ),
    )

    class Data:
        name = coordinate["id"]

    class Task:
        data = Data()

    class Episode:
        group = None

        def record_run(self, _info):
            return None

        def to_record(self):
            return {"ok": True, "errors": [], "traces": [{"id": "t", "calls": []}]}

    class Serving:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_):
            return False

    class Env:
        taskset = [Task()]

        def serving(self):
            return Serving()

        async def run_slot(self, _slot, _context):
            return Episode()

    monkeypatch.setattr(module.study, "environment", lambda _phase: Env())
    monkeypatch.setattr(module, "model_context", lambda *_: object())
    monkeypatch.setattr(
        module,
        "inspect_trace",
        lambda *_args, **_kwargs: {
            "scientifically_available": False, "raw_exact": False,
            "normalized_exact": False, "reward": 0.0, "root_actions_returned": 0,
            "child_actions_returned": 0, "prompt_tokens": 0, "completion_tokens": 0,
            "usage_unknown_calls": 0, "native_mapping_complete": True,
            "initial_root_prefix_verified": True, "six_total_root_child_cap_respected": True,
        },
    )
    fake_hooks = types.SimpleNamespace()

    class Installed:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

    fake_hooks.installed_hooks = lambda *_: Installed()
    assert callable(module.role_hooks().installed_hooks)
    monkeypatch.setattr(module, "role_hooks", lambda: fake_hooks)
    result = asyncio.run(module.run("held", "base", endpoint_path, tmp_path / "out", 10**10))
    assert result == 0
    saved = json.loads((tmp_path / "out/RESULT.json").read_text())
    assert saved["recorded"] == 1 and saved["complete"] is True
