import asyncio
import importlib.util
import json
from pathlib import Path
import sys
import types


ROOT = Path(__file__).resolve().parent


def load(name):
    path = ROOT / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"token_tis_eval_v2_test_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_v2_study_exports_full_inherited_runtime_contract():
    study = load("study_v2")
    assert callable(study.load)
    assert callable(study.source)
    assert Path(study.source().RUNTIME_BIN).is_dir()
    ready = study.read(study.READY)
    assert ready["inputs"]["held"]["schedule_sha256"] == study.digest(study.schedule("held"))


def test_actual_inherited_owner_verify_source_reaches_checkpoint_gate(monkeypatch):
    owner = load("owner_v2")
    marker = {"eligible": True}
    monkeypatch.setattr(owner.source.checkpoint, "verify_checkpoint", lambda: marker)
    ready = owner.source.verify_source()
    assert ready["status"] == "CPU_READY_CONDITIONAL_ON_TWO_INDEPENDENT_STEP1_BRANCHES_V2"
    assert owner.source.verify("base")["identity"] == ready["identity"]


def test_actual_role_hooks_and_runtime_path_are_resolved():
    collect = load("collect_v2")
    module = collect.source_module()
    hooks = module.role_hooks()
    assert callable(hooks.installed_hooks)
    assert Path(module.study.source().RUNTIME_BIN).is_dir()
    assert module.verify_ready()["identity"] == collect.study.read(collect.study.READY)["identity"]


def test_actual_collector_run_reaches_one_fake_slot_without_model_call(tmp_path, monkeypatch):
    collect = load("collect_v2")
    module = collect.source_module()
    # Closure verification is exercised separately against the immutable READY.
    # This test isolates the subsequent environment/run_slot/runtime boundary.
    monkeypatch.setattr(module, "verify_ready", lambda: {"identity": "fake-ready"})
    coordinate = module.study.schedule("held")[0]
    endpoint_dir = tmp_path / "service" / "service"
    endpoint_dir.mkdir(parents=True)
    binding_file = endpoint_dir.parent / "BINDING.json"
    binding_file.write_text("{}")
    endpoint = {
        "model_alias": "fake-root",
        "host": "127.0.0.1",
        "port": 1,
        "api_key_env": "TOKEN_TIS_FAKE_KEY",
        "base_model": {"path": "fake-base"},
        "adapter": {"path": "fake-adapter", "model_sha256": "m", "config_sha256": "c"},
        "role_binding_sha256": module.study.sha(binding_file),
    }
    endpoint_path = endpoint_dir / "endpoint-original.json"
    endpoint_path.write_text(json.dumps(endpoint))
    monkeypatch.setenv("TOKEN_TIS_FAKE_KEY", "in-memory-only")
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
        lambda path: endpoint
        if Path(path) == endpoint_path
        else ({coordinate["record_id"]: {"answer": "x", "random_string_to_prepend": "m"}}
              if Path(path).name == "HOST_GOLD.json"
              else ({coordinate["id"]: {"token_ids": [1]}}
                    if Path(path).name == "PREFIXES.json" else json.loads(Path(path).read_text()))),
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
            "scientifically_available": False,
            "raw_exact": False,
            "normalized_exact": False,
            "reward": 0.0,
            "root_actions_returned": 0,
            "child_actions_returned": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "usage_unknown_calls": 0,
            "native_mapping_complete": True,
            "initial_root_prefix_verified": True,
            "six_total_root_child_cap_respected": True,
        },
    )
    fake_hooks = types.SimpleNamespace()

    class Installed:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

    fake_hooks.installed_hooks = lambda *_: Installed()
    actual_hooks = module.role_hooks()
    assert callable(actual_hooks.installed_hooks)
    monkeypatch.setattr(module, "role_hooks", lambda: fake_hooks)
    result = asyncio.run(module.run("held", "base", endpoint_path, tmp_path / "out", 10**10))
    assert result == 0
    saved = module.study.read(tmp_path / "out/RESULT.json")
    assert saved["recorded"] == 1 and saved["complete"] is True
