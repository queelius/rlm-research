import asyncio
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import sys


ROOT = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_recovery_exposes_complete_reused_collector_interfaces():
    study = load("study")
    protocol = load("protocol")
    required_study = {
        "JOINT",
        "LABELS",
        "ATTEMPT",
        "ROOT",
        "corpus",
        "interface",
        "load",
        "read",
        "runtime",
        "sha",
        "stack",
        "verify",
        "write",
        "answer",
        "aliases",
        "validate",
    }
    required_protocol = {
        "correction",
        "error_probe",
        "layout",
        "null_row",
        "physical_cost",
        "producer",
        "row",
        "scalar",
        "target_spans",
        "verify_replay",
        "visible_maps",
    }
    assert not (required_study - set(dir(study)))
    assert not (required_protocol - set(dir(protocol)))


def test_actual_underlying_implementation_enters_fake_transport(tmp_path, monkeypatch):
    collect = load("collect")
    module = collect.implementation()
    calls = []

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"data": []}

    class Client:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def get(self, url):
            calls.append(url)
            return Response()

    monkeypatch.setattr("httpx.AsyncClient", Client)
    monkeypatch.setattr(module.s, "verify", lambda: {"identity": "fixture"})
    monkeypatch.setattr(module.s, "runtime", lambda: None)
    monkeypatch.setattr(module.s, "validate", lambda binding, descriptor, path: None)

    def fake_read(path):
        name = Path(path).name
        if name == "binding.json":
            return {"models": {}}
        if name == "endpoint.json":
            return {"host": "fixture", "port": 1, "api_key_env": "FIXTURE_KEY"}
        if name in {"FREE_PLAN.json", "PUBLIC.json"}:
            return []
        raise AssertionError(path)

    monkeypatch.setattr(module.s, "read", fake_read)
    monkeypatch.setenv("FIXTURE_KEY", "fixture")
    args = SimpleNamespace(
        binding=Path("binding.json"),
        endpoint=Path("endpoint.json"),
        plan="FREE_PLAN.json",
        start=0,
        stop=0,
        output=tmp_path / "out",
        mode="capture",
        deadline=99999999999.0,
    )
    with module.s.aliases({"od_binding": module.s}):
        asyncio.run(module.run(args))
    assert calls == ["http://fixture:1/v1/models"]

