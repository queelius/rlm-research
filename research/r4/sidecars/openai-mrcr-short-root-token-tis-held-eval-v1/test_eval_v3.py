"""Run the actual V2 boundary tests against the additive V3 entrypoints."""

import test_eval_v2 as prior


def _use_v3(monkeypatch):
    original = prior.load

    def load(name):
        return original(name.replace("_v2", "_v3"))

    monkeypatch.setattr(prior, "load", load)


def test_study_contract_and_nested_ready(monkeypatch):
    _use_v3(monkeypatch)
    prior.test_study_exports_complete_runtime_contract_and_nested_ready()


def test_actual_owner_verifier(monkeypatch):
    _use_v3(monkeypatch)
    prior.test_actual_inherited_owner_verify_source_reaches_checkpoint_gate(monkeypatch)


def test_actual_collector_contract(monkeypatch):
    _use_v3(monkeypatch)
    prior.test_actual_role_hooks_and_runtime_path_are_resolved()


def test_actual_fake_run_slot(monkeypatch, tmp_path):
    _use_v3(monkeypatch)
    prior.test_actual_collector_run_reaches_one_fake_slot_without_model_call(tmp_path, monkeypatch)

