"""Two fresh owned operator/broker/native fixtures, no model sampling."""
import argparse
import asyncio
import json
import os
import time
from pathlib import Path
from aiohttp import web
import experiment as e
import hooks
import contract

async def qualify(output):
    from renderers import Qwen3RendererConfig,create_renderer
    from renderers.base import load_tokenizer
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv,SingleAgentEnvConfig
    output.mkdir(parents=True,exist_ok=False);started=time.time();calls=[];current={};proofs=[]
    hooks.configure_runtime();os.sched_setaffinity(0,{32,33})
    tok=create_renderer(load_tokenizer(e.c.pilot_recipe()['base_model']),Qwen3RendererConfig(enable_thinking=True))._tokenizer
    binding=e.binding_for(e.c.read(e.PRIOR/'SPEC.json')['policy'])
    async def provider(request):
        body=await request.json();calls.append({'case':current['case'],'body':body})
        assert body['model']==binding['fixed_child'],'operator invented root model action'
        schema=body['sampling_params']['structured_outputs']['json']
        ids=['q0001','q0002'] if current['case']=='all16' else ['q0001']
        assert list(schema['properties'])==schema['required']==ids
        assert not schema['additionalProperties']
        labels={i:'numeric value' if i=='q0001' else 'location' for i in ids}
        text=contract.encoded(labels);contract.batch.strict_map(text,ids)
        tokens=tok.encode(text,add_special_tokens=False)+[151645]
        return web.json_response({'request_id':f'TYPED_OPERATOR_CPU_{len(calls)}','choices':[{'token_ids':tokens,'finish_reason':'stop',
            'logprobs':{'content':[{'token':f'token_id:{t}','logprob':-.5} for t in tokens]}}]})
    async def models(request):return web.json_response({'data':[{'id':a,'max_model_len':8192} for a in binding['models']]})
    app=web.Application();app.router.add_post('/inference/v1/generate',provider);app.router.add_get('/v1/models',models)
    runner=web.AppRunner(app);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start()
    endpoint={**e.old.planned_endpoint(binding),'url':f'http://127.0.0.1:{site._server.sockets[0].getsockname()[1]}/v1','api_key_env':'TYPED_OPERATOR_CPU_KEY'}
    os.environ['TYPED_OPERATOR_CPU_KEY']='cpu-fixture-not-secret'
    try:
        async with asyncio.timeout(360):
            for index,kind in enumerate(('all16','filter16')):
                current['case']=kind;task=e.a.fixture_task(kind)
                task.plain_query='How many records from user u00 ask for a numeric value?'
                task.data=task.data.model_copy(update={'prompt':task.data.prompt.replace('How many records in the entire file ask for a numeric value?',task.plain_query)})
                row={'id':f'cpu-{kind}','arm':'user_all' if kind=='all16' else 'user_filter','context_window_id':task.data.context_window_id,
                    'seed':e.SEEDS[0],'temperature':.5,'client_path':'train'}
                catalog={str(task.data.context_window_id):{'context_sha256':e.hashlib.sha256(task.data.context.encode()).hexdigest(),'records':task.public_records}}
                target=output/kind;environment=SingleAgentEnv(SingleAgentEnvConfig.model_validate(e.environment_config()))
                with hooks.installed(binding,target,[row],catalog):
                    async with environment.serving():
                        episode=await asyncio.wait_for(environment.run_slot(RunSlot(task),e.make_context(endpoint,row)),160)
                        raw=episode.to_record()
                e.c.write_once(target/'EPISODE.json',raw)
                all_calls=[c for t in raw['traces'] for c in t['calls']]
                assert len(all_calls)==1 and all_calls[0]['model']==binding['fixed_child']
                assert [t.get('root_reply') for t in raw['traces']]==['Answer: 1']
                relations=json.loads(raw['traces'][0]['info']['operator_native']['raw'])['session_relations']
                root=next(r for r in relations if r['parent_invocation'] is None);child=next(r for r in relations if r['parent_invocation'] is not None)
                assert root['last_request_id'] is None and child['parent_invocation']==root['invocation'] and child['spawned_by_request_id'] is None
                assert child['last_request_id']==all_calls[0]['acp']['request_id']
                audit=[e.c.read(p) for p in (target/'typed-audit').glob('*-result.json')]
                assert len(audit)==1 and audit[0]['wire_schema_verified'] and audit[0]['decision']['apply']
                proofs.append({'case':kind,'root_model_calls':0,'child_model_calls':1,'requested_ids':audit[0]['decision']['requested_ids'],
                    'answer':'Answer: 1','native_ancestry_verified':True,'operator_root_behavior_likelihood':None})
        e.c.write_once(output/'RESULT.json',{'status':'PASS','cases':proofs,'provider_calls':len(calls),'real_model_calls':0,'gpu_calls':0,
            'seconds':time.time()-started,'cap_seconds':360,'image_id':e.IMAGE,'source':'Unchanged operator code; real owned runtime/native client; synthetic fixture replies/logprobs only.'})
    except BaseException as error:
        e.c.write_once(output/'FAILURE.json',{'type':type(error).__name__,'message':str(error),'seconds':time.time()-started,'provider_calls':len(calls)});raise
    finally:e.c.write_once(output/'PROVIDER_REQUESTS.json',calls);await runner.cleanup()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    asyncio.run(qualify(p.parse_args().output))
