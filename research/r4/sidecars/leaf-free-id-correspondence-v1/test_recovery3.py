from pathlib import Path

import pytest

import driver_v3
import owner_v4


def test_actual_owner_to_driver_composition_accepts_only_attempt003_rollout():
    attempt = owner_v4.module.ATTEMPT
    stage = attempt / "owned-service"
    argv = owner_v4.collector_argv(stage, attempt, 1234.5)

    parsed = driver_v3.validate_owner_argv(argv)
    assert parsed["endpoint"] == stage / "service/endpoint-original.json"
    assert parsed["output"] == attempt / "rollout" == driver_v3.AUTHORIZED_OUTPUT
    assert parsed["deadline"] == 1234.5

    wrong = list(argv)
    wrong[wrong.index("--output") + 1] = str(attempt.parent / "attempt-002/rollout")
    with pytest.raises(ValueError, match="attempt-003"):
        driver_v3.validate_owner_argv(wrong)


def test_owner_attempt003_keeps_recovery_wrapper_and_v2_contract():
    source = owner_v4.source_text()

    assert 's.ROOT / "READY_RECOVERY3.json"' in source
    assert 's.ROOT / "outputs/attempt-003"' in source
    assert "import lifecycle_adapter_v3 as lifecycle_adapter" in source
    assert "collector_argv(stage, output, collection_deadline)" in source
    assert "attempt-001" not in source and "attempt-002" not in source


def test_all_future_owned_output_consumers_are_attempt003():
    assert owner_v4.module.ATTEMPT == Path(owner_v4.s.ROOT / "outputs/attempt-003")
    assert driver_v3.AUTHORIZED_OUTPUT == owner_v4.module.ATTEMPT / "rollout"
