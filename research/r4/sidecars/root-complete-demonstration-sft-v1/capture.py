"""Run authored actions in owned native IPython; only children contact the real model."""
import argparse
import asyncio
import json
import os
import re
import time
import traceback
from pathlib import Path
import study as s
from learning import terminal_row

def scalar_from_prefix(text):
    matches=re.findall(r'<tool_response>\n(.*?)</tool_response>',text,re.S)
    if len(matches)!=1 or not re.fullmatch(r'\s*[0-9]+\s*',matches[0]):raise ValueError('actual action did not yield one authentic scalar; stop corpus')
    return int(matches[0])

async def run(args):
    import httpx
    from aiohttp import web
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv,SingleAgentEnvConfig
    import binding as b
    ready=s.verify();args.output.mkdir(parents=True,exist_ok=False);started=time.time()
    binding=s.read(args.binding);descriptor=s.read(args.endpoint)
    if binding!=b.binding('unchanged',b.selected('unchanged')):raise ValueError('actual teacher child/start binding')
    b.validate_descriptor(binding,descriptor,s.sha(args.binding))
    headers={'Authorization':'Bearer '+os.environ[descriptor['api_key_env']]}
    base=f'http://{descriptor["host"]}:{descriptor["port"]}'
    st=s.stack();n=st.native;renderer=n.renderer();tokenizer=renderer._tokenizer
    templates=s.read(s.PLAN/'prepared-v2/NATIVE_TEMPLATE.json');tools=json.loads(templates['tools_ordered_json'])
    originals=s.read(s.PLAN/'prepared-v2/ROWS_canonical.json');public={c['id']:c for c in s.read(s.PRIOR/'prepared-v2/PUBLIC.json') if c['stratum']=='train'}
    host_gold=s.read(s.PRIOR/'prepared-v2/HOST_GOLD.json')
    state={};episodes=[];attempt=0
    async with httpx.AsyncClient(trust_env=False,timeout=180,headers=headers) as client:
        cards=(await client.get(base+'/v1/models'));cards.raise_for_status();cards={c['id']:c for c in cards.json()['data']}
        for alias,model in binding['models'].items():
            if cards.get(alias,{}).get('root')!=model['path'] or cards[alias].get('parent')!=descriptor['base_model']['path']:raise ValueError('teacher actual /models differs')
        s.write(args.output/'PROVIDER_BINDING.json',dict(binding=binding,descriptor=descriptor,cards=cards,scripted_roots=True,live_child=True,sampled_root_policy=False))
        async def provider(request):
            nonlocal attempt
            body=await request.json();attempt+=1;path=args.output/'physical'/f'{attempt:04d}.json'
            row=dict(body=body,started_epoch=time.time(),authored_example_id=state['action']['id'])
            try:
                if body['model']==binding['fixed_child']:
                    row['origin']='actual c32 model';state['child_calls']+=1
                    response=await client.post(base+'/inference/v1/generate',json=body)
                    row.update(status=response.status_code,response=response.json());response.raise_for_status()
                    return web.json_response(response.json(),status=response.status_code)
                if body['model']!=binding['role_map']['root']:raise ValueError('unknown model alias')
                row['origin']='operator-authored native root script; NOT policy sampling';state['prefixes'].append(body['token_ids'])
                if len(state['prefixes'])==1:
                    action=state['action']
                    if body['token_ids']!=action['input_ids'][:action['prompt_length']]:raise ValueError('exact authored initial prefix differs')
                    reply=n.tool_action(action['authored_code'])
                elif len(state['prefixes'])==2:
                    state['scalar']=scalar_from_prefix(tokenizer.decode(body['token_ids'],skip_special_tokens=False))
                    reply='Answer: '+str(state['scalar'])
                else:raise ValueError('unexpected extra authored root request; no repair')
                ids=tokenizer.encode(reply,add_special_tokens=False)+[151645]
                payload={'request_id':f'AUTHORED_NOT_POLICY_{attempt}','choices':[{'token_ids':ids,'finish_reason':'stop','logprobs':{'content':[{'token':f'token_id:{v}','logprob':0.} for v in ids]}}]}
                row.update(status=200,response=payload,logprobs='synthetic transport placeholder, never training likelihood')
                return web.json_response(payload)
            except BaseException as error:row['error']=dict(type=type(error).__name__,message=str(error));raise
            finally:row['ended_epoch']=time.time();s.write(path,row)
        async def models(request):return web.json_response({'data':list(cards.values())})
        app=web.Application();app.router.add_post('/inference/v1/generate',provider);app.router.add_get('/v1/models',models)
        runner=web.AppRunner(app);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start()
        endpoint={**n.e.old.planned_endpoint(binding),'url':f'http://127.0.0.1:{site._server.sockets[0].getsockname()[1]}/v1','api_key_env':descriptor['api_key_env']}
        try:
            for index,action in enumerate(originals):
                if time.time()>=args.deadline:raise TimeoutError('capture deadline; partial corpus retained, no reroll')
                c=public[action['context_id']];target=args.output/f'example-{index:02d}';target.mkdir()
                coordinate=dict(id='authored-'+action['id'],context_id=c['id'],context_window_id=st.prior.context_window_id(c),family=action['family'],arm='free',seed=981330101+index,temperature=.5,client_path='train')
                state.clear();state.update(action=action,prefixes=[],scalar=None,child_calls=0)
                with s.aliases({'interface':st.interface}):interface=st.local.configure_interface(target)
                with interface.installed(binding,target,[coordinate],{c['id']:c}):
                    env=SingleAgentEnv(SingleAgentEnvConfig.model_validate(interface.e.environment_config()))
                    async with env.serving():
                        raw=(await asyncio.wait_for(env.run_slot(RunSlot(n.task(c,st.prior.prompt(c,action['family']),0,coordinate['id'])),interface.e.make_context(endpoint,coordinate)),min(180,max(0,args.deadline-time.time())))).to_record()
                # Host task's dummy verifier answer is not a teacher label or RL reward.
                s.write(target/'EPISODE_AUTHORED_NOT_RL.json',raw)
                trace=raw['traces'][0];nodes=trace['nodes'];toolnodes=[v for v in nodes if v.get('message',{}).get('role')=='tool']
                if not trace['is_completed'] or not trace['ok'] or len(state['prefixes'])!=2 or len(toolnodes)!=1 or not re.fullmatch(r'\s*[0-9]+\s*',toolnodes[0]['message']['content']):raise ValueError('authentic completed one-action scalar execution required')
                scalar=int(toolnodes[0]['message']['content'])
                if scalar!=state['scalar'] or trace['root_reply']!='Answer: '+str(scalar):raise ValueError('actual observation/target disagreement')
                actionnode=next(v for v in nodes if v.get('message',{}).get('role')=='assistant')
                messages=[nodes[0]['message'],nodes[1]['message'],actionnode['message'],toolnodes[0]['message']]
                exact=renderer.render(messages,tools=tools,add_generation_prompt=True).token_ids
                if exact!=state['prefixes'][1]:raise ValueError('native graph/physical second prefix mismatch')
                suffix=tokenizer.encode('Answer: '+str(scalar),add_special_tokens=False)+[151645]
                true_count=host_gold[c['id']]['answers'][action['family']]
                evidence=dict(authentic_scalar=scalar,host_diagnostic_true_dataset_count=true_count,scalar_equals_dataset_count=scalar==true_count,
                  native_task_dummy_answer_is_gold=False,episode_path=str(target/'EPISODE_AUTHORED_NOT_RL.json'),episode_sha256=s.sha(target/'EPISODE_AUTHORED_NOT_RL.json'),native_prefix_ids_equal=True,child_calls=state['child_calls'],sampled_root_policy=False)
                terminal=terminal_row(action['id']+'-terminal',exact,suffix,evidence)
                episode=dict(episode_id=action['id'],turns=[action,terminal],provenance='operator-authored SFT with actual child execution; NOT RL')
                s.write(target/'TEACHER.json',episode);episodes.append(episode);print({'captured':len(episodes),'child_calls':state['child_calls'],'terminal_tokens':len(suffix)},flush=True)
            if len(episodes)!=16:raise ValueError('all16 or stop')
            s.write(args.output/'EPISODES.json',episodes)
            files={str(p):s.sha(p) for p in args.output.rglob('*.json')}
            s.write(args.output/'CORPUS_READY.json',dict(prepared_identity=ready['identity'],episodes=16,synthetic_child=False,sampled_root_policy=False,files_sha256=files,action_targets_per_pass=sum(e['turns'][0]['target_tokens'] for e in episodes),terminal_targets_per_pass=sum(e['turns'][1]['target_tokens'] for e in episodes),elapsed_seconds=time.time()-started))
        except BaseException as error:
            s.write(args.output/'FAILURE.json',dict(type=type(error).__name__,message=str(error),traceback=traceback.format_exc(),captured=len(episodes),no_reroll=True));raise
        finally:await runner.cleanup()

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ('output','binding','endpoint'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--deadline',type=float,required=True);asyncio.run(run(p.parse_args()))
