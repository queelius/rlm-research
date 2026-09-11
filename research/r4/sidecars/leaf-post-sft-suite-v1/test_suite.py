import importlib.util
import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent


def load():
    assert (ROOT/'suite.py').exists(), 'suite coordinator absent'
    spec = importlib.util.spec_from_file_location('suite_test', ROOT/'suite.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_stage_order_and_fixed_final_binding_do_not_mislabel_selection(tmp_path):
    m = load()
    assert [(r['kind'], r['condition']) for r in m.jobs('original_old')] == [
        ('correspondence', 'representation'), ('correspondence', 'rotation'),
        ('sentiment', 'original'), ('sentiment', 'old_sft')]
    assert [(r['kind'], r['condition']) for r in m.jobs('mixed_ab')] == [('sentiment', 'A'), ('sentiment', 'B')]
    assert [(r['kind'], r['condition']) for r in m.jobs('mixed_ab', True)] == [
        ('sentiment', 'A'), ('mixed_schema', 'Afinal'), ('sentiment', 'B'), ('mixed_schema', 'Bfinal')]
    models = {'alias-a': {'path': '/checkpoint0206', 'adapter_sha256': 'a', 'config_sha256': 'ca'},
              'alias-b': {'path': '/checkpoint0204', 'adapter_sha256': 'b', 'config_sha256': 'cb'}}
    decision = {'rule': 'Fixed final epoch2; not validation-selected', 'models': models}
    m.c.write_once(tmp_path/'DECISION.json', decision)
    binding = m.final_binding(models, tmp_path/'DECISION.json')
    assert binding['schema'] == 'fixed-final-epoch2-dual-leaf-binding-v1'
    assert binding['models'] == models
    assert binding['selection_sha256'] == m.c.file_hash(tmp_path/'DECISION.json')
    assert binding['role_map'] == {'root': 'alias-a', 'children': ['alias-a', 'alias-b']}
    assert 'validation-selected' not in binding['schema']


def test_failed_stage_always_releases_its_owned_service(tmp_path, monkeypatch):
    m = load()
    observed = []
    monkeypatch.setattr(m, 'start_service', lambda directory, binding, deadline: observed.append('start'))
    monkeypatch.setattr(m, 'run_jobs', lambda *args: (_ for _ in ()).throw(RuntimeError('scorer failed')))
    monkeypatch.setattr(m, 'release_service', lambda directory: observed.append(('release', directory)))
    with pytest.raises(RuntimeError, match='scorer failed'):
        m.execute_stage(tmp_path/'stage', {}, 'original_old', 100)
    assert observed == ['start', ('release', tmp_path/'stage')]
    assert m.c.read(tmp_path/'stage/STAGE_ERROR.json')['error_type'] == 'RuntimeError'


def test_reused_lifecycle_accepts_prime_title_but_rejects_pid_reuse():
    m = load()
    actual = {'pid': 123, 'uid': os.getuid(), 'pgid': 123, 'start_ticks': 900,
              'started_epoch': 1000.0, 'argv': ['PRL::Inference']}
    assert m.life.validate_start_observation(actual, {'pid': 123, 'started': 1000.1}, ['inference', '@', 'config'])
    with pytest.raises(ValueError, match='identity'):
        m.life.live_owned([actual], lambda pid: {**actual, 'start_ticks': 901})
