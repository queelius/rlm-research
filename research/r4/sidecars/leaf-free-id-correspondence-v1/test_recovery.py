from pathlib import Path

import owner_v3
import service_wrapper_v3


def test_recovery_wrapper_uses_direct_launcher_pin_not_absent_spec_entry():
    source = service_wrapper_v3.source_text()

    assert "pin=s.read(s.ROOT/'SPEC.json')['source_sha256']" not in source
    assert service_wrapper_v3.LAUNCHER_SHA256 in source
    assert "env=adapt_environment(env)" in source


def test_recovery_owner_is_additive_attempt002_with_v2_scoring_and_deadline():
    source = owner_v3.source_text()

    assert 's.ROOT / "READY_RECOVERY.json"' in source
    assert 's.ROOT / "driver_v2.py"' in source
    assert 's.ROOT / "outputs/attempt-002"' in source
    assert "collection_deadline = min(work_deadline, time.time() + 1500)" in source
    assert '"--deadline", str(collection_deadline)' in source
    assert "import lifecycle_adapter_v3 as lifecycle_adapter" in source
    assert "attempt-001" not in source


def test_recovery_output_does_not_exist_before_launch():
    assert not Path(owner_v3.module.ATTEMPT).exists()
