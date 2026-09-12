import asyncio,importlib.util,json,sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parent
def load(name):
    s=importlib.util.spec_from_file_location('g4_v4_'+name,ROOT/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def test_actual_inner_run_crosses_unmocked_verify(tmp_path,monkeypatch):
    c=load('collect_v4'); endpoint=tmp_path/'endpoint.json';endpoint.write_text(json.dumps({'sentinel':True}))
    class Reached(Exception):pass
    inner=c.source.source.source.source
    monkeypatch.setattr(inner.checkpoint,'binding',lambda arm: (_ for _ in ()).throw(Reached()))
    with pytest.raises(Reached):asyncio.run(c.run('train','checkpoint32',endpoint,tmp_path/'out',10**10))
def test_all_layers_and_owner_v4():
    c=load('collect_v4');expected=c.verify_ready();cursor=c
    for _ in range(5):
        assert cursor.verify_ready()==expected
        if not hasattr(cursor,'source'):break
        cursor=cursor.source
    o=load('owner_v4');assert o.verify()==expected;assert o.OUTPUT.name=='attempt-004';assert o.COLLECTOR.name=='collect_v4.py'
