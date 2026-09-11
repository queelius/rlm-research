import asyncio
import importlib
import json
import sys
import time
from pathlib import Path
from types import SimpleNamespace
import pytest

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))


def test_selection_is_label_independent_and_excludes_whole_conflict():
    s=importlib.import_module('study')
    rows=[{'index':i,'text':f'text {i}','label':i%2} for i in range(12)]
    rows.extend([{'index':12,'text':'Conflict','label':0},{'index':13,'text':' CONFLICT ','label':1}])
    excluded={s.group('text 2')}
    selected,_=s.choose(rows,excluded,'sst2',5)
    relabeled=[{**r,'label':1-r['label']} for r in rows]
    other,_=s.choose(relabeled,excluded,'sst2',5)
    assert [r['group_id'] for r in selected]==[r['group_id'] for r in other]
    assert not {s.group('text 2'),s.group('Conflict')}&{r['group_id'] for r in selected}
    assert len(selected)==5


def test_grid96_exact_source_pairs_and_strict_scoring():
    s=importlib.import_module('study');d=s.build_design(s.build_data())
    assert len(d['plan'])==96 and len({r['id'] for r in d['plan']})==96
    assert len(d['contexts'])==8 and {c['dataset'] for c in d['contexts']}=={'sst2','agnews'}
    for model in s.MODELS:
        rows=[r for r in d['plan'] if r['model']==model]
        assert len(rows)==48
        for context in range(8):
            calls=[s.make_request(d,r) for r in rows if r['context_index']==context]
            assert len(calls)==6
            assert len({b['messages'][1]['content'].split(s.INPUT_MARKER)[1] for b in calls})==1
    r=next(r for r in d['plan'] if r['arm']=='matching');gold=d['batches'][r['batch_id']]['gold']
    sample=s.synthetic(gold,gold['labels'][0]);assert s.score_labels(s.serialize(sample),gold)['schema_valid']
    sample[0]['tag']='q0001';assert not s.score_labels(s.serialize(sample),gold)['schema_valid']


def test_owned_actual_two_stages_caps(tmp_path,monkeypatch):
    import study as s
    m=s.private('owned.py',{'2400':('1650',1),'2640':('1770',2),'time.time()+900':('time.time()+600',1),'argv,930':('argv,630',1)},extra={'service':s.private('service.py')})
    monkeypatch.setattr(s,'ROOT',tmp_path);monkeypatch.setattr(s,'sha',lambda p:'fixture')
    deadlines=[];commands=[];releases=[];start=time.time()
    suite=SimpleNamespace(start_service=lambda stage,binding,deadline:deadlines.append(deadline),
      command=lambda stage,label,argv,cap,deadline:commands.append((argv,cap,deadline)),release_service=lambda stage:releases.append(stage))
    result=m.execute(tmp_path/'owned/attempt-001',suite,start)
    assert result['complete'] and len(commands)==len(releases)==2
    assert all(cap==630 and deadline<=start+1650 for _,cap,deadline in commands)
    assert all(float(argv[argv.index('--deadline')+1])<=time.time()+600 for argv,_,_ in commands)
    attempt=s.read(tmp_path/'owned/attempt-001/ATTEMPT.json')
    assert attempt['work_deadline_epoch']==start+1650 and attempt['owned_deadline_epoch']==start+1770


def test_actual_driver48_wire_and_terminal_cardinality(tmp_path,monkeypatch):
    import study as s
    import httpx
    service=s.private('service.py')
    m=s.private('driver.py',{'planned=72':('planned=48',1),'len(records)==72':('len(records)==48',1)},extra={'service':service})
    data=s.build_data();d=s.build_design(data);requests={r['id']:s.make_request(d,r) for r in d['plan']}
    rendered={r['id']:{'typed_token_ids_sha256':s.digest([100])} for r in d['plan']};d['rendered_prompts']=rendered
    spec={'design':d,'requests':requests,'request_sha256':{k:s.digest(v) for k,v in requests.items()},'source_sha256':{},'weight_stat_identity':{}}
    spec['spec_id']=s.digest(spec)
    monkeypatch.setattr(s,'ROOT',tmp_path)
    for name,value in [('DATA.json',data),('SPEC.json',spec),('CPU_QUALIFICATION.json',{'rendered_prompts':rendered})]:s.write_once(tmp_path/name,value)
    model=s.MODELS['qwen3'];endpoint=service.descriptor(model,tmp_path)
    s.write_once(tmp_path/'endpoint.json',endpoint);monkeypatch.setenv(endpoint['api_key_env'],'synthetic-fixture-not-secret')
    by={s.digest(body):r for r in d['plan'] for body in [requests[r['id']]]};calls=[]
    async def handler(request):
        if request.url.path=='/version':return httpx.Response(200,json={'version':'0.28.0'})
        if request.url.path=='/v1/models':return httpx.Response(200,json={'data':[{'id':model['alias'],'root':model['path'],'parent':None}]})
        body=json.loads(request.content);row=by[s.digest(body)];calls.append(row['id']);gold=d['batches'][row['batch_id']]['gold']
        return httpx.Response(200,json={'model':body['model'],'prompt_token_ids':[100],
          'choices':[{'message':{'content':s.serialize(s.synthetic(gold,gold['labels'][0]))},'finish_reason':'stop','token_ids':[101]}],
          'usage':{'prompt_tokens':1,'completion_tokens':1,'prompt_tokens_details':{'cached_tokens':0}}})
    original=httpx.AsyncClient
    monkeypatch.setattr(httpx,'AsyncClient',lambda **kwargs:original(transport=httpx.MockTransport(handler),**kwargs))
    output=tmp_path/'outputs/qwen3'
    assert asyncio.run(m.run('qwen3',tmp_path/'endpoint.json',output,time.time()+30))==0
    status=s.read(output/'STATUS.json')
    assert status['planned']==48 and status['recorded']==48 and status['stop_reason'] is None
    assert len(calls)==len(set(calls))==len(list((output/'wire').glob('*.json')))==48
