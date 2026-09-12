"""Focused conditional paired-checkpoint evaluator regressions."""

import copy
import hashlib
import json
from pathlib import Path

import pytest

import owner
import paired_eval_study as study


def test_actual_collector_build_uses_exact_frozen_schedule_and_selected_facade():
    collector = owner.build("rloo")
    rows = collector.study.schedule()
    assert collector.study is study
    assert study.resolve_branch() == "rloo"
    assert len(rows) == 64
    assert len({identifier for row in rows for identifier in row["ids"]}) == 256
    assert all(row["body"]["sampling_params"]["temperature"] == 0 for row in rows)


def test_zero_argument_verify_resolves_selected_branch(monkeypatch):
    study.select("other31")
    ready = {
        **study.plan("other31"),
        "closure_sha256": {},
        "identity": "placeholder",
    }
    ready["identity"] = study.digest(
        {key: value for key, value in ready.items() if key != "identity"}
    )
    original = study.read
    monkeypatch.setattr(
        study,
        "read",
        lambda path: ready if Path(path) == study.ready_path("other31") else original(path),
    )
    assert study.verify(require_training=False)["branch"] == "other31"


def test_branch_binding_replaces_only_child_and_preserves_root(tmp_path):
    checkpoint = tmp_path / "checkpoint-0001"
    checkpoint.mkdir()
    (checkpoint / "adapter_model.safetensors").write_bytes(b"adapter")
    (checkpoint / "adapter_config.json").write_text("{}")
    source_binding = {
        "role_map": {"root": "root", "children": [study.CHILD_ALIAS]},
        "fixed_child": study.CHILD_ALIAS,
        "models": {
            "root": {"path": "root", "adapter_sha256": "root-sha"},
            study.CHILD_ALIAS: {"path": "c32", "adapter_sha256": study.CHILD_SHA},
        },
    }
    update = {
        "experiment": study.TRAINING.name,
        "branch": "rloo",
        "step": 1,
        "baseline": study.BASELINES["rloo"],
        "shared_collection_sha256": "shared",
        "root_unchanged": True,
        "state_sha256": "state",
        "source_child": source_binding["models"][study.CHILD_ALIAS],
    }
    binding = copy.deepcopy(source_binding)
    binding["models"][study.CHILD_ALIAS] = {
        "path": str(checkpoint),
        "adapter_sha256": hashlib.sha256(b"adapter").hexdigest(),
        "config_sha256": hashlib.sha256(b"{}").hexdigest(),
    }
    binding["child_only_update"] = update
    assert study.verify_binding(
        checkpoint, "rloo", "shared", "state", source_binding, binding
    ) == binding
    broken = copy.deepcopy(binding)
    broken["models"]["root"]["adapter_sha256"] = "changed"
    with pytest.raises(ValueError, match="beyond|root"):
        study.verify_binding(
            checkpoint, "rloo", "shared", "state", source_binding, broken
        )


def test_actual_dependency_loader_and_owner_verify_entrypoint(monkeypatch):
    monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY", "cpu-placeholder-secret")
    suite = study.dependencies()
    assert callable(suite.start_service) and callable(suite.release_service)
    called = []
    monkeypatch.setattr(study, "verify", lambda: called.append(study.resolve_branch()) or {})
    collector = owner.build("other31")
    collector.study.verify()
    assert called == ["other31"]
