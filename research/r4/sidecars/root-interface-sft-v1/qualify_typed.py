"""One authored owned-native proof: new catalog/free root/typed child/physical prefix."""
import asyncio
import json
from aiohttp import web
import study as s
import native as n
import interface

async def run():
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv,SingleAgentEnvConfig
    output=s.ROOT/'qualification-typed-001';output.mkdir(exist_ok=False)
    public=s.read(s.ROOT/'prepared-v2/PUBLIC.json');c=public[0]
    row=dict(id='authored-new-catalog-helper-proof',arm='typed',context_window_id=s.context_window_id(c),seed=981284001,temperature=.5,client_path='train')
    renderer=n.renderer();tokenizer=renderer._tokenizer;binding=n.initial_binding();calls=[]
    async def provider(request):
        body=await request.json();calls.append(body)
        if body['model']==binding['fixed_child']:
            grammar=body['sampling_params']['structured_outputs']['json']
            assert list(grammar['properties'])==[r['id'] for r in c['records'][:4]]
            reply=json.dumps({r['id']:'entity' for r in c['records'][:4]})
        else:
            assert 'structured_outputs' not in body['sampling_params']
            reply=n.tool_action(s.HELPER) if len(calls)==1 else 'Answer: 0'
        ids=tokenizer.encode(reply,add_special_tokens=False)+[151645]
        return web.json_response({'request_id':f'INTERFACE_TYPED_CPU_{len(calls)}','choices':[{'token_ids':ids,'finish_reason':'stop','logprobs':{'content':[{'token':f'token_id:{v}','logprob':-.5} for v in ids]}}]})
    async def models(request):return web.json_response({'data':[{'id':a,'max_model_len':8192} for a in binding['models']]})
    app=web.Application();app.router.add_post('/inference/v1/generate',provider);app.router.add_get('/v1/models',models)
    runner=web.AppRunner(app);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start()
    endpoint={**n.e.old.planned_endpoint(binding),'url':f'http://127.0.0.1:{site._server.sockets[0].getsockname()[1]}/v1','api_key_env':'INTERFACE_TYPED_CPU_KEY'}
    import os
    os.environ['INTERFACE_TYPED_CPU_KEY']='cpu-fixture-not-secret'
    try:
        task=n.task(c,s.prompt(c,'single_user'),0,row['id'])
        with interface.installed(binding,output,[row],{c['id']:c}):
            env=SingleAgentEnv(SingleAgentEnvConfig.model_validate(interface.e.environment_config()))
            async with env.serving():raw=(await asyncio.wait_for(env.run_slot(RunSlot(task),interface.e.make_context(endpoint,row)),180)).to_record()
        s.write(output/'EPISODE.json',raw)
        first=s.read(s.ROOT/'prepared-v2/ROWS.json')[0]
        assert len(calls)==3 and calls[0]['token_ids']==first['input_ids'][:first['prompt_length']]
        assert raw['traces'][0]['root_reply']=='Answer: 0'
        assert task.data.context_window_id==24000 and task.data.source_id==24024000
        assert 'operator_program' not in s.HELPER
        s.write(output/'RESULT.json',dict(status='PASS',actual_model_calls=0,gpu_calls=0,new_context_window_id=task.data.context_window_id,context_len=task.data.context_len,root_unconstrained=True,child_typed_exact_first4=True,first_native_wire_prefix_equal=True,provider_calls=3,root_model_calls=2,child_model_calls=1,source='Operator-authored qualification only; child answer/second-root prefix NEVER training data'))
        print('PASS new-catalog free-root→typed-child→strict-map native qualification',flush=True)
    finally:s.write(output/'PROVIDER_REQUESTS.json',calls);await runner.cleanup()

if __name__=='__main__':asyncio.run(run())
