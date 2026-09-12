import copy
import importlib
import inspect
import json
from pathlib import Path

import pytest

import one_update_panel_study as study
import owner


def test_actual_collector_binds_v2_facade_and_unchanged_panel(monkeypatch, tmp_path):
    expected = copy.deepcopy(study.read(study.SOURCE_BINDING))
    monkeypatch.setattr(study, "qualify_one_update", lambda: {"binding": expected})
    monkeypatch.setattr(study, "ATTEMPT", tmp_path / "not-created")
    collector = owner.build_collector()
    assert collector.study is study
    assert collector.study.binding() == expected
    assert len(study.schedule()) == 64
    assert len({x for row in study.schedule() for x in row["ids"]}) == 256
    assert len(inspect.signature(study.binding).parameters) == 0


def test_v2_qualifier_requires_exact_rng_receipt(monkeypatch, tmp_path):
    output = tmp_path / "attempt"
    output.mkdir()
    receipt = {
        "schema": "fresh48-one-update-rng-seeds-v2",
        "master_seed_unchanged": True,
        "master_seed": 202609121401,
        "python_seed": 202609121401,
        "numpy_legacy_seed": 745658489,
        "torch_seed": 202609121401,
        "torch_cuda_all_seed": 202609121401,
        "v1_failure_preserved": True,
    }
    (output / "RNG_SEEDS_ACTUAL.json").write_text(json.dumps(receipt))
    monkeypatch.setattr(study.base, "qualify_one_update", lambda value: {"eligible": True, "binding": {}})
    assert study.qualify_one_update(output)["rng_seeds"] == receipt
    receipt["numpy_legacy_seed"] = 202609121401
    (output / "RNG_SEEDS_ACTUAL.json").write_text(json.dumps(receipt))
    with pytest.raises(ValueError, match="RNG seed receipt"):
        study.qualify_one_update(output)


def test_training_binding_is_v2_and_output_is_unused():
    assert study.TRAINING.name.endswith("one-update-v2")
    assert study.TRAIN_READY_SHA == "c4a631fae66b535cdf681f45c41454bce5c6086e0ba0eee076e144d236350509"
    assert not study.TRAIN_OUTPUT.exists()
    assert not study.ATTEMPT.exists()
