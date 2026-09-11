"""Prepare authored SFT with REAL owned CPU metadata observations, never fake child targets."""
import argparse
import asyncio
import copy
import json
import os
from pathlib import Path
import study as s
import native as n

async def prepare(output):
    from aiohttp import web
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv,SingleAgentEnvConfig
    output.mkdir(parents=True,exist_ok=False)
    public,host,provenance=s.build_data()
    s.write(output/'PUBLIC.json',public);s.write(output/'HOST_GOLD.json',host)
    s.write(output/'PROVENANCE.json',provenance);s.write(output/'EVAL_PLAN.json',s.plan(public))
    renderer=n.renderer();tokenizer=renderer._tokenizer;binding=n.initial_binding()
    template=s.read(s.ROOT.parent/'adaptive-filter-pilot-v1/qualification-attempt-005/free-valid/EPISODE.json')['traces'][0]
    system=template['nodes'][0]['message'];tools=n.wire_tools(template['tools'])
    state={};wire=[];rows=[];proofs=[]
    async def provider(request):
        body=await request.json();wire.append(dict(example=state['name'],body=body))
        if body['model']==binding['fixed_child']:
            # One helper seam fixture only. Its fake answer NEVER appears in any SFT row.
            state['child_calls']+=1
            reply=json.dumps({r['id']:'entity' for r in state['context']['records'][:4]})
        else:
            state['prefixes'].append(body['token_ids'])
            reply=n.tool_action(state['code']) if len(state['prefixes'])==1 else 'Answer: '+str(state['answer'])
            if len(state['prefixes'])>1:
                text=tokenizer.decode(body['token_ids'])
                assert 'Traceback' not in text,text[-2000:]
                if state['kind']=='terminal':
                    assert f'\n{state["answer"]}\n' in text or f'>{state["answer"]}\n' in text,text[-1500:]
        ids=tokenizer.encode(reply,add_special_tokens=False)+[151645]
        return web.json_response({'request_id':f'INTERFACE_AUTHORED_CPU_{len(wire)}','choices':[{'token_ids':ids,'finish_reason':'stop','logprobs':{'content':[{'token':f'token_id:{v}','logprob':-.5} for v in ids]}}]})
    async def models(request):return web.json_response({'data':[{'id':a,'max_model_len':8192} for a in binding['models']]})
    app=web.Application();app.router.add_post('/inference/v1/generate',provider);app.router.add_get('/v1/models',models)
    runner=web.AppRunner(app);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start()
    endpoint={**n.e.old.planned_endpoint(binding),'url':f'http://127.0.0.1:{site._server.sockets[0].getsockname()[1]}/v1','api_key_env':'INTERFACE_AUTHORED_CPU_KEY'}
    os.environ['INTERFACE_AUTHORED_CPU_KEY']='cpu-fixture-not-secret'
    os.environ['PATH']=str(n.e.capture.q.ROOTLESS/'bin')+os.pathsep+os.environ.get('PATH','')
    os.environ.setdefault('VERIFIERS_CACHE_DIR','/project/alex_phd/cache/verifiers-prime')
    try:
        for i,c in enumerate(public[:8]):
            for family in ('single_user','global'):
                p=s.prompt(c,family)
                prefix=renderer.render([system,{'role':'user','content':p}],tools=tools,add_generation_prompt=True).token_ids
                target=tokenizer.encode(n.tool_action(s.HELPER),add_special_tokens=False)+[151645]
                rows.append(s.training_row(c['id']+'-'+family,'helper',prefix,target))
            for kind in ('divisibility','users'):
                p,code,answer=s.metadata(c,i,kind);name=c['id']+'-'+kind
                state.update(name=name,kind='terminal',context=c,code=code,answer=answer,prefixes=[],child_calls=0)
                target=output/'native'/name
                env=SingleAgentEnv(SingleAgentEnvConfig.model_validate(n.e.environment_config()))
                with n.e.capture.installed_hooks(binding,target):
                    async with env.serving():
                        episode=await asyncio.wait_for(env.run_slot(RunSlot(n.task(c,p,answer,name)),n.e.make_context(endpoint,{'seed':981284001,'temperature':.5,'client_path':'train'})),120)
                raw=episode.to_record();s.write(target/'EPISODE.json',raw)
                assert len(state['prefixes'])==2 and state['child_calls']==0
                assert raw['traces'][0]['root_reply']==f'Answer: {answer}' and raw['traces'][0]['is_completed']
                expected=renderer.render([system,{'role':'user','content':p}],tools=tools,add_generation_prompt=True).token_ids
                assert expected==state['prefixes'][0],'first native physical prefix mismatch'
                targetids=tokenizer.encode(f'Answer: {answer}',add_special_tokens=False)+[151645]
                row=s.training_row(name,'terminal',state['prefixes'][1],targetids)
                row.update(observed_answer=answer,observation_episode_path=str(target/'EPISODE.json'),observation_episode_sha256=s.sha(target/'EPISODE.json'))
                rows.append(row);proofs.append(dict(id=name,real_owned_metadata_execution=True,child_calls=0,first_prefix_equal=True,answer=answer))
                print(json.dumps({'prepared':name,'rows':len(rows)}),flush=True)
        # Actual native helper seam, independent qualification fixture; no child/second root tokens train.
        c=public[0];p=s.prompt(c,'single_user');name='helper-native-proof'
        state.update(name=name,kind='helper',context=c,code=s.HELPER,answer=0,prefixes=[],child_calls=0)
        target=output/'native'/name;env=SingleAgentEnv(SingleAgentEnvConfig.model_validate(n.e.environment_config()))
        with n.e.capture.installed_hooks(binding,target):
            async with env.serving():raw=(await asyncio.wait_for(env.run_slot(RunSlot(n.task(c,p,0,name)),n.e.make_context(endpoint,{'seed':981284001,'temperature':.5,'client_path':'train'})),120)).to_record()
        s.write(target/'EPISODE.json',raw)
        assert state['child_calls']==1 and state['prefixes'][0]==rows[0]['input_ids'][:rows[0]['prompt_length']]
        assert len(rows)==32 and sum(r['kind']=='helper' for r in rows)==16
        s.write(output/'ROWS.json',rows)
        s.write(output/'NATIVE_TEMPLATE.json',dict(system=system,tools_ordered_json=json.dumps(tools)))
        s.write(output/'QUALIFICATION.json',dict(status='PASS',actual_model_calls=0,gpu_calls=0,metadata=proofs,helper_initial_prefix_equal=True,helper_fake_observation_in_training=False,training_likelihood='AUTHORED_TARGET_CE_ONLY',target_tokens=sum(r['target_tokens'] for r in rows),max_input_tokens=max(len(r['input_ids']) for r in rows)))
    finally:
        s.write(output/'CPU_PROVIDER_REQUESTS.json',wire);await runner.cleanup()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=s.ROOT/'prepared-v2')
    asyncio.run(prepare(p.parse_args().output))
