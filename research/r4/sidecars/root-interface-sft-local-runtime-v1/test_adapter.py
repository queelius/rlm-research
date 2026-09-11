import importlib.util
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parent
def module():
    assert (ROOT/'adapter.py').exists(),'runtime adapter is not implemented'
    spec=importlib.util.spec_from_file_location('runtime_amendment_test',ROOT/'adapter.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def test_rewrites_only_eval_argv_not_training():
    m=module()
    train=['python',str(m.PRIOR/'train.py'),'run','--output','/owned/training']
    assert m.rewrite(train)==train
    evaluate=['python',str(m.PRIOR/'evaluate.py'),'--weight','initial']
    assert m.rewrite(evaluate)==['python',str(ROOT/'adapter.py'),'collect','--weight','initial']
    assert evaluate[1]==str(m.PRIOR/'evaluate.py')

def test_missing_or_wrong_owned_store_never_falls_back(tmp_path):
    m=module()
    with pytest.raises(ValueError):m.validate_store(tmp_path/'absent')
    with pytest.raises(ValueError):m.validate_store(tmp_path)

def test_local_cache_is_stage_specific():
    m=module()
    a=m.cache_path(Path('/owned/initial/rollout'));b=m.cache_path(Path('/owned/final/rollout'))
    assert a!=b and a.parent==m.STORE and b.parent==m.STORE
