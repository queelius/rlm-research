import importlib.util
from pathlib import Path

import pytest

import collect
import owner
import study


def test_exact_original_schedules_and_runtime_contract():
    old = study.old
    assert study.schedule("train") == old.schedule("train")
    assert study.schedule("held") == old.schedule("held")
    assert len(study.schedule("train")) == len(study.schedule("held")) == 32
    assert len({row["record_id"] for row in study.schedule("held")}) == 16
    assert callable(study.load) and callable(study.source)
    assert Path(study.source().RUNTIME_BIN).is_dir()
    hooks = collect.role_hooks()
    assert callable(hooks.installed_hooks)


def test_train32_owner_does_not_consult_held_gate(monkeypatch):
    monkeypatch.setattr(owner.source.checkpoint, "verify_checkpoint", lambda: {"eligible": True})
    monkeypatch.setattr(owner.source, "held_gate", lambda: (_ for _ in ()).throw(AssertionError("gate")))
    ready = {"identity": "i", "closure_sha256": {}, "inputs": {
        "train": {"schedule_sha256": study.digest(study.schedule("train"))},
        "held": {"schedule_sha256": study.digest(study.schedule("held"))},
    }}
    ready["identity"] = study.digest({key: value for key, value in ready.items() if key != "identity"})
    monkeypatch.setattr(owner.source.study, "read", lambda _path: ready)
    assert owner.source.verify("train32")["identity"] == ready["identity"]


def test_held_gate_reads_the_train32_stage():
    gate = owner.held_gate()
    assert gate == {"eligible": False, "reason": "train readout is absent"}


def test_actual_inherited_collector_reaches_fake_run_slot(monkeypatch, tmp_path):
    fixture_path = (
        study.SIDE / "openai-mrcr-short-root-token-tis-held-eval-v1" / "test_eval_v2.py"
    )
    spec = importlib.util.spec_from_file_location("continue32_actual_run_fixture", fixture_path)
    fixture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixture)
    monkeypatch.setattr(fixture, "load", lambda _name: collect)
    fixture.test_actual_collector_run_reaches_one_fake_slot_without_model_call(tmp_path, monkeypatch)


def test_checkpoint_contract_symbols_exist():
    import checkpoint

    for name in ("qualify_training", "ensure_checkpoint", "verify_checkpoint", "binding"):
        assert callable(getattr(checkpoint, name))
    with pytest.raises(ValueError, match="checkpoint-0032"):
        checkpoint.validate_result_header(
            {"status": "COMPLETED_32_TOTAL_UPDATES", "optimizer_steps": 31},
            Path("/tmp/not-used"),
        )
