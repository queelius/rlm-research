"""Bounded authored native fixture and intercepted actual service entry, CPU only."""
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
    import ss_study as s
    import ss_owner as o
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
            assert len(s.read(output/'PLANNED_EVALUATION.json')['full'])==24
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
    assert len(result['readout_inventory'])==24

def test_missing_result_and_late_physical_never_erase_cost(tmp_path):
    import ss_study as s
    import ss_owner as o
    plan=s.read(s.ROOT/'inputs/EVALUATION_PLAN.json');rows=plan['full']
    directory=tmp_path/'sft24/free'/rows[0]['coordinate']['id']
    s.write(directory/'RESULT.json',dict(available=True,reward=0))
    s.write(directory/'physical/0001.json',dict(physical_request_attempt=True,response={'choices':[{}],'usage':{'prompt_tokens':5,'completion_tokens':2}}))
    s.write(directory/'physical/0002.json',dict(physical_request_attempt=True,status=400,error='context length'))
    second=tmp_path/'sft24/free'/rows[1]['coordinate']['id'];s.write(second/'FAILURE.json',{'error':'interrupted'})
    inventory=o.harvest(tmp_path,plan);cost=o.ledger(tmp_path)['full_native']
    assert len(inventory)==24 and sum(r['available'] for r in inventory)==1
    assert inventory[0]['reward']==0 and inventory[1]['reward'] is None
    assert inventory[1]['cause']=='attempted_exception_no_result'
    assert cost['physical_requests_attempted']==2 and cost['returned_native_completions']==1
    assert cost['usage']=={'known':{'input':5,'output':2,'cached':0},'unknown':{'input':1,'output':1,'cached':2}}

def test_authored_native_two_child_accumulation(tmp_path,monkeypatch):
    import ss_study as s
    import ss_collect as c
    from aiohttp import web
    monkeypatch.setenv('STRICT_RLM_CALIBRATION_API_KEY','CPU_FIXTURE_NOT_CREDENTIAL');monkeypatch.setenv('SCALE_CPU_KEY','CPU_FIXTURE_NOT_CREDENTIAL')
    async def fixture():
        row=next(r for r in s.read(s.ROOT/'inputs/FREE_PLAN.json') if r['records']==16 and r['operator']=='weight_sum')
        context=next(x for x in s.read(s.ROOT/'inputs/PUBLIC.json') if x['id']==row['context_id']);binding=s.binding()
        tokenizer=s.stack().native.renderer()._tokenizer;roots=[];children=[]
        labels={r['id']:row['target'] if i%3==0 else ('entity' if row['target']!='entity' else 'human being') for i,r in enumerate(context['records'])}
        expected=sum(r['weight'] for r in context['records'] if labels[r['id']]==row['target']);assert expected>0
        code1='import json\nfrom rlm.api import run as rlm\nfrom batch_contract import request_for, strict_map\nrecords=json.load(open("records.json"))\nlabels={}\npart=records[:8]\nchild=await rlm(request_for(part))\nlabels.update(strict_map(child.answer,[r["id"] for r in part]))\nprint(json.dumps(labels,sort_keys=True))'
        code2='part=records[8:]\nchild=await rlm(request_for(part))\nlabels.update(strict_map(child.answer,[r["id"] for r in part]))\nprint(json.dumps(labels,sort_keys=True))'
        code3=f'answer=sum(r["weight"] for r in records if labels[r["id"]]=={row["target"]!r})\nprint(answer)'
        async def provider(request):
            body=await request.json()
            if body['model']==binding['role_map']['root']:
                roots.append(body);assert body['sampling_params']['max_tokens']==2048
                if len(roots)==1:assert body['token_ids']==s.read(s.ROOT/'inputs/PROMPTS_ACCURATE.json')[row['id']]['token_ids']
                assert len(roots)<=4
                reply=s.stack().native.tool_action([code1,code2,code3][len(roots)-1]) if len(roots)<4 else 'Answer: '+str(expected)
            else:
                assert body['model']==binding['fixed_child'];children.append(body)
                ids=body['sampling_params']['structured_outputs']['json']['required'];assert len(ids)==8
                assert body['sampling_params']['max_tokens']==2048
                reply=json.dumps({key:labels[key] for key in ids})
            ids=tokenizer.encode(reply,add_special_tokens=False)+[151645]
            return web.json_response(dict(request_id='SCALE_CPU_'+str(len(roots)+len(children)),usage=dict(prompt_tokens=len(body['token_ids']),completion_tokens=len(ids)),choices=[dict(token_ids=ids,finish_reason='stop',logprobs=dict(content=[dict(token=f'token_id:{v}',logprob=-.5) for v in ids]))]))
        async def models(request):return web.json_response(dict(data=[dict(id=a,root=v['path'],max_model_len=8192) for a,v in binding['models'].items()]))
        app=web.Application();app.router.add_post('/inference/v1/generate',provider);app.router.add_get('/v1/models',models);runner=web.AppRunner(app);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start()
        descriptor=dict(host='127.0.0.1',port=site._server.sockets[0].getsockname()[1],api_key_env='SCALE_CPU_KEY')
        try:
            await c.implementation().episode(row,context,binding,descriptor,tmp_path/'native',time.time()+120,'free')
            result=s.read(tmp_path/'native/RESULT.json');assert result['available'] and result['final_branch_token_identity_verified'] and result['reply']=='Answer: '+str(expected)
            assert len(roots)==4 and len(children)==2
            required=[b['sampling_params']['structured_outputs']['json']['required'] for b in children]
            assert set(required[0]).isdisjoint(required[1]) and set(required[0]+required[1])==set(labels)
            assert result['gold']==s.answer(context['records'],s.read(s.ROOT/'inputs/HOST_GOLD.json')[context['id']]['labels'],row)
        finally:await runner.cleanup()
    asyncio.run(fixture())
