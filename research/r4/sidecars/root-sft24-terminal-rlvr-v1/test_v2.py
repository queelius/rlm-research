"""Regression tests for additive V2 composition; no GPU/service launch."""
import signal
import time
import types
from pathlib import Path

import pytest


def test_v2_export_binds_lazy_collector_import(tmp_path):
    import warm_export_v2 as export
    with pytest.raises(FileNotFoundError):
        export.rebuild(tmp_path / "not-an-attempt")


def test_v2_trainer_replay_uses_existing_v2_native_entry(tmp_path):
    import warm_train_v2 as train
    argv = train.native_replay_argv(tmp_path / "export/GROUP.json")
    assert Path(argv[1]).name == "warm_native_v2.py"
    assert Path(argv[1]).exists()
    assert argv[2:] == ["verify-export", "--output", str(tmp_path / "export")]


def test_v2_collection_rearms_alarm_to_collection_cap(tmp_path, monkeypatch):
    import warm_owner_v2 as owner
    observed = {}
    stage = tmp_path / "collection"

    def command(_service, _name, _argv, duration, deadline):
        observed.update(alarm=signal.getitimer(signal.ITIMER_REAL)[0], duration=duration,
                        deadline=deadline - time.time())
        owner.study.write(stage / "rollout/SPEC.json", {})
        signal.setitimer(signal.ITIMER_REAL, 0)
        raise TimeoutError("simulated fired stage alarm")

    def exported(_attempt, output):
        observed["export_alarm"] = signal.getitimer(signal.ITIMER_REAL)[0]
        owner.study.write(output / "MANIFEST.json", {})
        return {"complete": True}

    previous = signal.getitimer(signal.ITIMER_REAL)
    try:
        owner.v1.alarm(time.time() + 180)
        monkeypatch.setattr(owner.collect, "prepare_spec", lambda *_args: None)
        monkeypatch.setattr(owner.export, "export_attempt", exported)
        owner.collection_stage(types.SimpleNamespace(command=command), tmp_path / "service",
                               stage, "readout-unchanged", time.time() + 2400, cap=2340)
    finally:
        signal.setitimer(signal.ITIMER_REAL, *previous)
    assert observed["duration"] > 2300
    assert observed["alarm"] > 2300
    assert abs(observed["alarm"] - observed["duration"]) < 1
    assert observed["export_alarm"] > 2300


def test_v2_owner_uses_only_fresh_attempt002_namespace(tmp_path, monkeypatch):
    import warm_owner_v2 as owner
    attempt = tmp_path / "attempt-002"
    monkeypatch.setattr(owner, "ATTEMPT_V2", attempt)
    owner.check_output(attempt)
    with pytest.raises(ValueError):
        owner.check_output(tmp_path / "attempt-003")
    attempt.mkdir()
    with pytest.raises(FileExistsError):
        owner.check_output(attempt)
