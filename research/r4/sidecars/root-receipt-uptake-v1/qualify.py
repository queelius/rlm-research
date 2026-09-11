"""Exact offered examples in pinned owned rootless/native runtime, fake tokens only."""
import argparse
import asyncio
import json
import os
from pathlib import Path
from aiohttp import web
import experiment as e
import results


async def qualify(output):
    from renderers import Qwen3RendererConfig,create_renderer
    from renderers.base import load_tokenizer
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv,SingleAgentEnvConfig
    output.mkdir(parents=True,exist_ok=False)
    renderer=create_renderer(load_tokenizer(e.c.pilot_recipe()['base_model']),Qwen3RendererConfig(enable_thinking=True))
    tokenizer=renderer._tokenizer
    policies=e.c.read(e.old.ROOT/'SPEC.json')['policies']
    bindings={w:e.binding_for(p) for w,p in policies.items()}
    tasks=e.make_tasks()
    name=sorted(tasks)[0]
    coordinate=next(r for r in e.build_plan(tasks) if r['task_name']==name)
    calls,current=[],{}
    valid='{'+','.join(json.dumps(f'q{i:04d}')+':"entity"' for i in range(1,5))+'}'
    fixtures={'valid':valid,'missing':'{"q0001":"entity"}',
        'duplicate':valid[:-1]+',"q0001":"entity"}',
        'unknown':valid[:-1]+',"q9999":"entity"}'}
    cases=[(a,'valid') for a in e.ARMS]+[('restored_receipt',f) for f in ('missing','duplicate','unknown')]

    async def provider(request):
        body=await request.json()
        calls.append({'arm':current['arm'],'fixture':current['fixture'],'body':body})
        text=tokenizer.decode(body['token_ids'])
        if body['model']==current['binding']['fixed_child']:
            if current['arm']=='unchanged':
                assert 'Return only a JSON array of labels' in text
                completion='["entity","entity","entity","entity"]'
            else:
                assert 'mapping each supplied source id to its label string' in text
                assert all(f'q{i:04d}' in text for i in range(1,5))
                assert 'Classify the type of answer requested' in text
                completion=fixtures[current['fixture']]
        elif not current['root_calls']:
            current['root_calls']+=1
            assert current['task'].data.prompt in text
            completion='<tool_call>\n'+json.dumps({'name':'ipython','arguments':{'code':current['code']}})+'\n</tool_call>'
        else:
            assert 'Traceback' not in text
            if current['arm']!='unchanged':
                assert 'q0001' in text
                # Every fixture executes the exact offered snippet, not a replacement helper.
                if current['fixture']=='valid': assert "'example_batch_count': 0" in text
                else:
                    assert "'valid': False" in text and "'labels_by_id': None" in text
            completion='Answer: 0'
        ids=tokenizer.encode(completion,add_special_tokens=False)+[151645]
        return web.json_response({'request_id':f'UPTAKE_CPU_FIXTURE_{len(calls)}','choices':[{'token_ids':ids,'finish_reason':'stop',
            'logprobs':{'content':[{'token':f'token_id:{token}','logprob':-.5} for token in ids]}}]})

    async def models(request):
        aliases={a for b in bindings.values() for a in b['models']}
        return web.json_response({'data':[{'id':a,'max_model_len':8192} for a in aliases]})
    app=web.Application()
    app.router.add_post('/inference/v1/generate',provider)
    app.router.add_get('/v1/models',models)
    runner=web.AppRunner(app)
    await runner.setup()
    site=web.TCPSite(runner,'127.0.0.1',0)
    await site.start()
    port=site._server.sockets[0].getsockname()[1]
    os.environ['UPTAKE_CPU_FIXTURE_KEY']='cpu-fixture-not-secret'
    os.environ['PATH']=str(e.capture.q.ROOTLESS/'bin')+os.pathsep+os.environ.get('PATH','')
    os.environ.setdefault('VERIFIERS_CACHE_DIR','/project/alex_phd/cache/verifiers-prime')
    proofs=[]
    try:
        for index,(arm,fixture) in enumerate(cases):
            weight='original' if index%2==0 else 'step8'
            binding=bindings[weight]
            task=e.with_prompt(tasks[name],arm)
            code=e.example_code(task.data.prompt)
            current.update(arm=arm,fixture=fixture,binding=binding,task=task,code=code,root_calls=0)
            target=output/f'{index:02d}-{arm}-{fixture}'
            endpoint={**e.old.planned_endpoint(binding),'url':f'http://127.0.0.1:{port}/v1','api_key_env':'UPTAKE_CPU_FIXTURE_KEY'}
            environment=SingleAgentEnv(SingleAgentEnvConfig.model_validate(e.c.read(e.c.PILOT/'SPEC.json')['environment']))
            with e.capture.installed_hooks(binding,target):
                async with environment.serving():
                    episode=await asyncio.wait_for(environment.run_slot(RunSlot(task),e.capture.make_context(endpoint,coordinate)),timeout=180)
                    raw=episode.to_record()
            e.c.write_once(target/'EPISODE.json',raw)
            proof=results.corroborate(raw,target,binding)
            if proof['root_calls']!=2 or proof['child_calls']!=1:
                raise ValueError('expected exact native root-child-root CPU chain')
            if arm!='unchanged':
                if not proof['helper_uptake'] or len(proof['results'])!=1: raise ValueError('helper source/native binding not corroborated')
                result=proof['results'][0]
                if result['map_valid']!=(fixture=='valid') or not result['map_report_matches']:
                    raise ValueError('strict map fixture mismatch')
                if result['receipt_access_claim']!=(arm=='restored_receipt'): raise ValueError('wrong receipt availability/access')
                if result['native_terminal_matches']!=1: raise ValueError('actual child terminal not uniquely matched')
            proofs.append({'arm':arm,'fixture':fixture,'weight':weight,'example_sha256':e.hashlib.sha256(code.encode()).hexdigest(),'proof':proof})
        e.c.write_once(output/'PROVIDER_REQUESTS.json',calls)
        result={'conditions':list(e.ARMS),'cases':proofs,'provider_calls':len(calls),'actual_model_calls':0,'gpu_calls':0,
            'real_owned_rootless_runtime':True,'real_native_client_renderer':True,'exact_offered_snippets':True,
            'fixture_notice':'Deterministic CPU-provider token/logprob fixtures, never model behavior or behavior likelihood.'}
        e.c.write_once(output/'RESULT.json',result)
        print(json.dumps({'cases':len(proofs),'provider_calls':len(calls),'gpu_calls':0}),flush=True)
    finally:
        e.c.write_once(output/'ALL_RETAINED_PROVIDER_REQUESTS.json',calls)
        await runner.cleanup()


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=e.ROOT/'qualification-attempt-002')
    asyncio.run(qualify(parser.parse_args().output.resolve()))
