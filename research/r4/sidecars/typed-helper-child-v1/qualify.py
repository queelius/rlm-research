"""Actual owned runtime/native hook, synthetic provider only; new attempt per failure."""
import argparse
import asyncio
import json
import os
import time
from pathlib import Path
from aiohttp import web
import experiment as e
import contract
import hooks

async def qualify(output):
    from renderers import Qwen3RendererConfig,create_renderer
    from renderers.base import load_tokenizer
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv,SingleAgentEnvConfig
    output.mkdir(parents=True,exist_ok=False);started=time.time();calls=[];current={};proofs=[]
    hooks.configure_runtime();os.sched_setaffinity(0,{32,33})
    renderer=create_renderer(load_tokenizer(e.c.pilot_recipe()['base_model']),Qwen3RendererConfig(enable_thinking=True));tok=renderer._tokenizer
    tasks=e.make_tasks();plan=e.build_plan(tasks);name=sorted(tasks)[0]
    rows=[r for r in plan if r['task_name']==name];binding=e.binding_for(e.c.read(e.UPTAKE/'SPEC.json')['policies']['step8'])
    catalog=e.catalog_for(tasks[name]);catalogs={str(tasks[name].data.context_window_id):catalog}
    # Both R/T execute exactly the offered raw example, then an ordinary unmatched child.
    task=e.with_prompt(tasks[name],'restored_raw')
    code=e.example_code(task.data.prompt)+'\nfrom rlm.api import run\nother = await run("CPU unmatched ordinary request")\nprint(other.answer)\n'
    async def provider(request):
        body=await request.json();calls.append({'arm':current['arm'],'body':body})
        text=tok.decode(body['token_ids']);is_child=body['model']==binding['fixed_child']
        if is_child:
            if 'CPU unmatched ordinary request' in text:
                assert body['sampling_params'].get('structured_outputs') is None
                completion='ordinary fixture'
            else:
                expected={f'q{i:04d}':'entity' for i in range(1,5)}
                grammar=body['sampling_params'].get('structured_outputs')
                assert (grammar is not None)==(current['arm']=='typed')
                if grammar: assert list(grammar['json']['properties'])==list(expected)
                completion=contract.encoded(expected)
        elif current['root_calls']==0:
            assert body['sampling_params'].get('structured_outputs') is None
            current['root_calls']+=1
            completion='<tool_call>\n'+json.dumps({'name':'ipython','arguments':{'code':code}})+'\n</tool_call>'
        else:
            assert body['sampling_params'].get('structured_outputs') is None
            assert 'Traceback' not in text and 'ordinary fixture' in text
            completion='Answer: 0'
        ids=tok.encode(completion,add_special_tokens=False)+[151645]
        return web.json_response({'request_id':f'TYPED_CPU_{len(calls)}','choices':[{'token_ids':ids,'finish_reason':'stop',
            'logprobs':{'content':[{'token':f'token_id:{t}','logprob':-.5} for t in ids]}}]})
    async def models(request): return web.json_response({'data':[{'id':a,'max_model_len':8192} for a in binding['models']]})
    app=web.Application();app.router.add_post('/inference/v1/generate',provider);app.router.add_get('/v1/models',models)
    runner=web.AppRunner(app);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start()
    port=site._server.sockets[0].getsockname()[1];os.environ['TYPED_CPU_KEY']='cpu-fixture-not-secret'
    try:
        async with asyncio.timeout(420):
            for arm in ('restored_raw','typed'):
                row=next(r for r in rows if r['arm']==arm);current.update(arm=arm,root_calls=0)
                target=output/arm
                endpoint={**e.old.planned_endpoint(binding),'url':f'http://127.0.0.1:{port}/v1','api_key_env':'TYPED_CPU_KEY'}
                env=SingleAgentEnv(SingleAgentEnvConfig.model_validate(e.environment()))
                with hooks.installed(binding,target,rows,catalogs):
                    async with env.serving():
                        episode=await asyncio.wait_for(env.run_slot(RunSlot(e.with_prompt(tasks[name],arm)),e.make_context(endpoint,row)),180)
                        raw=episode.to_record()
                e.c.write_once(target/'EPISODE.json',raw)
                roots,turns=e.native.exporter.episode_turns(raw,target,binding)
                if len(roots)!=2 or len(turns)!=4: raise ValueError('expected root + two true broker children + root')
                audits=[e.c.read(p) for p in (target/'typed-audit').glob('*-result.json')]
                if len(audits)!=4 or sum(r['decision']['apply'] for r in audits)!=(arm=='typed'): raise ValueError('hook decision count')
                if not all(r['wire_schema_verified'] for r in audits): raise ValueError('missing actual wire proof')
                proofs.append({'arm':arm,'root_turns':len(roots),'all_turns':len(turns),'typed_invocations':sum(r['decision']['apply'] for r in audits),
                               'native_graph_verified':True,'strict_reward':e.capture.native.episode_metrics(raw,0)['strict_reward']})
        a=[r['body'] for r in calls if r['arm']=='restored_raw'];b=[r['body'] for r in calls if r['arm']=='typed']
        assert len(a)==len(b)==4
        comparisons=[]
        for i,(left,right) in enumerate(zip(a,b,strict=True)):
            right=json.loads(json.dumps(right));grammar=right['sampling_params'].pop('structured_outputs',None)
            assert left==right,'R/T native wires differ beyond grammar'
            comparisons.append({'index':i,'wire_equal_except_schema':True,'typed_schema_present':grammar is not None,'alias':left['model']})
        e.c.write_once(output/'RESULT.json',{'conditions':['restored_raw','typed'],'cases':proofs,'comparisons':comparisons,
            'provider_calls':len(calls),'actual_model_calls':0,'gpu_calls':0,'image_id':e.IMAGE,'seconds':time.time()-started,
            'synthetic_only':'Fixture token/logprob data, never model outcomes or behavior likelihood.','cap_seconds':420})
    except BaseException as error:
        e.c.write_once(output/'FAILURE.json',{'type':type(error).__name__,'message':str(error),'seconds':time.time()-started,'provider_calls':len(calls)});raise
    finally:
        e.c.write_once(output/'PROVIDER_REQUESTS.json',calls);await runner.cleanup()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    asyncio.run(qualify(p.parse_args().output))
