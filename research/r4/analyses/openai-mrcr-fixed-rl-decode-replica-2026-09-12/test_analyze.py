from pathlib import Path
import importlib.util
import pytest

ROOT=Path(__file__).resolve().parent

def test_both_arms_use_new_run_directories_and_frozen_new_seeds():
    assert (ROOT/'analyze.py').exists(), 'replica audit binding missing'
    spec=importlib.util.spec_from_file_location('replica_audit_fixture',ROOT/'analyze.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    a,s=m.bind()
    for arm in ('cp32','updated'):
        assert m.attempt(arm)==m.SIDE/f'outputs/{arm}-001'
    assert a.bindings().study.BASELINES['held']==m.attempt('cp32')
    assert sorted(c['seed'] for c in s.schedule('cp32'))==list(range(202609270000,202609270032))
    assert s.schedule('cp32')==s.schedule('updated')
    with pytest.raises(ValueError):m.attempt('best')
