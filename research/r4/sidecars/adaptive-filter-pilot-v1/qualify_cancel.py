"""Cancellation of only a newly owned operator fixture, never a research service."""
import argparse
import asyncio
import json
import os
from pathlib import Path
from aiohttp import web
import experiment as e


async def main(output):
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv,SingleAgentEnvConfig
    output.mkdir(parents=True,exist_ok=False)
    binding=e.binding_for(e.c.read(e.old.ROOT/'SPEC.json')['policies']['step8'])
    seen,release=asyncio.Event(),asyncio.Event()
    calls=[]
    async def provider(request):
        body=await request.json();calls.append(body)
        assert body['model']==binding['fixed_child'],'operator cancellation invented root model request'
        seen.set();await release.wait()
        return web.json_response({'error':'CPU qualification cancelled'},status=499)
    async def models(request):
        return web.json_response({'data':[{'id':a,'max_model_len':8192} for a in binding['models']]})
    app=web.Application();app.router.add_post('/inference/v1/generate',provider);app.router.add_get('/v1/models',models)
    runner=web.AppRunner(app);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start()
    endpoint={**e.old.planned_endpoint(binding),'url':f'http://127.0.0.1:{site._server.sockets[0].getsockname()[1]}/v1','api_key_env':'ADAPTIVE_CPU_CANCEL_KEY'}
    os.environ['ADAPTIVE_CPU_CANCEL_KEY']='cpu-fixture-not-secret'
    os.environ['PATH']=str(e.capture.q.ROOTLESS/'bin')+os.pathsep+os.environ.get('PATH','')
    os.environ.setdefault('VERIFIERS_CACHE_DIR','/project/alex_phd/cache/verifiers-prime')
    environment=SingleAgentEnv(SingleAgentEnvConfig.model_validate(e.environment_config()))
    cancelled=False
    try:
        with e.installed_hooks(binding,output):
            async with environment.serving():
                task=asyncio.create_task(environment.run_slot(RunSlot(e.fixture_task('all16')),
                    e.make_context(endpoint,{'seed':981281401,'temperature':.5,'client_path':'train'})))
                await asyncio.wait_for(seen.wait(),90)
                task.cancel()
                try:
                    raw=await asyncio.wait_for(task,45)
                    e.c.write_once(output/'EPISODE.json',raw.to_record())
                except asyncio.CancelledError:
                    cancelled=True
                finally:release.set()
        audits=[e.c.read(p) for p in (output/'role-audit').glob('*-result.json')]
        assert cancelled and len(calls)==1 and len(audits)==1
        assert audits[0]['depth']==1 and audits[0]['status']=='error'
        e.c.write_once(output/'RESULT.json',{'status':'OWNED_CANCELLATION_PASS','cancelled':True,
            'provider_requests':1,'root_provider_requests':0,'native_attempts_preserved':1,
            'native_error_type':audits[0]['error_type'],'environment_serving_exited':True,
            'actual_model_calls':0,'gpu_calls':0,'root_terminal':None,
            'partial_trace_limitation':'Inherited Env may discard partial episode on cancellation; native attempt/error survives separately.'})
        print('OWNED_CANCELLATION_PASS',flush=True)
    finally:
        release.set();e.c.write_once(output/'PROVIDER_REQUESTS.json',calls);await runner.cleanup()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    asyncio.run(main(parser.parse_args().output.resolve()))
