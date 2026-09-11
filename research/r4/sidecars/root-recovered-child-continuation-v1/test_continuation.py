"""CPU contracts at the coordinator/trainer seam, not mock GPU outcomes."""

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def module(name):
    spec = importlib.util.spec_from_file_location("continuation_test_" + name, ROOT / (name + ".py"))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def test_schedule_starts_with_preserved_round04_training_and_original_remaining_stages():
    driver = module("driver")
    assert driver.schedule() == [
        ("training", 4), ("validation", 4), ("collection", 5), ("training", 5),
        ("collection", 6), ("training", 6), ("validation", 6),
        ("collection", 7), ("training", 7), ("collection", 8), ("training", 8),
        ("validation", 8), ("selection", None), ("transfer", "original"), ("transfer", "selected")]


def test_fresh_launch_envelope_does_not_inherit_expired_v2_clock():
    driver = module("driver")
    envelope = driver.run_envelope(20000.0, "0", "amendment-fixture")
    assert envelope["started_epoch"] == 20000.0 and envelope["deadline_epoch"] == 30800.0
    assert envelope["new_global_cap_seconds"] == 10800


def test_verifier_dispatch_changes_only_the_native_proof_entrypoint():
    train = module("train")
    command = [str(train.c.NATIVE_PYTHON), str(train.a.OLD / "campaign_native.py"), "verify-export", "--output", "/fixed/export"]
    assert train.native_proof_command(command) == [str(train.c.NATIVE_PYTHON), str(ROOT / "native_amendment.py"), "verify-export", "--output", "/fixed/export"]
    for bad in ([*command, "--skip-checks"], [*command[:2], "collect", *command[3:]], ["python", *command[1:]]):
        with pytest.raises(ValueError):
            train.native_proof_command(bad)


def test_fixed_earliest_maximum_selection_includes_original_prior_validation():
    driver = module("driver")
    rows = [{"step": step, "strict_successes": score} for step, score in [(0, 4), (2, 5), (4, 5), (6, 3), (8, 5)]]
    assert driver.selected_step(rows) == 2
