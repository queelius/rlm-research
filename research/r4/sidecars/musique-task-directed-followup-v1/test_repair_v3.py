"""Catch an engine-argv mismatch in actual start/claim/release, not just config."""
import importlib
import os
from pathlib import Path
import time

import pytest


def test_actual_start_claim_release_accepts_exact_v2_engine_and_rejects_other(tmp_path, monkeypatch):
    candidate = importlib.import_module(os.environ.get('REPORT_TEST_OWNER', 'owner_v3'))
    owner = candidate.implementation()
    study = owner.study
    suite = study.base_owner().study.dependencies()
    suite.SERVE = study.ROOT / 'service_wrapper_v2.py'
    suite.life.ALLOCATION_SERVICE = suite.SERVE
    if hasattr(owner, 'lifecycle'): owner.lifecycle.install(suite)
    directory = tmp_path / 'attempt/service'; directory.mkdir(parents=True)
    service = directory / 'service'; service.mkdir()
    binding = {'fixture': 'exact matching binding, not a model'}
    started = time.time()
    parent = {'pid': 900001, 'pgid': 900001, 'uid': os.getuid(), 'start_ticks': 111,
              'started_epoch': started, 'argv': [str(study.NATIVE), str(suite.SERVE)]}
    engine = {'pid': 900002, 'pgid': 900002, 'uid': os.getuid(), 'start_ticks': 112,
              'started_epoch': started, 'argv': ['PRL::Inference']}
    active = {parent['pid']: parent, engine['pid']: engine}
    monkeypatch.setenv('CUDA_VISIBLE_DEVICES', 'CPU_FIXTURE_NOT_A_GPU')
    monkeypatch.setattr(suite.life, 'observe', lambda pid: active.get(pid))
    monkeypatch.setattr(suite.life, 'live_owned', lambda records: [r for r in records if r['pid'] in active])
    monkeypatch.setattr(suite.life, 'snapshot_descendants', lambda *args: None)
    monkeypatch.setattr(suite.life.v1, 'ports_free', lambda: True)
    monkeypatch.setattr(suite, 'preflight', lambda *args: None)
    def signal_exact_group(pgid, sig):
        assert pgid == engine['pgid']
        active.pop(engine['pid'])
    monkeypatch.setattr(suite.life.os, 'killpg', signal_exact_group)
    class CPUOnlyLauncher:
        pid = parent['pid']; returncode = 0
        def __init__(self, command, **kwargs):
            assert command == [str(study.NATIVE), str(suite.SERVE), '--binding',
                               str(directory / 'BINDING.json'), '--run-dir', str(service)]
            study.write_x(service / 'BINDING.json', binding)
            study.write_x(service / 'SERVER_START.json', {
                'command': [str(study.NATIVE), str(study.ROOT / 'engine_entry_v2.py'), '@', str(service / 'inference.json')],
                'gpu': 'CPU_FIXTURE_NOT_A_GPU', 'launcher_sha256': study.sha(suite.SERVE),
                'pid': engine['pid'], 'started': started})
            study.write_x(service / 'inference.json', {'CPU_fixture': True})
            (service / 'inference.log').touch()
            study.write_x(service / 'SERVER_READY.json', {'CPU_fixture': True})
        def poll(self): return 0
    monkeypatch.setattr(suite.subprocess, 'Popen', CPUOnlyLauncher)
    suite.start_service(directory, binding, time.time() + 20)
    receipt = study.read(directory / 'SERVICE_OWNER_V2.json')
    assert receipt['process']['pid'] == 900002
    assert receipt['command'][1].endswith('/engine_entry_v2.py')
    suite.release_service(directory)
    stopped = study.read(directory / 'SERVICE_STOPPED.json')
    assert stopped['all_owned_process_identities_exited'] and stopped['ports_free']
    assert directory not in suite.LAUNCHERS
    # New directory, same exact actual claim function: a different entrypoint is rejected.
    wrong = tmp_path / 'wrong/service'; wrong.mkdir(parents=True)
    for name in ('SERVER_START.json', 'BINDING.json'):
        value = study.read(service / name)
        if name == 'SERVER_START.json': value['command'][1] = '/wrong/entrypoint.py'
        study.write_x(wrong / name, value)
    request = study.read(directory / 'SERVICE_REQUEST.json')
    request['command'][-1] = str(wrong)
    request['command'][-3] = str(wrong.parent / 'BINDING.json')
    study.write_x(wrong.parent / 'SERVICE_REQUEST.json', request)
    study.write_x(wrong.parent / 'BINDING.json', binding)
    with pytest.raises(ValueError, match='binding does not authenticate'):
        suite.life.claim_service(wrong)


def test_exception_details_redact_credentials(monkeypatch):
    import owner_v3
    monkeypatch.setenv('STRICT_RLM_CALIBRATION_API_KEY', 'private-fixture-credential')
    try:
        raise ValueError('actual failure private-fixture-credential')
    except ValueError as error:
        row = owner_v3.error_record('owner', error)
    assert row['type'] == 'ValueError' and row['message'] == 'actual failure [REDACTED]'
    assert 'ValueError: actual failure [REDACTED]' in row['traceback']
    assert 'private-fixture-credential' not in row['traceback']
