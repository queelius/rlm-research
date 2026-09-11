"""Breaks caught: cached mutable returns, hidden target input, and unpaired plan."""
import importlib.util
import json
from pathlib import Path

def protocol():
    path=Path(__file__).with_name('cl_protocol.py')
    assert path.exists(), 'canonical source access is not implemented'
    import cl_protocol
    return cl_protocol

def test_loader_returns_only_original_plain_objects_and_reloads_after_mutation():
    p=protocol();records='[{"id":"qa","user":"u0","text":"literal question","weight":7}]';raw='{"qa":"location"}'
    namespace={};exec(compile(p.module_source(records,raw),'AUTHORED_LOADER','exec'),namespace)
    first=namespace['load']()
    assert first=={'records':[{'id':'qa','user':'u0','text':'literal question','weight':7}], 'predictions':{'qa':'location'}}
    assert type(first) is dict and type(first['records']) is list and type(first['records'][0]) is dict
    first['records'][0]['weight']=999;first['predictions']['qa']='entity';first['records'].clear()
    second=namespace['load']()
    assert second['records'][0]['weight']==7 and second['predictions']=={'qa':'location'}
    assert second is not first and second['predictions'] is not first['predictions']

def test_all_blocks_pair_fresh_seed_and_no_source_error_repair():
    p=protocol();values=p.build();rows=values['PLAN.json']
    assert len(rows)==48 and len(values['REUSED_SOURCES.json'])==8
    for block in range(24):
        pair=[r for r in rows if r['block']==block]
        assert {r['representation'] for r in pair}=={'FILE','LOADER'}
        assert len({r['seed'] for r in pair})==1 and pair[0]['seed']==981631101+block
        assert len({r['task_name'] for r in pair})==1
    assert sum(r['representation']=='LOADER' and r['position']==0 for r in rows)==12
    for entry in values['REUSED_SOURCES.json']:
        actual=entry['record'];assert actual['map']['raw']==actual['raw_response']['choices'][0]['message']['content']
        assert p.map_state(actual['map']['raw'],list(actual['map']['labels']))['labels']==actual['map']['labels']

def test_accessor_signature_has_no_task_or_oracle_and_no_query_dependency():
    import inspect
    p=protocol();assert list(inspect.signature(p.module_source).parameters)==['records_json','map_raw']
    code=p.module_source('[]','{}');namespace={};exec(compile(code,'AUTHORED_EMPTY_LOADER','exec'),namespace)
    assert namespace['load']()=={'records':[],'predictions':{}}
    assert list(inspect.signature(namespace['load']).parameters)==[]
