import asyncio
import json
from collections import Counter,defaultdict
from copy import deepcopy
import httpx
import pytest

def study():
    import study as s
    return s

def test_complete_balanced_eight_call_units():
    s=study();d=s.build_design(s.build_data());assert len(d['plan'])==192
    assert {r['seed'] for r in d['plan']}=={981310011,981310021}
    assert len(s.dispatch_units(d))==24
    for task in ('trec','sst2','agnews'):
        rows=[r for r in d['plan'] if r['dataset']==task]
        for position in range(8):assert Counter(r['condition'] for r in rows if r['cell_order']==position)==dict.fromkeys('ABCDEFGH',1)
    with pytest.raises(ValueError):s.dispatch_units({**d,'plan':d['plan'][:-1]})

def test_phase_same_record_bijection_and_no_circular_predecessor():
    s=study()
    assert s.distance(0,3) is None and s.distance(2,3) is None
    assert [s.distance(3,p) for p in range(4)]==[3,2,1,0]
    for i in range(3,64):assert sorted(s.distance(i,p) for p in range(4))==[0,1,2,3]
    for p in range(4):assert sum(s.is_anchor(i,p) for i in range(64))==16

def test_only_schema_changes_and_gold_never_reaches_prompt():
    s=study();d=s.build_design(s.build_data())
    for group in s.dispatch_units(d):
        bodies=[s.make_request(d,r) for r in group]
        common=[{k:v for k,v in b.items() if k!='structured_outputs'} for b in bodies]
        assert all(x==common[0] for x in common)
        assert len({s.ordered_digest(b['structured_outputs']) for b in bodies})==8
        for row,body in zip(group,bodies):
            types=[i['type'] for i in body['structured_outputs']['json']['prefixItems']]
            assert Counter(types)=={'object':16,'string':48}
            assert [i for i,x in enumerate(types) if x=='object']==list(range(row['phase'],64,4))
    row=d['plan'][0];before=s.serialize(s.make_request(d,row))
    for r in d['contexts'][row['context_index']]['records']:r['gold_label']='PRIVATE'
    assert s.serialize(s.make_request(d,row))==before

@pytest.mark.parametrize('phase',range(4))
def test_strict_phase_schema_and_late_errors(phase):
    s=study();d=s.build_design(s.build_data());r=next(r for r in d['plan'] if r['phase']==phase)
    gold=d['batches'][r['batch_id']]['gold'];good=s.synthetic_output(gold,gold['labels'][0]);assert s.score_labels(s.serialize(good),gold)['schema_valid']
    for kind in ('tag','order','nonanchor','short','duplicate'):
        bad=deepcopy(good)
        if kind=='tag':bad[60+phase]['tag']='q99999'
        if kind=='order':bad[phase]=dict(reversed(list(bad[phase].items())))
        if kind=='nonanchor':bad[(phase+1)%4]={'tag':'p0000','label':gold['labels'][0]}
        if kind=='short':bad=bad[:-1]
        text=s.serialize(bad)
        if kind=='duplicate':text=text.replace('"tag":','"tag":"duplicate","tag":',1)
        result=s.score_labels(text,gold);assert not result['schema_valid'] and result['strict_correct']==0

def test_primary_same_record_and_missing_block():
    s=study()
    values={(p,a):[int(a=='matching' and i%4==p) for i in range(64)] for p in range(4) for a in ('matching','constant')}
    primary,profile=s.block_primary(values);assert primary==1 and profile==[1,0,0,0]
    values[(1,'constant')]=None;assert s.block_primary(values)==(None,None)

def test_raw_projection_retains_all_nulls_and_completed_invalid_zero():
    s=study();d=s.build_design(s.build_data());calls=[]
    for row in s.dispatch_units(d)[0]:
        gold=d['batches'][row['batch_id']]['gold'];values=s.synthetic_output(gold,gold['labels'][0])
        for i,record in enumerate(gold['records']):
            correct=row['arm']=='matching' and i%4==row['phase']
            label=record['gold_label'] if correct else next(x for x in gold['labels'] if x!=record['gold_label'])
            if isinstance(values[i],dict):values[i]['label']=label
            else:values[i]=label
        calls.append({'coordinate':row,'score':{'untrusted':True},'model_called':True,'started':0,'ended':1,'raw_response':{'choices':[{'message':{'content':s.serialize(values)}}]}})
    result=s.summarize(d,calls);complete=[r for r in result['blocks'] if r['primary'] is not None]
    assert len(complete)==1 and complete[0]['primary']==1
    assert sum(r['null_calls'] for r in result['cells'])==184
    assert all(r['equal_context_mean'] is None for r in result['task_primary'])
    assert s.score_labels('',d['batches'][0]['gold'])['strict_correct']==0

def test_actual_eight_call_dispatch_and_cancel_settlement(tmp_path):
    import time
    s=study();d=s.build_design(s.build_data());req={r['id']:s.make_request(d,r) for r in d['plan']}
    frozen={'design':d,'requests':req,'request_sha256':{k:s.digest(v) for k,v in req.items()}}
    lookup={s.ordered_digest(req[r['id']]):r for r in d['plan']};byworker=defaultdict(list);active=set();peak=0
    async def response(request):
        nonlocal peak
        row=lookup[s.ordered_digest(json.loads(request.content))];unit=row['unit_index'];assert unit not in active
        active.add(unit);peak=max(peak,len(active));byworker[id(asyncio.current_task())].append(row['id'])
        await asyncio.sleep(.001);active.remove(unit);gold=d['batches'][row['batch_id']]['gold']
        return httpx.Response(200,json={'model':s.ALIAS,'prompt_token_ids':[101,102],'choices':[{'message':{'role':'assistant','content':s.serialize(s.synthetic_output(gold,gold['labels'][0]))},'finish_reason':'stop','token_ids':[103]}],'usage':{'prompt_tokens':2,'completion_tokens':1,'prompt_tokens_details':{'cached_tokens':0}}})
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(response)) as client:return await s.collect_calls(client,'http://fixture/v1',frozen,tmp_path/'complete')
    rows,reason=asyncio.run(run());assert reason is None and len(rows)==192 and peak==4
    expected={tuple(r['id'] for r in group) for group in s.dispatch_units(d)}
    actual={tuple(ids[i:i+8]) for ids in byworker.values() for i in range(0,len(ids),8)};assert actual==expected
    async def slow(request):await asyncio.sleep(10)
    async def cancel():
        async with httpx.AsyncClient(transport=httpx.MockTransport(slow)) as client:
            rows,reason=await s.collect_calls(client,'http://fixture/v1',frozen,tmp_path/'cancel',time.monotonic()+.03)
            assert reason=='wall_time_cap' and len(rows)==4 and all(r['error']['type']=='CancelledError' for r in rows)
            before=list((tmp_path/'cancel/calls').glob('*.json'));assert len(before)==4
            await asyncio.sleep(.01);assert len(list((tmp_path/'cancel/calls').glob('*.json')))==4
    asyncio.run(cancel())
