from pathlib import Path

import pytest

import owner
import service_wrapper_v2


def test_missing_credential_prevents_output_creation(tmp_path, monkeypatch):
    output = tmp_path / "attempt-001"
    monkeypatch.delenv("STRICT_RLM_CALIBRATION_API_KEY", raising=False)
    monkeypatch.setattr(owner, "ATTEMPT", output)

    with pytest.raises(ValueError, match="Missing nonempty"):
        owner.execute(output)

    assert not output.exists()


def test_owner_uses_allocation_service_wrapper_v2():
    assert owner.RUNTIME_SERVICE.name == "service_wrapper_v2.py"
    assert owner.RUNTIME_SERVICE.is_file()
    assert Path(owner.RUNTIME_LIFECYCLE_MANIFEST).name == "LIFECYCLE_READY_V2.json"


def test_base_service_wrapper_pins_source_and_injects_new_driver_environment():
    adapted = service_wrapper_v2.source_text()

    assert "env=adapt_environment(env)" in adapted
    assert "ALLOCATION_DRIVER.json" in adapted
