import asyncio
import json
from collections import Counter, defaultdict
from copy import deepcopy

import httpx
import pytest

def study():
    import study as s
    return s

def test_complete_williams_units_and_source_coverage():
    s=study();d=s.build_design(s.build_data())
    assert len(d['plan'])==96 and len(d['contexts'])==12
    assert {r['seed'] for r in d['plan']}=={981304011,981304021}
    for task in ('trec','sst2','agnews'):
        rows=[r for r in d['plan'] if r['dataset']==task]
        assert Counter(r['condition'] for r in rows)==dict(A=8,B=8,C=8,D=8)
        for index in range(4):
            assert Counter(r['condition'] for r in rows if r['cell_order']==index)==dict(A=2,B=2,C=2,D=2)
    for group in s.dispatch_units(d):
        assert len(group)==4 and {r['condition'] for r in group}==set('ABCD')
        assert len({(r['context_index'],r['seed']) for r in group})==1
    with pytest.raises(ValueError):s.dispatch_units({**d,'plan':d['plan'][:-1]})

def test_order_pairs_have_identical_prompts_but_opposite_wire_schema():
    s=study();d=s.build_design(s.build_data())
    for group in s.dispatch_units(d):
        by={r['condition']:r for r in group}
        for a,b in [('A','C'),('B','D')]:
            x,y=[s.make_request(d,by[k]) for k in (a,b)]
            assert x['messages']==y['messages'] and x['tools']==y['tools']
            assert 'keys tag and label' in x['messages'][1]['content']
            assert 'keys tag then label' not in x['messages'][1]['content']
            assert list(x['structured_outputs']['json']['prefixItems'][0]['properties'])==['tag','label']
            assert list(y['structured_outputs']['json']['prefixItems'][0]['properties'])==['label','tag']
            assert s.ordered_digest(x)!=s.ordered_digest(y)
        bodies=[s.make_request(d,r) for r in group]
        assert len({b['messages'][1]['content'].split(s.INPUT_MARKER)[1] for b in bodies})==1

def test_gold_changes_never_reach_request():
    s=study();d=s.build_design(s.build_data());r=d['plan'][0];before=s.serialize(s.make_request(d,r))
    for item in d['batches'][r['batch_id']]['gold']['records']:item['gold_label']='PRIVATE_GOLD'
    assert s.serialize(s.make_request(d,r))==before

@pytest.mark.parametrize('order',['tag_first','label_first'])
def test_whole_order_schema_is_strict_including_late_bad_tag(order):
    s=study();d=s.build_design(s.build_data());r=next(r for r in d['plan'] if r['field_order']==order)
    gold=d['batches'][r['batch_id']]['gold'];good=s.synthetic_output(gold,gold['labels'][0])
    assert s.score_labels(s.serialize(good),gold)['schema_valid']
    bad=deepcopy(good);bad[60]['tag']='q999999'
    score=s.score_labels(s.serialize(bad),gold)
    assert not score['schema_valid'] and not score['assigned_order_conformant'] and score['strict_correct']==0
    bad=deepcopy(good);bad[0]=dict(reversed(list(bad[0].items())))
    assert not s.score_labels(s.serialize(bad),gold)['schema_valid']
    for bad in [good[:-1],good+[good[-1]],[{'label':'bad'}]+good[1:]]:
        assert not s.score_labels(s.serialize(bad),gold)['schema_valid']
    text=s.serialize(good).replace('"tag":','"tag":"duplicate","tag":',1)
    assert not s.score_labels(text,gold)['schema_valid']
    bad=deepcopy(good);bad[1]={'label':gold['labels'][0]}
    assert not s.score_labels(s.serialize(bad),gold)['schema_valid']

def test_primary_positive_shift_and_null_are_distinct():
    s=study()
    values={'A':[1,.25,0,0],'B':[.25,.25,0,0],'C':[.25,1,0,0],'D':[.25,.25,0,0]}
    assert s.shift_interaction(values)==1.5
    values['C']=None
    assert s.shift_interaction(values) is None

def test_raw_projection_computes_assigned_quadruple_and_keeps_unrun_null():
    s=study();d=s.build_design(s.build_data());calls=[]
    for row in s.dispatch_units(d)[0]:
        gold=d['batches'][row['batch_id']]['gold'];values=s.synthetic_output(gold,gold['labels'][0])
        for i,record in enumerate(gold['records']):
            correct=(row['condition']=='A' and i%4==0) or (row['condition']=='C' and i%4==1)
            label=record['gold_label'] if correct else next(x for x in gold['labels'] if x!=record['gold_label'])
            if isinstance(values[i],dict):values[i]['label']=label
            else:values[i]=label
        calls.append(dict(coordinate=row,score={'untrusted_stored_score':True},model_called=True,started=0,ended=1,
            raw_response={'choices':[{'message':{'content':s.serialize(values)}}]}))
    result=s.summarize(d,calls)
    observed=[x for x in result['quadruples'] if x['strict_positive_shift_interaction'] is not None]
    assert len(observed)==1 and observed[0]['strict_positive_shift_interaction']==2
    assert sum(x['null_calls'] for x in result['cells'])==92
    assert all(x['strict_equal_context_mean'] is None for x in result['task_primary'])

def test_actual_dispatch_is_sequential_quadruples_not_individual_rows(tmp_path):
    s=study();d=s.build_design(s.build_data())
    req={r['id']:s.make_request(d,r) for r in d['plan']}
    spec={'design':d,'requests':req,'request_sha256':{k:s.digest(v) for k,v in req.items()}}
    lookup={s.ordered_digest(req[r['id']]):r for r in d['plan']}
    byworker=defaultdict(list);active=set();seen=[];max_active=0
    async def response(request):
        nonlocal max_active
        row=lookup[s.ordered_digest(json.loads(request.content))]
        unit=(row['context_index'],row['seed'])
        assert unit not in active
        active.add(unit);max_active=max(max_active,len(active))
        byworker[id(asyncio.current_task())].append(row['id']);seen.append(row['id'])
        await asyncio.sleep(.001)
        active.remove(unit)
        gold=d['batches'][row['batch_id']]['gold']
        return httpx.Response(200,json={'model':s.ALIAS,'prompt_token_ids':[101,102],
            'choices':[{'message':{'role':'assistant','content':s.serialize(s.synthetic_output(gold,gold['labels'][0]))},'finish_reason':'stop','token_ids':[103]}],
            'usage':{'prompt_tokens':2,'completion_tokens':1,'prompt_tokens_details':{'cached_tokens':0}}})
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(response)) as client:
            return await s.collect_calls(client,'http://fixture/v1',spec,tmp_path)
    rows,reason=asyncio.run(run())
    assert reason is None and len(rows)==len(set(seen))==96 and max_active==4
    expected={tuple(r['id'] for r in group) for group in s.dispatch_units(d)}
    actual={tuple(ids[i:i+4]) for ids in byworker.values() for i in range(0,len(ids),4)}
    assert actual==expected and len(byworker)==4

def test_unavailable_and_observed_empty_not_repaired():
    s=study();d=s.build_design(s.build_data());row=d['plan'][0]
    assert s.score_coordinate(d,row,[])['strict_correct_assignments'] is None
    assert s.score_labels('',d['batches'][0]['gold'])['strict_correct']==0

def test_deadline_awaits_all_inflight_final_records(tmp_path):
    import time
    s=study();d=s.build_design(s.build_data())
    req={r['id']:s.make_request(d,r) for r in d['plan']}
    spec={'design':d,'requests':req,'request_sha256':{k:s.digest(v) for k,v in req.items()}}
    async def response(request):
        await asyncio.sleep(10)
        raise AssertionError('deadline must cancel')
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(response)) as client:
            rows,reason=await s.collect_calls(client,'http://fixture/v1',spec,tmp_path,time.monotonic()+.03)
            assert reason=='wall_time_cap' and len(rows)==4
            before={p.name for p in (tmp_path/'calls').glob('*.json')}
            assert len(before)==4 and all(r['error']['type']=='CancelledError' for r in rows)
            await asyncio.sleep(.01)
            assert {p.name for p in (tmp_path/'calls').glob('*.json')}==before
    asyncio.run(run())
