import asyncio
import json
from pathlib import Path
from types import SimpleNamespace
import httpx
import pytest
import study as s


def test_owned_dual_alias_binding_and_work_clock():
    assert (Path(__file__).parent/'owned.py').exists(), 'dual alias owned wrapper absent'
    import owned
    weights={'models':{name:{'path':'/'+name,'model_sha256':name,'config_sha256':'cfg'} for name in s.ALIASES}}
    bound=owned.service_binding(weights,Path('/weights'),'weightsha')
    assert set(bound['models'])==set(s.ALIASES.values())
    assert bound['role_map']['root']==s.ALIASES['original']
    assert owned.work_deadline(1000)==2080 and owned.collection_command_cap(1000,1001)==930
    with pytest.raises(TimeoutError): owned.collection_command_cap(1000,2080)


def test_actual_collector_preserves_twelve_weight_cells_wire_and_one_null(tmp_path):
    import driver
    design=s.build_design(s.build_data());design['plan']=design['coordinates']=design['plan'][:12]
    requests={r['id']:s.make_request(design,r) for r in design['plan']}
    spec={'design':design,'requests':requests,'request_sha256':{k:s.digest(v) for k,v in requests.items()}}
    seen=[];fail=False
    async def provider(request):
        body=json.loads(request.content);row=next(r for r in design['plan'] if requests[r['id']]==body)
        seen.append(row['id'])
        if fail: return httpx.Response(500,json={'error':'operator fixture unavailable'})
        gold=design['batches'][row['batch_id']]['gold']
        content=json.dumps([{'tag':tag,'label':r['gold_label']} for tag,r in zip(s.expected_tags(gold['records'],row['arm'],row['source_prefix']),gold['records'],strict=True)])
        return httpx.Response(200,json={'model':body['model'],'prompt_token_ids':[1],
            'choices':[{'message':{'content':content},'finish_reason':'stop','token_ids':[2]}],
            'usage':{'prompt_tokens':1,'completion_tokens':1}})
    async def run(output):
        async with httpx.AsyncClient(transport=httpx.MockTransport(provider),event_hooks={'request':[driver.wire_hook(spec,output)]}) as client:
            return await s.collect_calls(client,'http://fake/v1',spec,output)
    records,reason=asyncio.run(run(tmp_path))
    assert len(seen)==len(set(seen))==len(records)==12 and reason is None
    assert len(list((tmp_path/'wire').glob('*.json')))==12
    assert sum(r.get('score') is None for r in records)==0
    assert all(r['score']['strict_correct']==64 for r in records if r.get('score'))
    summary=s.summarize(design,records)
    assert len(summary['cells'])==12 and len(summary['weight_interactions'])==2
    assert sum(c['strict_correct_assignments'] is None for c in summary['coordinates'])==0
    for path in (tmp_path/'wire').glob('*.json'):
        value=s.read(path);assert value['body_utf8']==s.serialize(requests[value['coordinate_id']])
    fail=True;seen.clear()
    failed,reason=asyncio.run(run(tmp_path/'failure'))
    assert reason=='request_error' and len(failed)==len(seen)==1
    assert failed[0]['score'] is None
    assert s.score_coordinate(design,failed[0]['coordinate'],failed)['strict_correct_assignments'] is None


def test_source_mutation_rejected_before_data_or_model_execution(tmp_path):
    import driver
    source=tmp_path/'frozen.json';s.write_once(source,{'x':1})
    spec={'source_sha256':{str(source):'0'*64}}
    spec['spec_id']=s.digest(spec)
    with pytest.raises(ValueError): driver.verify(spec)
