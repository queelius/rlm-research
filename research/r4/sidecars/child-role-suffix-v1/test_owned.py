import time
from pathlib import Path
from types import SimpleNamespace
import pytest


def test_owned_envelope_releases_after_collection_failure_and_keeps_original_clock(tmp_path,monkeypatch):
    assert (Path(__file__).parent/'owned.py').exists(), 'bounded owned envelope missing'
    import owned
    calls=[]
    suite=SimpleNamespace(PYTHON='/cpu/python')
    suite.start_service=lambda directory,binding,deadline:calls.append(('start',deadline))
    def command(*args):
        calls.append(('collect',args[-2],args[-1]))
        raise RuntimeError('fixture collection failure')
    suite.command=command
    suite.release_service=lambda directory:calls.append(('release',str(directory)))
    monkeypatch.setattr(owned.e,'bind',lambda *args:None)
    started=time.time()-10
    result=owned.execute(tmp_path/'owned',suite,{'role_binding':{}},started)
    assert not result['complete'] and result['error']['message']=='fixture collection failure'
    assert [c[0] for c in calls]==['start','collect','release']
    assert calls[0][1]==started+180
    assert calls[1][-1]==started+1680
    assert result['deadline_epoch']==started+1800
    assert calls[1][1]<=1530
