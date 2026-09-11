import importlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def test_recovery_binds_leaf_weight_manifest_at_service_consumer():
    import service_wrapper_v4
    import study as s

    source = service_wrapper_v4.source_text()
    expected = s.sha(ROOT / "WEIGHTS.json")
    assert expected in source
    assert "s.sha(s.ROOT/'WEIGHTS.json')" not in source


def test_actual_owner_lifecycle_and_collector_namespaces_compose():
    import owner_v3
    import service_wrapper_v4

    suite = owner_v3.module.load_suite()
    expected = ROOT / "outputs/attempt-002"
    assert owner_v3.module.ATTEMPT == expected
    assert suite.SERVE == Path(service_wrapper_v4.__file__)
    assert suite.life.__dict__["ALLOCATION_SERVICE"] == Path(service_wrapper_v4.__file__)
    argv = owner_v3.module.collector_argv(ROOT / "stage", expected, 1234.5)
    assert argv[1] == str(ROOT / "driver_v3.py")
    assert argv[6] == str(expected / "rollout")
    with pytest.raises(ValueError):
        owner_v3.module.collector_argv(ROOT / "stage", ROOT / "outputs/attempt-001", 1234.5)


def test_recovery_driver_allows_only_attempt002():
    driver = importlib.import_module("driver_v3")

    assert driver.AUTHORIZED_OUTPUT == ROOT / "outputs/attempt-002/rollout"
    with pytest.raises(ValueError):
        driver.validate_output(ROOT / "outputs/attempt-001/rollout")
