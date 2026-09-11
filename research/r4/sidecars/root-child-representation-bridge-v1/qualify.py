"""Actual owned native invocation→raw child→broker map→root; CPU fixture only."""
import argparse
import asyncio
import json
import os
import time
from pathlib import Path
from aiohttp import web
import study as s
import adapter
import bridge

FIXTURE_PROMPT='Use records.json and batch_contract.py. Return only Answer: N.'
async def qualify(output):
    from renderers import Qwen3RendererConfig,create_renderer
    from renderers.base import load_tokenizer
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv,SingleAgentEnvConfig
    output.mkdir(parents=True,exist_ok=False);started=time.time();calls=[];proofs=[];current={}
    os.sched_setaffinity(0,{34,35});st=s.stack();binding=s.binding()
    tok=create_renderer(load_tokenizer(str(st.prior.BASE)),Qwen3RendererConfig(enable_thinking=True))._tokenizer
    prototype=s.inputs()[0][0]
    context={**prototype,'text':'public synthetic fixture','records':[{'id':'q0002','text':'How many planets?','user':'u00'},
        {'id':'q0009','text':'Which city?','user':'u00'}]}
    code='''import json
from rlm.api import run as rlm
from batch_contract import request_for, strict_map
records=json.load(open('records.json'))
child=await rlm(request_for(records))
labels=strict_map(child.answer,[r['id'] for r in records])
print(child.answer)
'''
    expected='{"q0002":"location","q0009":"numeric value"}'
    async def provider(request):
        body=await request.json();calls.append({'arm':current['arm'],'body':body});text=tok.decode(body['token_ids'])
        grammar=body['sampling_params'].get('structured_outputs')
        if body['model']==binding['fixed_child']:
            assert grammar=={'json':bridge.schema(['q0002','q0009'],current['arm'])}
            assert bridge.child_prompt(context['records'],current['arm']) in text
            completion='["location","numeric value"]' if current['arm']=='array' else expected
        elif current['root']==0:
            assert grammar is None;current['root']+=1;completion=st.native.tool_action(code)
        else:
            assert grammar is None and expected in text and 'Traceback' not in text
            completion='Answer: 9'
        ids=tok.encode(completion,add_special_tokens=False)+[151645]
        return web.json_response({'request_id':f'BRIDGE_CPU_{len(calls)}','choices':[{'token_ids':ids,'finish_reason':'stop',
            'logprobs':{'content':[{'token':f'token_id:{t}','logprob':-.5} for t in ids]}}]})
    async def models(request):return web.json_response({'data':[{'id':a,'max_model_len':8192} for a in binding['models']]})
    app=web.Application();app.router.add_post('/inference/v1/generate',provider);app.router.add_get('/v1/models',models)
    runner=web.AppRunner(app);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start()
    os.environ['BRIDGE_CPU_KEY']='synthetic-fixture-not-secret'
    endpoint={**st.native.e.old.planned_endpoint(binding),'url':f'http://127.0.0.1:{site._server.sockets[0].getsockname()[1]}/v1','api_key_env':'BRIDGE_CPU_KEY'}
    plan=[{'id':'cpu-'+arm,'arm':arm,'context_window_id':st.prior.context_window_id(context),'seed':s.SEEDS[0],
        'temperature':.5,'client_path':'train'} for arm in ('array','map')]
    try:
        async with asyncio.timeout(360):
            for row in plan:
                current.update(arm=row['arm'],root=0);target=output/row['arm']
                task=adapter.task(context,FIXTURE_PROMPT,9,'cpu-bridge',row)
                env=SingleAgentEnv(SingleAgentEnvConfig.model_validate(adapter.environment()))
                with adapter.installed(binding,target,[row],{context['id']:context}) as interface:
                    async with env.serving():
                        raw=(await asyncio.wait_for(env.run_slot(RunSlot(task),interface.e.make_context(endpoint,row)),170)).to_record()
                s.write(target/'EPISODE.json',raw)
                roots,turns=st.exporter.episode_turns(raw,target,binding)
                assert len(roots)==2 and len(turns)==3
                events=[json.loads(line) for line in raw['traces'][0]['info']['representation_bridge']['raw'].splitlines()]
                delivered=[e for e in events if e['event']=='delivered'];assert len(delivered)==1
                event=delivered[0];assert event['eligible'] and event['projection_valid'] and event['broker_answer']==expected
                matched=[v for v in turns if v['role_depth']==1 and v['role_audit']['invocation']==event['child_invocation']]
                assert len(matched)==1
                physical=s.read(matched[0]['role_audit']['source_audit_path'])
                assert physical['native_response']['message']['content']==event['raw_answer']
                assert physical['native_wire_request']['body']==[c['body'] for c in calls if c['arm']==row['arm']][1]
                assert event['raw_answer']==('["location","numeric value"]' if row['arm']=='array' else expected)
                proofs.append({'arm':row['arm'],'raw_child_native_graph_unchanged':True,'broker_map_in_next_actual_root':True,
                    'root_turns':2,'child_turns':1,'delivered':event,'raw_child_audit':matched[0]['role_audit']['source_audit_path']})
        left=[c['body'] for c in calls if c['arm']=='array'];right=[c['body'] for c in calls if c['arm']=='map']
        assert len(left)==len(right)==3 and left[0]==right[0] and left[2]==right[2]
        assert proofs[0]['delivered']['root_invocation']!=proofs[1]['delivered']['root_invocation']
        s.write(output/'RESULT.json',{'status':'PASS','proofs':proofs,'initial_root_wire_equal':True,
            'subsequent_root_wire_equal_for_same_projected_evidence':True,'provider_calls':6,'actual_model_calls':0,'gpu_calls':0,
            'elapsed_seconds':time.time()-started,'cap_seconds':360,'fixture_likelihood_never_training_data':True})
    except BaseException as error:
        s.write(output/'FAILURE.json',{'type':type(error).__name__,'message':str(error),'elapsed_seconds':time.time()-started,'provider_calls':len(calls)});raise
    finally:s.write(output/'PROVIDER_REQUESTS.json',calls);await runner.cleanup()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    asyncio.run(qualify(p.parse_args().output))
