"""Actual composed owner launch interception and authored native metadata uptake."""
import asyncio
import importlib.util
import json
import os
from pathlib import Path
import runpy
import sys
import time
import types
from unittest.mock import patch

def test_actual_owner_service_entry(tmp_path):
    import ts_study as s
    import ts_owner as o
    class InterceptedLaunch(BaseException):pass
    spawned=[];original_spec=importlib.util.spec_from_file_location
    def instrument(name,path,*a,**kw):
        spec=original_spec(name,path,*a,**kw)
        if name=='dual_lora_owned_launcher':
            execute=spec.loader.exec_module
            def load(m):
                execute(m);m._port_free=lambda p:True;m._wait_endpoint_model=lambda *a,**k:None;m._load_adapter=lambda d:None;m._stop=lambda p:None
            spec.loader.exec_module=load
        return spec
    output=tmp_path/'attempt';stage=output/'service-sft24'
    with patch.dict(os.environ,{'STRICT_RLM_CALIBRATION_API_KEY':'CPU_FIXTURE_NOT_CREDENTIAL'}):suite=o.dependencies()
    def popen(argv,**kwargs):
        spawned.append(argv)
        if len(spawned)==1:
            assert len(s.read(output/'PLANNED_EVALUATION.json')['full'])==72
            assert Path(argv[1]).name=='service_wrapper_v2.py';previous=list(sys.path)
            try:
                with patch.object(sys,'argv',argv[1:]),patch('importlib.util.spec_from_file_location',side_effect=instrument):runpy.run_path(argv[1],run_name='__main__')
            finally:sys.path[:]=previous
            raise InterceptedLaunch()
        config=s.read(argv[2]);assert Path(argv[0]).name=='inference'
        assert config['vllm']['max_model_len']==8192 and config['vllm']['max_loras']==2
        return types.SimpleNamespace(pid=999999,returncode=0,poll=lambda:0)
    releases=[]
    with patch.dict(os.environ,{'CUDA_VISIBLE_DEVICES':'CPU_INTERCEPT_ONLY','STRICT_RLM_CALIBRATION_API_KEY':'CPU_FIXTURE_NOT_CREDENTIAL'}),patch.object(s,'ATTEMPT',output),patch.object(s,'verify',return_value={'identity':'CPU'}),patch.object(o,'dependencies',return_value=suite),patch.object(suite.life.v1,'ports_free',return_value=True),patch.object(suite.subprocess,'Popen',side_effect=popen),patch.object(suite,'release_service',side_effect=lambda p:releases.append(p)):
        result=o.execute(output)
    assert not result['complete'] and result['released'] and len(spawned)==2 and releases==[stage]
    endpoint=s.read(stage/'service/endpoint-original.json')
    assert endpoint['adapter']['model_sha256']==s.selected()['adapter_sha256'] and endpoint['role_binding_sha256']==s.sha(stage/'BINDING.json')
    run=s.read(output/'OWNER_RUN.json');assert run['work_deadline_epoch']-run['started_epoch']==3720 and run['owned_deadline_epoch']-run['started_epoch']==3870
    assert len(result['readout_inventory'])==72

def test_missing_result_and_partial_cost_union(tmp_path):
    import ts_study as s
    import ts_owner as o
    plan=s.read(s.ROOT/'inputs/EVALUATION_PLAN.json');rows=plan['full'];directory=tmp_path/'sft24/free'/rows[0]['coordinate']['id']
    s.write(directory/'RESULT.json',dict(available=True,reward=0))
    s.write(directory/'physical/0001.json',dict(physical_request_attempt=True,response={'choices':[{}],'usage':{'prompt_tokens':5,'completion_tokens':2}}))
    s.write(directory/'physical/0002.json',dict(physical_request_attempt=True,status=400,error='context length'))
    second=tmp_path/'sft24/free'/rows[1]['coordinate']['id'];s.write(second/'FAILURE.json',{'error':'interrupted'})
    inventory=o.harvest(tmp_path,plan);cost=o.ledger(tmp_path)['full_native']
    assert len(inventory)==72 and sum(r['available'] for r in inventory)==1 and inventory[0]['reward']==0 and inventory[1]['reward'] is None
    assert cost['physical_requests_attempted']==2 and cost['returned_native_completions']==1
    assert cost['usage']=={'known':{'input':5,'output':2,'cached':0},'unknown':{'input':1,'output':1,'cached':2}}

def test_native_metadata_file_child_observation_final(tmp_path,monkeypatch):
    import ts_study as s
    import ts_collect as c
    from aiohttp import web
    monkeypatch.setenv('STRICT_RLM_CALIBRATION_API_KEY','CPU_FIXTURE_NOT_CREDENTIAL');monkeypatch.setenv('TASK_SPEC_CPU_KEY','CPU_FIXTURE_NOT_CREDENTIAL')
    async def fixture():
        row=next(r for r in s.read(s.ROOT/'inputs/FREE_PLAN.json') if r['interface_arm']=='J' and r['operator']=='maximum_weight')
        context=next(x for x in s.read(s.ROOT/'inputs/PUBLIC.json') if x['id']==row['context_id']);binding=s.binding();tokenizer=s.stack().native.renderer()._tokenizer;roots=[];children=[]
        labels={r['id']:row['target'] if i<4 else ('entity' if row['target']!='entity' else 'human being') for i,r in enumerate(context['records'])}
        expected=max(sum(r['weight'] for r in context['records'][:4] if r['user']==u) for u in ('u0','u1','u2','u3'));assert expected>0
        code1='import json\nfrom rlm.api import run as rlm\nfrom batch_contract import request_for, strict_map\nspec=json.load(open("task.json"))\nprint(json.dumps(spec,sort_keys=True))\nrecords=json.load(open("records.json"))\nchild=await rlm(request_for(records))\nlabels=strict_map(child.answer,[r["id"] for r in records])\nprint(json.dumps(labels,sort_keys=True))'
        code2='assert spec["operator"]=="maximum_weight"\ntotals={u:sum(r["weight"] for r in records if r["user"]==u and labels[r["id"]]==spec["category_a"]) for u in {r["user"] for r in records}}\nprint(max(totals.values()))'
        async def provider(request):
            body=await request.json()
            if body['model']==binding['role_map']['root']:
                roots.append(body);assert body['sampling_params']['max_tokens']==2048
                if len(roots)==1:assert body['token_ids']==s.read(s.ROOT/'inputs/PROMPTS_ACCURATE.json')[row['id']]['token_ids']
                assert len(roots)<=3
                reply=s.stack().native.tool_action([code1,code2][len(roots)-1]) if len(roots)<3 else 'Answer: '+str(expected)
            else:
                assert body['model']==binding['fixed_child'];children.append(body);ids=body['sampling_params']['structured_outputs']['json']['required'];assert set(ids)==set(labels)
                reply=json.dumps({key:labels[key] for key in ids})
            ids=tokenizer.encode(reply,add_special_tokens=False)+[151645]
            return web.json_response(dict(request_id='TASK_SPEC_CPU_'+str(len(roots)+len(children)),usage=dict(prompt_tokens=len(body['token_ids']),completion_tokens=len(ids)),choices=[dict(token_ids=ids,finish_reason='stop',logprobs=dict(content=[dict(token=f'token_id:{v}',logprob=-.5) for v in ids]))]))
        async def models(request):return web.json_response(dict(data=[dict(id=a,root=v['path'],max_model_len=8192) for a,v in binding['models'].items()]))
        app=web.Application();app.router.add_post('/inference/v1/generate',provider);app.router.add_get('/v1/models',models);runner=web.AppRunner(app);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start()
        descriptor=dict(host='127.0.0.1',port=site._server.sockets[0].getsockname()[1],api_key_env='TASK_SPEC_CPU_KEY')
        try:
            await c.implementation().episode(row,context,binding,descriptor,tmp_path/'native',time.time()+120,'free')
            result=s.read(tmp_path/'native/RESULT.json');assert result['available'] and result['final_branch_token_identity_verified'] and result['reply']=='Answer: '+str(expected)
            trace=s.read(tmp_path/'native/EPISODE.json')['traces'][0];observations=[n['message'].get('content') for n in trace['nodes'] if n['message'].get('role')=='tool']
            assert any(json.dumps(s.task_protocol().spec(row),sort_keys=True) in (v or '') for v in observations)
            assert len(roots)==3 and len(children)==1
        finally:await runner.cleanup()
    asyncio.run(fixture())
