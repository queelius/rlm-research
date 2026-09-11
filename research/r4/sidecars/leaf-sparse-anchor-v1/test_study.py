import asyncio
import json
from copy import deepcopy

import httpx
import pytest


def study():
    import study as s
    return s


def test_grid_and_exact_pairs():
    s=study();d=s.build_design(s.build_data())
    assert len(d['plan'])==144 and len(d['contexts'])==12
    assert {r['seed'] for r in d['plan']}=={981296011,981296021}
    for left,right in zip(d['plan'][::2],d['plan'][1::2],strict=True):
        a,b=s.make_request(d,left),s.make_request(d,right)
        assert left['cadence']==right['cadence'] and left['arm']!=right['arm']
        assert a['messages'][1]['content'].split(s.INPUT_MARKER)[1]==b['messages'][1]['content'].split(s.INPUT_MARKER)[1]
        shape=[x['type'] for x in a['structured_outputs']['json']['prefixItems']]
        assert shape==[x['type'] for x in b['structured_outputs']['json']['prefixItems']]
        assert shape.count('object')==64//left['cadence']


def test_gold_is_host_only():
    s=study();d=s.build_design(s.build_data());row=d['plan'][0];before=s.serialize(s.make_request(d,row))
    for r in d['batches'][0]['gold']['records']: r['gold_label']='HOST_ONLY_SENTINEL'
    assert s.serialize(s.make_request(d,row))==before and 'HOST_ONLY_SENTINEL' not in before


@pytest.mark.parametrize('cadence',[1,4,16])
def test_mixed_exact_representation(cadence):
    s=study();d=s.build_design(s.build_data());row=next(r for r in d['plan'] if r['cadence']==cadence)
    gold=d['batches'][row['batch_id']]['gold'];values=s.synthetic_output(gold,gold['labels'][0])
    assert s.score_labels(s.serialize(values),gold)['schema_valid']
    values[0]={'label':gold['labels'][0],'tag':values[0]['tag']}
    bad=s.score_labels(s.serialize(values),gold)
    assert not bad['schema_valid'] and bad['strict_correct']==0 and bad['aligned_records']==0
    if cadence>1:
        values=s.synthetic_output(gold,gold['labels'][0]);values[1]={'label':gold['labels'][0]}
        assert not s.score_labels(s.serialize(values),gold)['schema_valid']


def test_duplicate_keys_and_missing_coordinates_not_repaired():
    s=study();d=s.build_design(s.build_data());row=d['plan'][0];gold=d['batches'][0]['gold']
    values=s.serialize(s.synthetic_output(gold,gold['labels'][0]))
    bad=values.replace('"label":','"label":"DUPLICATE","label":',1)
    assert not s.score_labels(bad,gold)['schema_valid']
    assert s.score_coordinate(d,row,[])['strict_correct_assignments'] is None


def test_actual_collector_callbacks_on_fake_http(tmp_path):
    s=study();d=s.build_design(s.build_data());d['plan']=d['plan'][:3];d['coordinates']=d['coordinates'][:3]
    d['max_concurrent_calls']=1
    d['rendered_prompts']={r['id']:{'typed_token_ids_sha256':s.digest([101,102])} for r in d['plan']}
    requests={r['id']:s.make_request(d,r) for r in d['plan']}
    spec={'design':d,'requests':requests,'request_sha256':{k:s.digest(v) for k,v in requests.items()}}
    byhash={s.digest(v):r for r in d['plan'] for v in [requests[r['id']]]};seen=[]
    def response(request):
        body=json.loads(request.content);row=byhash[s.digest(body)];seen.append(body)
        gold=d['batches'][row['batch_id']]['gold']
        content=s.serialize(s.synthetic_output(gold,gold['labels'][0])) if len(seen)==1 else 'invalid'
        if len(seen)==3: return httpx.Response(500,json={'error':'fixture'})
        return httpx.Response(200,json={'model':s.ALIAS,'prompt_token_ids':[101,102],
            'choices':[{'message':{'role':'assistant','content':content},'finish_reason':'stop','token_ids':[103]}],
            'usage':{'prompt_tokens':2,'completion_tokens':1}})
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(response)) as client:
            return await s.collect_calls(client,'http://fixture/v1',spec,tmp_path)
    rows,reason=asyncio.run(run())
    assert len(rows)==3 and reason=='request_error' and rows[0]['score']['schema_valid']
    assert rows[1]['score']['strict_correct']==0 and rows[2]['score'] is None
    assert s.score_coordinate(d,d['plan'][2],[rows[2]])['strict_correct_assignments'] is None
