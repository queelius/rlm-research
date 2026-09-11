import asyncio
import json
import time
from pathlib import Path
import httpx

def test_interrupted_harvest_keeps_result_and_late_response(tmp_path):
    import bg_collect as c
    import bg_study as s
    plan=[dict(id='a',ids=['x'],n=1),dict(id='b',ids=['y'],n=1)]
    s.write(tmp_path/'calls/a/RESULT.json',dict(coordinate=plan[0],score=dict(available=True,strict_correct=1)))
    s.write(tmp_path/'calls/a/REQUEST.json',dict(dispatch_epoch=1))
    s.write(tmp_path/'calls/a/RESPONSE.json',dict(status=200,raw=dict(usage=dict(prompt_tokens=3,completion_tokens=2))))
    s.write(tmp_path/'calls/b/REQUEST.json',dict(dispatch_epoch=2))
    s.write(tmp_path/'calls/b/RESPONSE.json',dict(status=400,raw={'error':'cap'}))
    result=c.harvest(tmp_path,plan)
    assert len(result['rows'])==2 and result['rows'][0]['score']['strict_correct']==1
    assert result['rows'][1]['score']['strict_correct'] is None
    assert result['cost']['attempted']==2 and result['cost']['unknown_usage']['output']==1

def test_actual_four_worker_native_dispatch(tmp_path,monkeypatch):
    import bg_collect as c
    import bg_study as s
    import bg_protocol as p
    monkeypatch.setenv('BATCH_CPU_KEY','fixture')
    plan=[dict(id=str(i),context_id='x',ids=['a'],n=1,arm='S',repeat=0,seed=1,batch=i) for i in range(8)]
    bodies={str(i):{'model':'child','token_ids':[1],'sampling_params':{'seed':1}} for i in range(8)}
    monkeypatch.setattr(s,'verify',lambda:{'identity':'CPU'})
    original=s.read
    def read(path):
        if Path(path).name=='PLAN.json':return plan
        if Path(path).name=='REQUESTS.json':return bodies
        if Path(path).name=='HOST_GOLD.json':return {'x':{'labels':{'a':'location'}}}
        return original(path)
    monkeypatch.setattr(s,'read',read)
    from types import SimpleNamespace
    monkeypatch.setattr(s,'renderer',lambda:(SimpleNamespace(parse_response=lambda ids:SimpleNamespace(content='{"a":"location"}',tool_calls=[])),None))
    endpoint=tmp_path/'endpoint.json';s.write(endpoint,dict(host='fixture.invalid',port=1,api_key_env='BATCH_CPU_KEY'))
    active=0;maximum=0
    async def response(request):
        nonlocal active,maximum
        active+=1;maximum=max(maximum,active);await asyncio.sleep(.01);active-=1
        assert request.url.path=='/inference/v1/generate'
        return httpx.Response(200,json={'model':'child','request_id':request.headers['x-science-call'],'choices':[{'token_ids':[2],'logprobs':{'content':[{'logprob':-.1}]},'finish_reason':'stop'}],'usage':{'prompt_tokens':1,'completion_tokens':1}})
    result=asyncio.run(c.run(endpoint,tmp_path/'rollout',time.time()+60,transport=httpx.MockTransport(response)))
    assert maximum==4 and result['cost']['attempted']==8
    assert all(r['score']['strict_correct']==1 for r in result['rows'])

def test_host_aggregate_is_diagnostic_and_null_until_full():
    import bg_collect as c
    context='scale-state-02-256';records=[dict(id='a',weight=3),dict(id='b',weight=2)]
    gold={context:{'labels':{'a':'location','b':'entity'}}};public={context:{'records':records}}
    row=dict(coordinate=dict(context_id=context,repeat=0,arm='W',n=2),score=dict(strict_correct=1,available=True,complete_map=True,labels={'a':'entity','b':'entity'},canonical_id_matches=2))
    result=c.summarize([row],gold,public)[0]
    assert result['host_target_scalar']==0 and result['host_target_gold']==3 and result['host_target_error']==-3
