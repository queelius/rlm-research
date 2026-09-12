import asyncio
import copy
import json
import time

from aiohttp import web
import pytest
import study_v2 as s
import collect_v2
import native_capture_v2 as native
import metrics

def saved():
    path=s.ROOT/'outputs/attempt-001/qwen3/science/native-calls/0000-result.json'
    n=s.read(path)
    return n['coordinate'],n['response'],json.loads(n['wire_response_text']),json.loads(n['wire_request_text'])

def test_saved_native_validator_fast_and_identical_contract():
    args=saved();s.tokenizer('qwen3');s.renderer('qwen3')
    started=time.perf_counter();native.validate_model_tokens(*args)
    assert time.perf_counter()-started<2

def test_out_of_range_ids_and_noninteger_still_reject():
    args=saved();limit=len(s.tokenizer('qwen3'))
    for bad in (-1,limit,True):
        changed=copy.deepcopy(args);changed[1]['tokens']['completion_ids'][0]=bad
        with pytest.raises(AssertionError):native.validate_model_tokens(*changed)

def test_eos_and_usage_checks_still_reject():
    args=saved();changed=copy.deepcopy(args);changed[1]['tokens']['completion_ids'][-1]=10
    with pytest.raises(AssertionError):native.validate_model_tokens(*changed)
    changed=copy.deepcopy(args);changed[2]['usage']['prompt_tokens']+=1
    with pytest.raises(AssertionError):native.validate_model_tokens(*changed)

def test_actual_two_tool_budget_completion_without_hidden_third_generation(tmp_path,monkeypatch):
    async def run():
        from verifiers.v1.env import RunSlot
        s.configure_runtime();s.bind_arm('qwen3');coordinate=s.plan('qwen3')[0]
        env=s.environment('qwen3');task=next(t for t in env.taskset if t.data.name==coordinate['id'])
        tokenizer=s.tokenizer('qwen3');requests=[]
        async def provider(request):
            body=await request.json();requests.append(body);assert len(requests)<=2
            text='<tool_call>\n'+json.dumps({'name':'ipython','arguments':{'code':"print('CPU_BUDGET_TOOL')"}})+'\n</tool_call>'
            ids=tokenizer.encode(text,add_special_tokens=False)+[tokenizer.eos_token_id]
            return web.json_response({'request_id':'CPU_BUDGET_'+str(len(requests)),
                'usage':{'prompt_tokens':len(body['token_ids']),'completion_tokens':len(ids),'total_tokens':len(body['token_ids'])+len(ids)},
                'choices':[{'token_ids':ids,'finish_reason':'stop','logprobs':{'content':[{'token':'token_id:'+str(i),'logprob':-.5} for i in ids]}}]})
        app=web.Application();app.router.add_post('/inference/v1/generate',provider)
        runner=web.AppRunner(app);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start()
        endpoint={'model_alias':s.MODEL_ALIAS,'base_model':s.MODELS['qwen3'],'adapter':None,'host':'127.0.0.1',
                  'port':site._server.sockets[0].getsockname()[1],'api_key_env':'CPU_BOUND_KEY'}
        monkeypatch.setenv('CPU_BOUND_KEY','CPU_ONLY_NOT_SECRET');started=time.perf_counter();slot=RunSlot(task)
        try:
            with native.capture(tmp_path/'native-calls',[coordinate]) as records:
                async with env.serving():
                    episode=await asyncio.wait_for(env.run_slot(slot,collect_v2.model_context(endpoint,coordinate)),120)
            raw=episode.to_record();derived=metrics.inspect(raw,coordinate,records)
        finally:await runner.cleanup()
        s.write_x(tmp_path/'EPISODE.json',raw);s.write_x(tmp_path/'DERIVED.json',derived)
        s.write_x(tmp_path/'REQUESTS.json',requests)
        assert len(requests)==2 and derived['root_actions_returned']==2
        assert derived['initial_prefix_verified'] and derived['known_model_outcome']
        assert derived['terminal_class']=='model_no_final_within_two_turns'
        assert derived['child_actions_returned']==0 and time.perf_counter()-started<120
    asyncio.run(run())
