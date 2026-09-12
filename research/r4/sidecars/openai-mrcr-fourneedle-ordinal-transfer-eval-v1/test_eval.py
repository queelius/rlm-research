from __future__ import annotations

import asyncio
import importlib.util
import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parent


def load(name):
    old = {key: sys.modules.get(key) for key in ("study", "checkpoint")}
    try:
        for key in ("study", "checkpoint"):
            spec = importlib.util.spec_from_file_location(key, ROOT / f"{key}.py")
            module = importlib.util.module_from_spec(spec)
            sys.modules[key] = module
            assert spec.loader is not None
            spec.loader.exec_module(module)
        spec = importlib.util.spec_from_file_location(f"fourneedle_{name}_test", ROOT / f"{name}.py")
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module
    finally:
        for key, value in old.items():
            if value is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = value


def test_prepared_inventory_schedule_and_prefixes_are_fourneedle():
    study = load("study")
    records = study.records()
    assert len(records) == 16
    assert [sum(row["target_occurrence_one_indexed"] == ordinal for row in records) for ordinal in (3, 4)] == [8, 8]
    schedule = study.schedule()
    assert [row["seed"] for row in schedule] == list(range(202609260000, 202609260016))
    public = study.read(study.INPUTS / "PUBLIC.json")
    tasks = study.read(study.INPUTS / "tasks.json")
    prefixes = study.read(study.INPUTS / "PREFIXES.json")
    assert public["record_ids"] == [row["id"] for row in records]
    assert len(tasks) == len(prefixes) == 16
    assert all(task["row_id"].startswith("omrcr-four-") for task in tasks)
    assert all(item["token_ids"] for item in prefixes.values())


def test_actual_collect_entry_crosses_real_ready_and_schedule(tmp_path, monkeypatch):
    collect = load("collect")

    class Reached(Exception):
        pass

    monkeypatch.setattr(collect.source.checkpoint, "binding", lambda arm: (_ for _ in ()).throw(Reached(arm)))
    endpoint = tmp_path / "endpoint.json"
    endpoint.write_text(json.dumps({}))
    with pytest.raises(Reached, match="base"):
        asyncio.run(collect.run("long", "base", endpoint, tmp_path / "out", 10**10))


def test_both_bindings_and_dual_service_dependency_are_exact():
    checkpoint = load("checkpoint")
    study = load("study")
    receipt = checkpoint.verify_checkpoint()
    assert receipt["fixed_primary_step"] == 32
    assert checkpoint.binding("base")["role_map"]["root"] == study.BASE_ALIAS
    assert checkpoint.binding("checkpoint32")["role_map"]["root"] == study.ADAPTED_ALIAS
    suite = study.dependencies()
    expected = study.SIDE / "runtime-an22-5801-v1/service_wrapper_v2.py"
    assert suite.SERVE == expected
    assert suite.life.__dict__["ALLOCATION_SERVICE"] == expected
