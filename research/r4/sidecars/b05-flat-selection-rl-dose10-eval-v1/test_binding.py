"""Actual inherited collector/owner aliases and frozen72 payloads, CPU only."""
from pathlib import Path
import importlib

def test_actual_inherited_entry_and_exact_all72_payloads():
    assert (Path(__file__).parent/'study.py').exists(),'dose readout not implemented'
    s=importlib.import_module('study');c=importlib.import_module('collect');o=importlib.import_module('owner');m=importlib.import_module('metrics')
    parent=s.load('dose_readout_original_study',s.PARENT/'study.py')
    assert s.calls()==parent.calls() and len(s.calls())==72
    for call in s.calls():
        a=s.request_for(call);b=parent.request_for(call)
        assert {k:v for k,v in a.items() if k!='model'}=={k:v for k,v in b.items() if k!='model'}
        assert s.prompt(call)==parent.prompt(call)
        assert a['model']==(str(s.train.BASE) if call['arm']=='base' else s.train.ALIAS)
    assert s.train.LEARNING_RATE==.001 and s.train.ALIAS!=parent.train.ALIAS
    assert c.implementation.inherited.study is s
    assert o.implementation.s is s and o.implementation.collect is c and o.implementation.metrics is m
    suite=s.dependencies();assert suite.SERVE==s.RUNTIME/'service_wrapper_v2.py'
