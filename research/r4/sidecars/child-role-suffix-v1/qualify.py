"""Real concurrent rootless/native CPU graph qualification; operator fixtures only."""
import argparse
import asyncio
import json
import os
from pathlib import Path
from aiohttp import web
import experiment as e
import runtime as r


async def qualify(output):
    from renderers import Qwen3RendererConfig,create_renderer
    from renderers.base import load_tokenizer
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv,SingleAgentEnvConfig
    from root_export import episode_turns

    output.mkdir(parents=True,exist_ok=False)
    descriptor=r.read(e.capture.ENDPOINT)
    renderer=create_renderer(load_tokenizer(descriptor['base_model']['path']),Qwen3RendererConfig(enable_thinking=True))
    tokenizer=renderer._tokenizer
    requests=[]
    def tool(code): return '<tool_call>\n'+json.dumps({'name':'ipython','arguments':{'code':code}})+'\n</tool_call>'
    async def provider(request):
        body=await request.json()
        requests.append(body)
        prompt=tokenizer.decode(body['token_ids'])
        if body['model']==e.capture.role.SELECTED:
            assert 'CPU native suffix fixture' in prompt
            completion='["entity"]' if 'CHILD_TOOL_OBSERVATION' in prompt else tool('print("CHILD_TOOL_OBSERVATION")')
        elif '["entity"]' in prompt:
            completion='Answer: 0'
        else:
            completion=tool('child = await rlm("CPU native suffix fixture: classify answer type and return only a JSON array containing entity")\nprint(child.answer)')
        ids=tokenizer.encode(completion,add_special_tokens=False)+[151645]
        return web.json_response({'request_id':f'CPU_FIXTURE_{len(requests)}','choices':[{
            'token_ids':ids,'finish_reason':'stop','logprobs':{'content':[
                {'token':f'token_id:{token}','logprob':-.5} for token in ids]}}]})
    async def models(request):
        return web.json_response({'data':[{'id':alias,'max_model_len':8192} for alias in (e.capture.role.ORIGINAL,e.capture.role.SELECTED)]})
    app=web.Application()
    app.router.add_post('/inference/v1/generate',provider)
    app.router.add_get('/v1/models',models)
    runner=web.AppRunner(app)
    await runner.setup()
    site=web.TCPSite(runner,'127.0.0.1',0)
    await site.start()
    port=site._server.sockets[0].getsockname()[1]
    endpoint={'url':f'http://127.0.0.1:{port}/v1','model':e.capture.role.ORIGINAL,
        'renderer_model':descriptor['base_model']['path'],'api_key_env':'CHILD_SUFFIX_CPU_FIXTURE_KEY'}
    os.environ['CHILD_SUFFIX_CPU_FIXTURE_KEY']='cpu-only-not-provider-secret'
    os.environ['PATH']=str(e.q.ROOTLESS/'bin')+os.pathsep+os.environ.get('PATH','')
    os.environ.setdefault('VERIFIERS_CACHE_DIR','/project/alex_phd/cache/verifiers-prime')
    environment=SingleAgentEnv(SingleAgentEnvConfig.model_validate(r.read(e.capture.ROLE/'SPEC.json')['environment']))
    tasks=e.make_tasks()
    plan=e.build_plan(tasks)[:2]
    guard=r.DispatchBudget(output/'dispatch-budget',16)
    hooks=r.native_hooks(guard)
    async def one(row):
        task=e.with_prompt(tasks[row['task_name']],row['arm'])
        episode=await r.run_coordinate(row,lambda:environment.run_slot(RunSlot(task),e.capture.make_context(endpoint,row)))
        raw=episode.to_record()
        r.write_once(output/(row['arm']+'-EPISODE.json'),raw)
        return raw
    try:
        with hooks.installed_hooks(e.binding(),output):
            async with environment.serving():
                raws=await asyncio.wait_for(asyncio.gather(*(one(row) for row in plan)),timeout=420)
        r.write_once(output/'PROVIDER_REQUESTS.json',requests)
        by_arm={}
        for row,raw in zip(plan,raws,strict=True):
            roots,evidence=episode_turns(raw,output,e.binding())
            assert len(roots)==2 and len(evidence)==4
            by_arm[row['arm']]=[r.read(item['role_audit']['source_audit_path']) for item in evidence]
        control,treatment=by_arm['control'],by_arm['child_role_suffix']
        root0=lambda calls:next(a for a in calls if a['depth']==0)['native_wire_request']['body']['token_ids']
        assert root0(control)==root0(treatment),'initial root physical tokens changed'
        child=lambda calls:[a for a in calls if a['depth']==1]
        for index,(a,b) in enumerate(zip(child(control),child(treatment),strict=True)):
            pa=tokenizer.decode(a['native_wire_request']['body']['token_ids'])
            pb=tokenizer.decode(b['native_wire_request']['body']['token_ids'])
            assert r.SUFFIX not in pa and pb.count(r.SUFFIX)==1
            assert pb.replace('\n\n'+r.SUFFIX,'',1)==pa, 'child non-system prompt changed'
            if index==1: assert 'CHILD_TOOL_OBSERVATION' in pa
        overlays=[r.read(p) for p in (output/'runtime-overlays').glob('*.json')]
        assert {x['coordinate']['arm'] for x in overlays}==set(r.ARMS)
        assert len({x['runtime'] for x in overlays})==2
        assert r.COORDINATE.get() is None and len(requests)==8 and guard.sent==8
        result={'complete':True,'real_owned_rootless_runtime':True,'real_TrainClient_renderer_graph':True,
            'concurrent_arms':list(r.ARMS),'provider_fixture_calls':8,'actual_model_calls':0,'gpu_calls':0,
            'graph_physical_prefix_verified_all_calls':True,'initial_root_token_ids_identical':True,
            'child_initial_and_continuation_only_suffix_delta':True,'tools_and_child_user_unchanged':True,
            'host_ContextVar_propagation_and_reset_verified':True,
            'operator_authored_fixture_code_only':True,'synthetic_logprobs_not_measurements':True,
            'native_executed_source_sha256':hooks.executed_source_sha256,
            'source_sha256':{str(p):r.file_hash(p) for p in (ROOT/'runtime.py',ROOT/'experiment.py',Path(__file__))}}
        r.write_once(output/'RESULT.json',result)
        print(json.dumps(result),flush=True)
    finally:
        r.write_once(output/'ALL_RETAINED_REQUESTS.json',requests)
        await runner.cleanup()


ROOT=e.ROOT
if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=ROOT/'qualification-attempt-001')
    asyncio.run(qualify(parser.parse_args().output))
