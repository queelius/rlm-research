"""Tests catch process exit races and accidental reapplication of saved updates."""
import importlib.util
import ast
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent


def candidate():
    if not (ROOT / "driver.py").exists():
        class BeforeFix:
            @staticmethod
            def observe_or_absent(observer, pid):
                return observer(pid)
        return BeforeFix
    spec = importlib.util.spec_from_file_location("lifecycle_cont_test", ROOT / "driver.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("error", [ProcessLookupError(3, "No such process"), FileNotFoundError(2, "Gone")])
def test_vanished_process_during_identity_read_is_absent(error):
    def exiting(_pid):
        raise error
    assert candidate().observe_or_absent(exiting, 12345) is None


def test_permission_failure_is_not_mistaken_for_process_exit():
    def denied(_pid):
        raise PermissionError("denied")
    with pytest.raises(PermissionError):
        candidate().observe_or_absent(denied, 12345)


def test_live_identity_is_preserved_exactly():
    identity = {"pid": 12345, "uid": 1000, "pgid": 12345, "start_ticks": 123456}
    assert candidate().observe_or_absent(lambda _pid: identity, 12345) is identity


def test_inherited_stages_do_not_include_unfinished_round7():
    assert candidate().inherited_names() == [
        "round-01", "round-02", "round-03", "round-04", "round-05", "round-06",
        "validation-00", "validation-02", "validation-04",
    ]


def test_continuation_clock_keeps_cleanup_reserve():
    value = candidate().run_envelope(10000.0, "gpu-fixture", "campaign-fixture", "sha-fixture")
    assert value["started_epoch"] == 10000.0
    assert value["deadline_epoch"] == 12880.0
    assert value["inherited_optimizer_steps"] == 6


def test_observed_getpgid_race_in_the_frozen_identity_reader(monkeypatch):
    source = ROOT.parent / "root-rlvr-campaign-v1/campaign.py"
    definition = next(node for node in ast.parse(source.read_text()).body
                      if isinstance(node, ast.FunctionDef) and node.name == "process_identity")
    namespace = {"Path": Path, "os": os}
    exec(compile(ast.Module(body=[definition], type_ignores=[]), str(source), "exec"), namespace)
    original = namespace["process_identity"]
    assert original(os.getpid())["pid"] == os.getpid()
    def gone(_pid):
        raise ProcessLookupError(3, "No such process")
    monkeypatch.setattr(os, "getpgid", gone)
    with pytest.raises(ProcessLookupError):
        original(os.getpid())
    assert candidate().observe_or_absent(original, os.getpid()) is None
