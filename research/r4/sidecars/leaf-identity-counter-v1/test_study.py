import asyncio
import importlib
import json
from collections import Counter
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest


def module():
    assert (Path(__file__).parent / 'study.py').exists(), 'identity-counter study missing'
    return importlib.import_module('study')


def test_source_ids_stay_attached_and_construction_ignores_labels():
    s = module()
    parent = s.read(s.PARENT / 'DATA.json')
    data = s.build_data(parent)
    changed = deepcopy(parent)
    for c in changed['contexts']:
        for r in c['records']:
            r['gold_label'] = 'SENTINEL_GOLD'
    other = s.build_data(changed)
    for c, altered in zip(data['contexts'], other['contexts']):
        assert c['presentations'] == altered['presentations']
        assert [r['id'] for r in c['records']] == [r['id'] for r in altered['records']]
        assert len(set(r['id'] for r in c['records'])) == 64
        assert sorted(r['id'] for r in c['records']) == [f'q{i:04d}' for i in range(1,65)]
        assert c['presentations'][0] != c['presentations'][1]
        for order in c['presentations']:
            assert sorted(order) == list(range(64))
            assert [c['records'][i]['id'] for i in order] != [f'q{i:04d}' for i in range(1,65)]


def test_grid_balance_and_paired_id_bearing_inputs():
    s = module()
    design = s.build_design(s.build_data(s.read(s.PARENT / 'DATA.json')))
    assert len(design['plan']) == 96
    assert Counter(r['arm'] for r in design['plan']) == {a:32 for a in s.ARMS}
    orders = Counter(tuple(r['arm'] for r in design['plan'][i:i+3]) for i in range(0,96,3))
    assert len(orders) == 6 and max(orders.values()) - min(orders.values()) <= 1
    for i in range(0,96,3):
        bodies = [s.make_request(design,r) for r in design['plan'][i:i+3]]
        assert len({b['messages'][1]['content'].split(s.INPUT_MARKER)[1] for b in bodies}) == 1
        assert all(b['messages'][0] == bodies[0]['messages'][0] and b['tools'] == bodies[0]['tools'] for b in bodies)
    altered = deepcopy(design)
    for b in altered['batches']:
        for r in b['gold']['records']:
            r['gold_label'] = 'HOST_ONLY_LABEL'
    assert s.make_request(altered,altered['plan'][0]) == s.make_request(design,design['plan'][0])


def test_tag_semantics_strict_cardinality_and_nulls():
    s = module()
    d = s.build_design(s.build_data(s.read(s.PARENT / 'DATA.json')))
    for row in d['plan'][:3]:
        gold = d['batches'][row['batch_id']]['gold']
        tags = s.expected_tags(gold['records'],row['arm'])
        body = json.dumps([{'tag':tag,'label':r['gold_label']} for tag,r in zip(tags,gold['records'])])
        assert s.score_labels(body,gold)['strict_correct'] == 64
        bad = json.loads(body)
        bad[0]['tag'] = 'wrong'
        for text in (json.dumps(bad),body[:-1],json.dumps(json.loads(body)[:-1])):
            score = s.score_labels(text,gold)
            assert not score['schema_valid'] and score['predictions'] == [None]*64
        assert s.score_coordinate(d,row,[])['strict_correct_assignments'] is None


def test_real_collector_saves_three_exact_tag_arms(tmp_path):
    s = module()
    d = s.build_design(s.build_data(s.read(s.PARENT / 'DATA.json')))
    d['plan'] = d['coordinates'] = d['plan'][:3]
    requests = {r['id']:s.make_request(d,r) for r in d['plan']}
    spec = {'design':d,'requests':requests,'request_sha256':{k:s.digest(v) for k,v in requests.items()}}
    async def provider(request):
        body=json.loads(request.content)
        row=next(r for r in d['plan'] if requests[r['id']]==body)
        gold=d['batches'][row['batch_id']]['gold']
        content=json.dumps([{'tag':t,'label':r['gold_label']} for t,r in zip(s.expected_tags(gold['records'],row['arm']),gold['records'])])
        return httpx.Response(200,json={'model':s.ALIAS,'prompt_token_ids':[1],
            'choices':[{'message':{'content':content},'finish_reason':'stop','token_ids':[2]}],
            'usage':{'prompt_tokens':1,'completion_tokens':1}})
    async def go():
        async with httpx.AsyncClient(transport=httpx.MockTransport(provider)) as client:
            return await s.collect_calls(client,'http://fake/v1',spec,tmp_path)
    records,reason=asyncio.run(go())
    assert reason is None and len(records)==3
    assert all(r['score']['strict_correct']==64 and not r['capture']['tools_executed'] for r in records)


def test_owned_caps_and_release_on_error(tmp_path,monkeypatch):
    module()
    assert (Path(__file__).parent/'owned.py').exists(), 'owned96 wrapper missing'
    o=importlib.import_module('owned')
    assert o.work_deadline(1000)==2080 and o.collection_command_cap(1000,1001)==630
    with pytest.raises(TimeoutError):o.collection_command_cap(1000,2080)
    monkeypatch.setattr(o,'ROOT',tmp_path)
    (tmp_path/'WEIGHTS.json').write_text('{}')
    events=[]
    def fail(*args):raise RuntimeError('fake startup failure')
    suite=SimpleNamespace(start_service=fail,release_service=lambda *a:events.append('release'))
    weights={'models':{'old_sft':{'path':'/frozen/old','model_sha256':'sha','config_sha256':'config'}}}
    with pytest.raises(RuntimeError,match='fake startup failure'):o.execute(tmp_path/'owned',suite,weights,1000)
    assert events==['release']
