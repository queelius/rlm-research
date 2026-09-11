import importlib
import json
from pathlib import Path


def test_v4_binds_attempt002_and_native_owner_entry():
    study = importlib.import_module("readout_study_v4")
    owner = importlib.import_module("readout_owner_v4")
    assert study.ATTEMPT == study.ROOT / "outputs/attempt-002"
    assert owner.study is study
    assert owner.collector_argv(Path("/stage"), 123.0)[0] == str(study.NATIVE)


def test_v4_owner_dependency_preflight_reaches_qualified_native_stack(monkeypatch):
    owner = importlib.import_module("readout_owner_v4")
    monkeypatch.setenv("STRICT_RLM_CALIBRATION_API_KEY", "test-only-non-secret")
    suite = owner.dependencies()
    assert hasattr(suite, "start_service")
    assert hasattr(suite, "command")
    assert hasattr(suite, "release_service")


def test_v4_ready_and_campaign_bind_attempt002():
    root = Path(__file__).resolve().parent
    campaign = json.loads((root / "CAMPAIGN_V4.json").read_text())
    ready = json.loads((root / "READY_V4.json").read_text())
    expected = str(root / "outputs/attempt-002")
    assert campaign["attempt"] == expected
    assert ready["attempt"] == expected
    assert ready["identity"] == campaign["identity"]
    assert ready["campaign_sha256"]
