"""Run the real coordinator to its first training boundary without a model call."""
import argparse
import importlib.util
import json
from pathlib import Path

import pytest
loader = importlib.util.spec_from_file_location('equality_reuse_driver', Path(__file__).parent / 'driver.py')
d = importlib.util.module_from_spec(loader)
loader.loader.exec_module(d)


def test_saved_exports_skip_validation_and_collection_before_first_update(tmp_path, monkeypatch):
    output = tmp_path / 'run'
    output.mkdir()
    d.stage_inherited(output)
    d.c.write_once(output / 'RUN.json', d.run_envelope(__import__('time').time(), 'CPU-fixture'))
    events = []
    def no_service(*args, **kwargs):
        raise AssertionError('saved validation/round1 must not start a service')
    def training(command, *args, **kwargs):
        events.append(command)
        assert command[:2] == [str(d.c.TRAIN_PYTHON), str(d.a.BROAD / 'campaign_train.py')]
        raise RuntimeError('CPU_STOP_AT_FIRST_TRAINING')
    monkeypatch.setenv('CUDA_VISIBLE_DEVICES', 'CPU-fixture')
    monkeypatch.setattr(d.coordinator.impl, 'start_service', no_service)
    monkeypatch.setattr(d.coordinator.impl, 'ports_free', lambda: True)
    monkeypatch.setattr(d.coordinator.impl, 'owned_command', training)
    # Real prepared-export authentication is exercised by prepare.py; no duplicate
    # full raw replay is needed merely to test state-machine dispatch.
    monkeypatch.setattr(d.coordinator.impl.native, 'authenticate_export', lambda path: {})
    with pytest.raises(RuntimeError, match='CPU_STOP_AT_FIRST_TRAINING'):
        d.coordinator.impl.run_campaign(argparse.Namespace(output=output, resume=True))
    assert len(events) == 1
    mapping = json.loads((output / 'INHERITED_STAGES.json').read_text())
    assert mapping['rerolled_episodes'] == mapping['reapplied_updates'] == 0
    assert (output / 'round-01/GENERATION.json').read_bytes() == (d.a.PRIOR_RUN / 'round-01/GENERATION.json').read_bytes()
