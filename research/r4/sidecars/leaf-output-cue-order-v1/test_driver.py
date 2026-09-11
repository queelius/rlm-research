import asyncio
import json
import time
from copy import deepcopy
from pathlib import Path
import httpx
import pytest


def modules():
    assert (Path(__file__).parent/'driver.py').exists(), 'ordered-wire driver absent'
    import driver
    return driver,driver.s


def test_wire_rejects_reordered_properties_even_if_dict_equality_unchanged(tmp_path):
    driver,s=modules();d=s.build_design(s.build_data());row=d['plan'][0]
    body=s.make_request(d,row)
    spec={'requests':{row['id']:body},'ordered_request_sha256':{row['id']:s.ordered_digest(body)}}
    hook=driver.wire_hook(spec,tmp_path)
    changed=deepcopy(body);props=changed['structured_outputs']['json']['prefixItems'][0]['properties']
    changed['structured_outputs']['json']['prefixItems'][0]['properties']=dict(reversed(list(props.items())))
    assert changed==body and s.digest(changed)==s.digest(body)
    with pytest.raises(ValueError):
        asyncio.run(hook(httpx.Request('POST','http://fake/v1/chat/completions',content=s.serialize(changed))))
    assert not list(tmp_path.rglob('*.json'))
    asyncio.run(hook(httpx.Request('POST','http://fake/v1/chat/completions',content=s.serialize(body))))
    saved=s.read(tmp_path/'wire'/f"{row['id']}.json")
    assert saved['body_utf8']==s.serialize(body) and saved['body_sha256']==s.ordered_digest(body)


def test_actual_collector_keeps_both_orders_and_first_failure_null(tmp_path):
    driver,s=modules();d=s.build_design(s.build_data());d['plan']=d['coordinates']=d['plan'][:6]
    requests={r['id']:s.make_request(d,r) for r in d['plan']}
    spec={'design':d,'requests':requests,'request_sha256':{k:s.digest(v) for k,v in requests.items()},
          'ordered_request_sha256':{k:s.ordered_digest(v) for k,v in requests.items()}}
    seen=[];fail=False
    async def provider(request):
        body=json.loads(request.content);row=next(r for r in d['plan'] if s.ordered_digest(requests[r['id']])==s.ordered_digest(body))
        seen.append(row['id'])
        if fail: return httpx.Response(500,json={'error':'operator fixture unavailable'})
        gold=d['batches'][row['batch_id']]['gold'];values=[]
        for r,tag in zip(gold['records'],s.expected_tags(gold['records'],row['arm'],'q'),strict=True):
            v={'tag':tag,'label':r['gold_label']};values.append({k:v[k] for k in s.ORDERS[row['field_order']]})
        return httpx.Response(200,json={'model':body['model'],'prompt_token_ids':[1],
            'choices':[{'message':{'content':s.serialize(values)},'finish_reason':'stop','token_ids':[2]}],
            'usage':{'prompt_tokens':1,'completion_tokens':1}})
    async def collect(output):
        async with httpx.AsyncClient(transport=httpx.MockTransport(provider),event_hooks={'request':[driver.wire_hook(spec,output)]}) as client:
            return await s.collect_calls(client,'http://fake/v1',spec,output,time.monotonic()+10)
    records,reason=asyncio.run(collect(tmp_path))
    assert reason is None and len(records)==len(seen)==6
    assert all(r['score']['strict_correct']==64 for r in records)
    assert {r['score']['assigned_field_order'] for r in records}=={'tag_first','label_first'}
    assert len(list((tmp_path/'wire').glob('*.json')))==6
    fail=True;seen.clear();records,reason=asyncio.run(collect(tmp_path/'failure'))
    assert reason=='request_error' and len(records)==len(seen)==1 and records[0]['score'] is None
    assert s.score_coordinate(d,records[0]['coordinate'],records)['strict_correct_assignments'] is None


def test_source_mutation_rejected_before_request_or_model(tmp_path):
    driver,s=modules();path=tmp_path/'source.json';s.write_once(path,{'x':1})
    spec={'source_sha256':{str(path):'0'*64}};spec['spec_id']=s.digest(spec)
    with pytest.raises(ValueError): driver.verify(spec)
