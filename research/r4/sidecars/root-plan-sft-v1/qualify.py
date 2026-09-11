"""Owned native authored-plan fixtures; synthetic child answers NEVER become SFT data."""
import argparse
import asyncio
import json
import os
import time
import traceback
from pathlib import Path
import study as s


async def run(output):
    from aiohttp import web
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv,SingleAgentEnvConfig
    started=time.monotonic();output.mkdir(parents=True,exist_ok=False)
    st=s.stack();n=st.native;renderer=n.renderer();tokenizer=renderer._tokenizer;binding=n.initial_binding()
    context=s.read(s.PRIOR/'prepared-v2/PUBLIC.json')[0];public={context['id']:context}
    labels=list(s.LABELS.values());synthetic={r['id']:labels[(int(r['id'][1:])-1)%6] for r in context['records']}
    answer=sum(synthetic[r['id']]==s.LABELS[context['target']] for r in context['records'] if r['user']==context['query_users'][0])
    state={};wire=[];proofs=[]
    async def provider(request):
        body=await request.json();wire.append(dict(arm=state['arm'],body=body))
        if body['model']==binding['fixed_child']:
            state['children']+=1;schema=body['sampling_params']['structured_outputs']['json']
            if isinstance(schema,str):schema=json.loads(schema)
            ids=list(schema['properties']);state['selected'].extend(ids)
            reply=json.dumps({i:synthetic[i] for i in ids})
        else:
            state['prefixes'].append(body['token_ids'])
            if len(state['prefixes'])==1:reply=n.tool_action(state['code'])
            else:
                text=tokenizer.decode(body['token_ids']);state['second_text']=text
                if 'Traceback' in text:raise ValueError('authored procedure raised in owned runtime: '+text[-1200:])
                reply='Answer: '+str(answer)
        ids=tokenizer.encode(reply,add_special_tokens=False)+[151645]
        return web.json_response({'request_id':f'PLAN_AUTHORED_CPU_{len(wire)}','choices':[{'token_ids':ids,'finish_reason':'stop','logprobs':{'content':[{'token':f'token_id:{v}','logprob':-.5} for v in ids]}}]})
    async def models(request):return web.json_response({'data':[{'id':a,'max_model_len':8192} for a in binding['models']]})
    app=web.Application();app.router.add_post('/inference/v1/generate',provider);app.router.add_get('/v1/models',models)
    runner=web.AppRunner(app);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start()
    endpoint={**n.e.old.planned_endpoint(binding),'url':f'http://127.0.0.1:{site._server.sockets[0].getsockname()[1]}/v1','api_key_env':'PLAN_AUTHORED_CPU_KEY'}
    os.environ['PLAN_AUTHORED_CPU_KEY']='cpu-fixture-not-secret'
    try:
        for arm in s.ARMS:
            name='plan-native-'+arm;row=next(r for r in s.read(s.ROOT/'prepared-v2'/f'ROWS_{arm}.json') if r['id']=='train-00-single_user')
            prompt=st.prior.prompt(context,'single_user');target=output/arm;target.mkdir()
            coordinate=dict(id=name,context_id=context['id'],context_window_id=st.prior.context_window_id(context),family='single_user',arm='free',seed=981320901,temperature=.5,client_path='train')
            state.update(arm=arm,code=row['authored_code'],prefixes=[],children=0,selected=[],second_text='')
            with s.aliases({'interface':st.interface}):interface=st.local.configure_interface(target)
            with interface.installed(binding,target,[coordinate],public):
                env=SingleAgentEnv(SingleAgentEnvConfig.model_validate(interface.e.environment_config()))
                async with env.serving():
                    episode=await asyncio.wait_for(env.run_slot(RunSlot(n.task(context,prompt,answer,name)),interface.e.make_context(endpoint,coordinate)),max(1,180-(time.monotonic()-started)))
            raw=episode.to_record();s.write(target/'EPISODE.json',raw)
            wanted=context['records'] if arm=='canonical' else [r for r in context['records'] if r['user']==context['query_users'][0]]
            expected_ids=[r['id'] for r in wanted]
            assert state['selected']==expected_ids and state['children']==(len(wanted)+15)//16
            assert len(state['prefixes'])==2 and state['prefixes'][0]==row['input_ids'][:row['prompt_length']]
            assert tokenizer.encode(n.tool_action(row['authored_code']),add_special_tokens=False)+[151645]==row['input_ids'][row['prompt_length']:]
            trace=raw['traces'][0];assert trace['is_completed'] and trace['root_reply']==f'Answer: {answer}'
            tools=[node['message']['content'] for node in trace['nodes'] if node.get('message',{}).get('role')=='tool']
            assert any(str(answer) in str(v) for v in tools),tools
            proofs.append(dict(arm=arm,children=state['children'],selected_ids=state['selected'],root_turns=len(state['prefixes']),
              initial_native_token_ids_equal=True,authored_action_suffix_equal=True,synthetic_printed_answer=answer,
              episode_path=str(target/'EPISODE.json'),episode_sha256=s.sha(target/'EPISODE.json')))
            print({'arm':arm,'native_fixture':'PASS','child_calls':state['children']},flush=True)
        s.write(output/'RESULT.json',dict(status='PASS',proofs=proofs,physical_cpu_provider_requests=len(wire),
          fake_provider_data_in_training=False,authored_code_executed_on_host=False,gpu_calls=0,actual_model_calls=0,elapsed_seconds=time.monotonic()-started))
    except BaseException as error:
        s.write(output/'FAILURE.json',dict(type=type(error).__name__,message=str(error),traceback=traceback.format_exc(),elapsed_seconds=time.monotonic()-started));raise
    finally:
        s.write(output/'CPU_PROVIDER_REQUESTS.json',wire);await runner.cleanup()


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=s.ROOT/'qualification-002');a=p.parse_args();asyncio.run(run(a.output))
