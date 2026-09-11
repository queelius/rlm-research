"""Actual native same-REPL producer/corrector capture and explicitly shared-prefix readout."""
import argparse
import asyncio
import json
import os
from pathlib import Path
import re
import time
import traceback
import joint_protocol as p
import joint_study as s
METRICS_PATH=s.ROOT.parent/'root-example-map-visibility-v1/metrics.py'
METRICS_SHA='0ef6a89ad3655afe71226878f0296802e6b8af62b5aa295eec23e3ed151c53d3'
metrics=s.load('corrective_qualified_native_final_metrics',METRICS_PATH,METRICS_SHA)

def messages(text):return re.findall(r'<tool_response>\n(.*?)</tool_response>',text,re.S)

def audits(directory,coordinate):
    typed=[s.read(p) for p in (directory/'typed-audit').glob('*-request.json')]
    ids={v['request_id'] for v in typed if v['coordinate']['id']==coordinate}
    return {v['request_id']:v for p in (directory/'role-audit').glob('*-result.json') if (v:=s.read(p))['request_id'] in ids}

async def native_slot(env,interface,slot,endpoint,coordinate,timeout):
    return await asyncio.wait_for(env.run_slot(slot,interface.e.make_context(endpoint,coordinate)),timeout)

async def episode(row,context,binding,descriptor,target,deadline,mode,shared=None,installed=None):
    import httpx
    from aiohttp import web
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv,SingleAgentEnvConfig
    target.mkdir(parents=True,exist_ok=False);started=time.time()
    n=s.stack().native;renderer=n.renderer();tokenizer=renderer._tokenizer
    template=s.read(s.ROOT/'inputs/NATIVE_TEMPLATE.json');tools=json.loads(template['tools_ordered_json'])
    prompt=s.read(s.ROOT/'inputs/PROMPTS_ACCURATE.json')[row['id']]
    coordinate={**row,'arm':'typed','context_window_id':context['native_context_id'],'temperature':.5,'client_path':'train'}
    count=16//row['width'] if mode!='free' else 0
    shape=p.layout(row) if mode!='free' else None
    state=dict(root=0,child=0,physical=0,prefixes=[],targets=[],child_records=[],root_sampled=0)
    source=s.read(shared/'TEACHER.json') if shared else None
    shared_records=[s.read(Path(x)) for x in source['actual_child_records']] if source else []
    headers={'Authorization':'Bearer '+os.environ[descriptor['api_key_env']]}
    async with httpx.AsyncClient(trust_env=False,timeout=180,headers=headers) as client:
        async def provider(request):
            body=await request.json();state['physical']+=1;index=state['physical']
            record=dict(body=body,started_epoch=time.time(),coordinate=row,paid_model_call=False)
            try:
                if body['model']==binding['fixed_child']:
                    state['child']+=1
                    if mode=='controlled' and state['root']<=count:
                        prior=shared_records[state['child']-1]
                        p.verify_replay(body,prior['body'])
                        payload=prior['response'];record.update(origin='replayed shared actual c32 acquisition',source_path=str(source['actual_child_records'][state['child']-1]),source_sha256=s.sha(source['actual_child_records'][state['child']-1]))
                    else:
                        response=await client.post(f'http://{descriptor["host"]}:{descriptor["port"]}/inference/v1/generate',json=body)
                        record.update(status=response.status_code,paid_model_call=True,origin='actual c32');response.raise_for_status();payload=response.json()
                        state['child_records'].append(str(target/'physical'/f'{index:04}.json'))
                elif body['model']==binding['role_map']['root']:
                    state['root']+=1;number=state['root'];state['prefixes'].append(body['token_ids'])
                    if number==1 and body['token_ids']!=prompt['token_ids']:raise ValueError('initial physical prefix changed')
                    authored=mode=='capture' or mode=='controlled' and number<=count
                    if not authored:
                        if mode=='controlled' and number==count+1:
                            expected=source['turns']['corrective'];expected=expected['input_ids'][:expected['prompt_length']]
                            if body['token_ids']!=expected:raise ValueError('controlled first sampled prefix differs from shared genuine state')
                        state['root_sampled']+=1
                        response=await client.post(f'http://{descriptor["host"]}:{descriptor["port"]}/inference/v1/generate',json=body)
                        record.update(status=response.status_code,paid_model_call=True,origin='actual sampled root');response.raise_for_status();payload=response.json()
                    else:
                        if number<=count:
                            code=p.producer(row,number-1);reply=n.tool_action(code);kind='first_producer' if number==1 else 'producer_history';spans={}
                        elif row['metadata_error'] and number==count+1:
                            reply=n.tool_action(p.error_probe());kind='error_history';spans={}
                        elif number==shape['corrective_turn']:
                            observations=messages(tokenizer.decode(body['token_ids'],skip_special_tokens=False))
                            if len(observations)!=count+shape['error_turns']:raise ValueError('exact visible producer/error history required')
                            if row['metadata_error'] and ('KeyError' not in observations[-1] or 'synthetic user metadata' not in observations[-1]):raise ValueError('actual prescribed error observation required')
                            pieces,merged=p.visible_maps(observations[:count],context);state['maps']=pieces
                            code,_=p.correction(pieces,row,s.LABELS[context['target']]);reply=n.tool_action(code);kind='corrective'
                            spans,span_ids=p.target_spans(tokenizer,reply,code)
                        elif number==shape['terminal_turn']:
                            observations=messages(tokenizer.decode(body['token_ids'],skip_special_tokens=False))
                            value=p.scalar(observations[-1]);state['scalar']=value;reply='Answer: '+str(value);kind='terminal';spans={}
                        else:raise ValueError('unexpected extra authored root call; no repair/reroll')
                        ids=tokenizer.encode(reply,add_special_tokens=False)+[151645]
                        if kind=='corrective' and ids!=span_ids:raise ValueError('offset tokenization differs from actual native suffix')
                        state['targets'].append(p.row(row['id']+'-'+str(number),body['token_ids'],ids,kind,spans))
                        payload={'request_id':f'AUTHORED_NOT_POLICY_{index}','choices':[{'token_ids':ids,'finish_reason':'stop','logprobs':{'content':[{'token':f'token_id:{v}','logprob':0.} for v in ids]}}]}
                        record.update(origin='authored transport; synthetic likelihood not RL',authored_kind=kind)
                else:raise ValueError('unknown native model alias')
                record.update(response=payload,status=200);return web.json_response(payload)
            except BaseException as error:record['error']=dict(type=type(error).__name__,message=str(error));raise
            finally:record['ended_epoch']=time.time();s.write(target/'physical'/f'{index:04}.json',record)
        async def models(request):
            response=await client.get(f'http://{descriptor["host"]}:{descriptor["port"]}/v1/models');response.raise_for_status();return web.json_response(response.json())
        app=web.Application();app.router.add_post('/inference/v1/generate',provider);app.router.add_get('/v1/models',models)
        runner=web.AppRunner(app);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start()
        endpoint={**n.e.old.planned_endpoint(binding),'url':f'http://127.0.0.1:{site._server.sockets[0].getsockname()[1]}/v1','api_key_env':descriptor['api_key_env']}
        try:
            slot=RunSlot(n.task(context,prompt['prompt'],0,row['id']));timeout=min(180,max(0,deadline-time.time()))
            if installed:
                env,interface=installed;raw=(await native_slot(env,interface,slot,endpoint,coordinate,timeout)).to_record()
            else:
                interface=s.interface(target)
                with interface.installed(binding,target,[coordinate],{context['id']:context}):
                    env=SingleAgentEnv(SingleAgentEnvConfig.model_validate(interface.e.environment_config()))
                    async with env.serving():raw=(await native_slot(env,interface,slot,endpoint,coordinate,timeout)).to_record()
            s.write(target/'EPISODE.json',raw);trace=raw['traces'][0] if len(raw.get('traces',[]))==1 else {}
            if mode=='capture':
                if not trace.get('ok') or not trace.get('is_completed') or state['root']!=shape['root_turns'] or state['child']!=count:raise ValueError('authentic complete teacher sequence required')
                if trace['root_reply']!='Answer: '+str(state['scalar']):raise ValueError('authentic final mismatch')
                calls=[c for c in trace['calls'] if c['model']==binding['role_map']['root']]
                history=[trace['nodes'][0]['message'],trace['nodes'][1]['message']]
                for i,call in enumerate(calls):
                    exact=renderer.render(history,tools=tools,add_generation_prompt=True).token_ids
                    if exact!=state['prefixes'][i]:raise ValueError('graph re-rendered prefix differs from physical root prefix')
                    node=call['node'];history.append(trace['nodes'][node]['message'])
                    history.extend(n['message'] for n in trace['nodes'] if n.get('parent')==node and n.get('message',{}).get('role')=='tool')
                turns={x['kind']:x for x in state['targets'] if x['kind'] in ('first_producer','corrective','terminal')}
                s.write(target/'TEACHER.json',dict(episode_id=row['id'],coordinate=row,turns=turns,visible_maps=state['maps'],
                    masked_history_turns=[x for x in state['targets'] if x['kind'] not in turns],
                    scalar=state['scalar'],authored_not_policy=True,actual_child_records=state['child_records'],
                    prefix_ids_verified=True,episode_path=str(target/'EPISODE.json'),episode_sha256=s.sha(target/'EPISODE.json'),elapsed_seconds=time.time()-started))
            else:
                paid=[s.read(x) for x in sorted((target/'physical').glob('*.json')) if s.read(x)['paid_model_call']]
                # Host gold is scoring-only and is never exposed to producers/corrections/providers.
                gold=s.read(s.ROOT/'inputs/HOST_GOLD.json')[context['id']]['labels'];answer=sum(gold[r['id']]==context['target'] for r in context['records'] if r['user'] in row['users'])
                roles=audits(target.parent if installed else target,row['id']);final,node_ids=metrics.final_capture(trace,roles)
                score=metrics.score(trace,final,answer)
                s.write(target/'RESULT.json',dict(coordinate=row,mode=mode,**score,gold=answer,
                    final_physical_request_id=final['request_id'] if final else None,final_branch_node_indices=node_ids,
                    final_branch_token_identity_verified=final is not None,physical_cost=p.physical_cost(paid),
                    shared_acquisition_cost_for_this_state=p.physical_cost(shared_records) if shared else None,
                    hypothetical_standalone_cost=p.physical_cost(paid+shared_records) if shared else p.physical_cost(paid),
                    shared_map_count=source['scalar'] if shared else None,
                    shared_map_consistent=metrics.score(trace,final,source['scalar'])['reward'] if shared else None,
                    actual_scoped_reduction=None,execution_evidence_requires_trace_audit=True,
                    sampled_root_requests=state['root_sampled'],paid_model_calls=len(paid),replayed_shared_child_calls=count if mode=='controlled' else 0,
                    shared_source=str(shared) if shared else None,physical_cost_records=[str(x) for x in sorted((target/'physical').glob('*.json'))],elapsed_seconds=time.time()-started))
        except BaseException as error:
            s.write(target/'FAILURE.json',dict(type=type(error).__name__,message=str(error),traceback=traceback.format_exc(),mode=mode,elapsed_seconds=time.time()-started));raise
        finally:await runner.cleanup()

async def run(args):
    import httpx
    import joint_binding as b
    s.verify();s.runtime();binding=s.read(args.binding);descriptor=s.read(args.endpoint)
    b.validate(binding,descriptor,args.binding)
    headers={'Authorization':'Bearer '+os.environ[descriptor['api_key_env']]}
    async with httpx.AsyncClient(trust_env=False,timeout=20,headers=headers) as client:
        response=await client.get(f'http://{descriptor["host"]}:{descriptor["port"]}/v1/models');response.raise_for_status();cards={x['id']:x for x in response.json()['data']}
    for alias,model in binding['models'].items():
        if cards.get(alias,{}).get('root')!=model['path']:raise ValueError('live actual adapter differs')
    plan=s.read(s.ROOT/'inputs'/args.plan);public={c['id']:c for c in s.read(s.ROOT/'inputs/PUBLIC.json')}
    chosen=plan[args.start:args.stop];args.output.mkdir(parents=True,exist_ok=True)
    if args.mode=='capture':
        for row in chosen:
            if time.time()>=args.deadline:raise TimeoutError('shared capture deadline')
            await episode(row,public[row['context_id']],binding,descriptor,args.output/row['id'],args.deadline,'capture')
        if args.plan=='TRAIN_PLAN.json' and args.stop==16:
            s.corpus(16);files={str(p):s.sha(p) for p in args.output.rglob('*.json')}
            s.write(args.output/'CORPUS_READY.json',dict(identity=s.verify()['identity'],examples=16,files_sha256=files,host_gold_used=False))
    else:
        from verifiers.v1.envs.single_agent import SingleAgentEnv,SingleAgentEnvConfig
        interface=s.interface(args.output)
        queue=asyncio.Queue()
        for row in chosen:queue.put_nowait(row)
        async def worker():
            while not queue.empty() and time.time()<args.deadline:
                row=queue.get_nowait()
                try:await episode(row,public[row['context_id']],binding,descriptor,args.output/row['id'],args.deadline,args.mode,
                    s.ATTEMPT/('capture' if args.plan=='DIAGNOSTIC_PLAN.json' else 'controlled-source')/row['id'] if args.mode=='controlled' else None,installed=(env,interface))
                except Exception:pass # Failure artifact retained; planned slot remains NULL.
        coordinates=[{**row,'arm':'typed','context_window_id':public[row['context_id']]['native_context_id'],'temperature':.5,'client_path':'train'} for row in chosen]
        with interface.installed(binding,args.output,coordinates,public):
            env=SingleAgentEnv(SingleAgentEnvConfig.model_validate(interface.e.environment_config()))
            async with env.serving():await asyncio.gather(*(worker() for _ in range(4)))
        results=[]
        for row in chosen:
            path=args.output/row['id']/'RESULT.json'
            results.append(s.read(path) if path.exists() else dict(coordinate=row,reward=None,available=False,reason='unrun/incomplete; see retained FAILURE'))
        s.write(args.output/'TERMINAL.json',dict(planned=len(chosen),recorded=len(results),results=results,correct=sum(x['reward']==1 for x in results),available=sum(x['available'] for x in results)))

def planned_results(rows,recorded):
    return [recorded.get(row['id'],p.null_row(row,'unrun/incomplete; see retained FAILURE')) for row in rows]

def parse_args(argv=None):
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=('capture','free','controlled'),required=True);ap.add_argument('--plan',choices=('TRAIN_PLAN.json','FREE_PLAN.json','CONTROLLED_PLAN.json','DIAGNOSTIC_PLAN.json'),required=True)
    for name in ('binding','endpoint','output'):ap.add_argument('--'+name,type=Path,required=True)
    ap.add_argument('--start',type=int,default=0);ap.add_argument('--stop',type=int,required=True);ap.add_argument('--deadline',type=float,required=True)
    return ap.parse_args(argv)

if __name__=='__main__':asyncio.run(run(parse_args()))
