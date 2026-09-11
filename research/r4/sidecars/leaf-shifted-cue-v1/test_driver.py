import asyncio
import json
import time
from copy import deepcopy
from pathlib import Path
import httpx
import pytest

def modules():
    assert (Path(__file__).parent/'driver.py').exists(),'driver missing'
    import driver
    return driver,driver.s

def test_wire_order_is_physical_not_sorted_dict_identity(tmp_path):
    driver,s=modules();d=s.build_design(s.build_data());row=d['plan'][0];body=s.make_request(d,row)
    spec={'requests':{row['id']:body},'ordered_request_sha256':{row['id']:s.ordered_digest(body)}}
    hook=driver.wire_hook(spec,tmp_path);wrong=deepcopy(body)
    properties=wrong['structured_outputs']['json']['prefixItems'][0]['properties']
    wrong['structured_outputs']['json']['prefixItems'][0]['properties']=dict(reversed(list(properties.items())))
    assert wrong==body
    with pytest.raises(ValueError):asyncio.run(hook(httpx.Request('POST','http://fake/v1/chat/completions',content=s.serialize(wrong))))
    asyncio.run(hook(httpx.Request('POST','http://fake/v1/chat/completions',content=s.serialize(body))))
    assert s.read(tmp_path/'wire'/(row['id']+'.json'))['body_utf8']==s.serialize(body)

def test_actual_run72_cardinality_captures_all_calls_and_no_inherited96(tmp_path,monkeypatch):
    driver,s=modules();d=s.build_design(s.build_data());requests={r['id']:s.make_request(d,r) for r in d['plan']}
    d['rendered_prompts']={r['id']:{'tokens':1,'typed_token_ids_sha256':s.digest([1])} for r in d['plan']}
    spec={'design':d,'requests':requests,'request_sha256':{k:s.digest(v) for k,v in requests.items()},
          'ordered_request_sha256':{k:s.ordered_digest(v) for k,v in requests.items()},'weight':{}}
    s.write_once(tmp_path/'SPEC.json',spec)
    endpoint={'host':'fake','port':80,'model_alias':s.ALIAS,'api_key_env':'SHIFTED_TEST_ONLY_KEY'}
    s.write_once(tmp_path/'endpoint.json',endpoint)
    monkeypatch.setenv('SHIFTED_TEST_ONLY_KEY','not-a-real-secret')
    monkeypatch.setattr(driver,'ROOT',tmp_path);monkeypatch.setattr(driver,'verify',lambda spec:None)
    monkeypatch.setattr(driver.qualified_http,'validate_descriptor',lambda *args:None)
    monkeypatch.setattr(driver.qualified_http,'validate_live_models',lambda *args:None)
    seen=[];real_client=httpx.AsyncClient
    async def provider(request):
        if request.method=='GET':return httpx.Response(200,json={'version':'0.28.0','data':[]})
        body=json.loads(request.content);row=next(r for r in d['plan'] if s.ordered_digest(requests[r['id']])==s.ordered_digest(body));seen.append(row['id'])
        gold=d['batches'][row['batch_id']]['gold'];values=[{'tag':tag,'label':r['gold_label']} for r,tag in zip(gold['records'],s.tags(gold['records'],row['arm']))]
        return httpx.Response(200,json={'model':s.ALIAS,'prompt_token_ids':[1],
            'choices':[{'message':{'content':s.serialize(values)},'finish_reason':'stop','token_ids':[2]}],
            'usage':{'prompt_tokens':1,'completion_tokens':1}})
    monkeypatch.setattr(driver.httpx,'AsyncClient',lambda **kwargs:real_client(transport=httpx.MockTransport(provider),**kwargs))
    output=tmp_path/'outputs/fixture'
    result=asyncio.run(driver.run(tmp_path/'endpoint.json',output,time.time()))
    status=s.read(output/'STATUS.json')
    assert result==0 and status['planned']==status['recorded']==72 and not status['unrun']
    assert len(seen)==len(list((output/'wire').glob('*.json')))==72
    projection=s.read(output/'analysis.json')
    assert all(c['strict_correct_assignments']==64 for c in projection['coordinates'])

def test_source_mutation_rejected_before_model(tmp_path):
    driver,s=modules();p=tmp_path/'source.json';s.write_once(p,{'x':1})
    spec={'source_sha256':{str(p):'0'*64}};spec['spec_id']=s.digest(spec)
    with pytest.raises(ValueError):driver.verify(spec)
