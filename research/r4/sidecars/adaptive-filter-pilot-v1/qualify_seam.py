"""Real owned ACP/operator/IPython/broker/native path, deterministic CPU provider only."""
import argparse
import asyncio
import json
import os
from pathlib import Path
from aiohttp import web
import experiment as e


async def qualify(output):
    from renderers import Qwen3RendererConfig,create_renderer
    from renderers.base import load_tokenizer
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv,SingleAgentEnvConfig
    output.mkdir(parents=True,exist_ok=False)
    renderer=create_renderer(load_tokenizer(e.c.pilot_recipe()['base_model']),Qwen3RendererConfig(enable_thinking=True))
    tokenizer=renderer._tokenizer
    binding=e.prior.binding_for(e.c.read(e.old.ROOT/'SPEC.json')['policies']['step8'])
    coordinate={'seed':981281401,'temperature':.5,'client_path':'train'}
    current,calls={},[]
    code='import json\nfrom pathlib import Path\nassert not Path("operator_program.py").exists()\nassert not Path("operator_config.json").exists()\nfrom rlm.api import run as rlm\nfrom batch_contract import request_for,strict_map\nrecords=json.load(open("records.json"))\nchild=await rlm(request_for(records))\nlabels=strict_map(child.answer,[r["id"] for r in records])\nprint(sum(v=="numeric value" for v in labels.values()))'

    async def provider(request):
        body=await request.json()
        calls.append({'case':current['case'],'body':body})
        text=tokenizer.decode(body['token_ids'])
        if body['model']==binding['fixed_child']:
            if current['case']=='operator-filter':
                assert 'Records: [{"id":"q0001","text":"How many planets are there?"}]' in text
                assert 'What is the capital of France?' not in text
                reply='{"q0001":"numeric value"}'
            else:
                assert 'Records: [{"id":"q0001","text":"How many planets are there?"},{"id":"q0002","text":"What is the capital of France?"}]' in text
                reply='{"q0002":"location","q0001":"numeric value"}' if current['case']!='operator-invalid' else '{"q0001":"numeric value"}'
        else:
            assert current['case']=='free-valid','operator invented a root model request'
            if current['root_calls']==0:
                reply='<tool_call>\n'+json.dumps({'name':'ipython','arguments':{'code':code}})+'\n</tool_call>'
            else:
                assert 'Traceback' not in text
                reply='Answer: 1'
            current['root_calls']+=1
        ids=tokenizer.encode(reply,add_special_tokens=False)+[151645]
        return web.json_response({'request_id':f'ADAPTIVE_CPU_FIXTURE_{len(calls)}','choices':[{'token_ids':ids,'finish_reason':'stop',
            'logprobs':{'content':[{'token':f'token_id:{v}','logprob':-.5} for v in ids]}}]})

    async def models(request):
        return web.json_response({'data':[{'id':a,'max_model_len':8192} for a in binding['models']]})
    app=web.Application();app.router.add_post('/inference/v1/generate',provider);app.router.add_get('/v1/models',models)
    runner=web.AppRunner(app);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start()
    endpoint={**e.old.planned_endpoint(binding),'url':f'http://127.0.0.1:{site._server.sockets[0].getsockname()[1]}/v1','api_key_env':'ADAPTIVE_CPU_FIXTURE_KEY'}
    os.environ['ADAPTIVE_CPU_FIXTURE_KEY']='cpu-fixture-not-secret'
    os.environ['PATH']=str(e.capture.q.ROOTLESS/'bin')+os.pathsep+os.environ.get('PATH','')
    os.environ.setdefault('VERIFIERS_CACHE_DIR','/project/alex_phd/cache/verifiers-prime')
    proofs=[]
    try:
        for case in ('operator-valid','free-valid','operator-invalid','operator-filter'):
            current.update(case=case,root_calls=0)
            target=output/case
            task=e.fixture_task('free' if case=='free-valid' else 'all16')
            if case=='operator-filter':
                task.controller='filter16'
                task.plain_query='How many records from user u00 ask for a numeric value?'
                task.data=task.data.model_copy(update={'prompt':task.data.prompt.replace('How many records in the entire file ask for a numeric value?',task.plain_query)})
            environment=SingleAgentEnv(SingleAgentEnvConfig.model_validate(e.environment_config()))
            with e.installed_hooks(binding,target):
                async with environment.serving():
                    episode=await asyncio.wait_for(environment.run_slot(RunSlot(task),e.make_context(endpoint,coordinate)),180)
                    raw=episode.to_record()
            e.c.write_once(target/'EPISODE.json',raw)
            native_calls=[c for t in raw['traces'] for c in t['calls']]
            roots=[c for c in native_calls if c['model']==binding['role_map']['root']]
            children=[c for c in native_calls if c['model']==binding['fixed_child']]
            assert len(roots)==(2 if case=='free-valid' else 0) and len(children)==1,(case,len(roots),len(children))
            replies=[t.get('root_reply') for t in raw['traces']]
            assert replies==([''] if case=='operator-invalid' else ['Answer: 1']),replies
            for call in children:
                assert call['acp']['request_id']
            if case!='free-valid':
                relations=json.loads(raw['traces'][0]['info']['operator_native']['raw'])
                root_relation=next(r for r in relations['session_relations'] if r['parent_invocation'] is None)
                child_relation=next(r for r in relations['session_relations'] if r['parent_invocation'] is not None)
                assert root_relation['last_request_id'] is None
                assert child_relation['parent_invocation']==root_relation['invocation']
                assert child_relation['spawned_by_request_id'] is None
                assert child_relation['last_request_id']==children[0]['acp']['request_id']
            proof={'case':case,'root_provider_calls':len(roots),'child_provider_calls':len(children),'root_replies':replies,
                   'trace_errors':[t.get('errors') for t in raw['traces']], 'fixture_only':True}
            proofs.append(proof)
        child_bodies=[x['body'] for x in calls if x['body']['model']==binding['fixed_child']]
        assert child_bodies[0]['token_ids']==child_bodies[1]['token_ids'],'initial child physical tokens differ'
        assert child_bodies[0]['sampling_params']==child_bodies[1]['sampling_params'],'child sampling differs'
        e.c.write_once(output/'RESULT.json',{'status':'SEAM_PROOF_PASS','proofs':proofs,'full_child_initial_tokens_equal':True,
            'free_has_no_operator_program_or_config':True,
            'query_aware_filter_fixture':True,
            'child_sampling_equal':True,'operator_root_likelihood':None,'actual_model_calls':0,'gpu_calls':0,
            'fixture_notice':'Native provider tokens/logprobs are CPU fixtures, not scientific observations or training data.'})
        print(json.dumps({'status':'SEAM_PROOF_PASS','provider_calls':len(calls),'gpu_calls':0}),flush=True)
    finally:
        e.c.write_once(output/'PROVIDER_REQUESTS.json',calls)
        await runner.cleanup()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    asyncio.run(qualify(parser.parse_args().output.resolve()))
