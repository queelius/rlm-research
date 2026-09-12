"""Actual inherited execution-boundary regressions for V4."""

import test_eval_v2 as prior


def _load(name):
    return prior.load(name.replace("_v2", "_v4"))


def test_study_contract_and_nested_ready():
    study = _load("study_v2")
    assert callable(study.load)
    assert callable(study.source)
    assert study.source().RUNTIME_BIN.is_dir()
    ready = study.read(study.READY)
    assert ready["inputs"]["held"]["schedule_sha256"] == study.digest(study.schedule("held"))


def test_actual_owner_verifier(monkeypatch):
    owner = _load("owner_v2")
    monkeypatch.setattr(owner.source.checkpoint, "verify_checkpoint", lambda: {"eligible": True})
    ready = owner.source.verify_source()
    assert ready["status"].endswith("_V4")
    assert owner.source.verify("base")["identity"] == ready["identity"]


def test_actual_collector_contract(monkeypatch):
    original = prior.load
    monkeypatch.setattr(prior, "load", lambda name: original(name.replace("_v2", "_v4")))
    prior.test_actual_role_hooks_and_runtime_path_are_resolved()


def test_actual_fake_run_slot(monkeypatch, tmp_path):
    original = prior.load
    monkeypatch.setattr(prior, "load", lambda name: original(name.replace("_v2", "_v4")))
    prior.test_actual_collector_run_reaches_one_fake_slot_without_model_call(tmp_path, monkeypatch)

