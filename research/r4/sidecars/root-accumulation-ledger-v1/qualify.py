"""One scoped owned native CPU fixture suite; synthetic provider, no model inference."""
import argparse
import asyncio
import json
import os
import time
from pathlib import Path
from aiohttp import web
import study as s
import adapter

async def qualify(output):
    from renderers import Qwen3RendererConfig,create_renderer
    from renderers.base import load_tokenizer
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv,SingleAgentEnvConfig
    output.mkdir(parents=True,exist_ok=False);started=time.time();calls=[];proofs=[];current={}
    os.sched_setaffinity(0,{34,35});st=s.stack();binding=s.binding()
    tok=create_renderer(load_tokenizer(str(st.prior.BASE)),Qwen3RendererConfig(enable_thinking=True))._tokenizer
    context={'id':'fixture-ledger','stratum':'validation','text':'fixture public records',
             'records':[{'id':'q0001','text':'How many planets?'},{'id':'q0002','text':'Which city?'},{'id':'q0003','text':'Who wrote this?'}]}
    # Use a real named prototype coordinate, with explicitly synthetic fixture public text.
    prototype=s.inputs()[0][0];context={**prototype,**context,'id':prototype['id']}
    code='''import json
from rlm.api import run as rlm
from batch_contract import request_for
records=json.load(open('records.json'))
for chosen in (records[:2],records[:2],records[:1],[dict(records[0],text='changed public text')]):
    returned=await rlm(request_for(chosen))
    print(returned.answer)
'''
    async def provider(request):
        body=await request.json();calls.append({'arm':current['arm'],'body':body});text=tok.decode(body['token_ids'])
        if body['model']==binding['fixed_child']:
            index=current['child'];current['child']+=1
            grammar=body['sampling_params'].get('structured_outputs')
            if index<3:
                assert grammar is not None
                assert grammar['json']['required']==(['q0001','q0002'] if index<2 else ['q0001'])
            else:assert grammar is None
            completion=json.dumps({'q0001':'numeric value','q0002':'location'} if index<2 else {'q0001':'location'},separators=(',',':'))
        elif current['root']==0:
            assert body['sampling_params'].get('structured_outputs') is None
            current['root']+=1;completion=st.native.tool_action(code)
        else:
            assert body['sampling_params'].get('structured_outputs') is None
            assert 'Traceback' not in text
            assert ('[Harness accumulation ledger' in text)==(current['arm']=='ledger')
            completion='Answer: 1'
        ids=tok.encode(completion,add_special_tokens=False)+[151645]
        return web.json_response({'request_id':f'LEDGER_CPU_{len(calls)}','choices':[{'token_ids':ids,'finish_reason':'stop',
            'logprobs':{'content':[{'token':f'token_id:{t}','logprob':-.5} for t in ids]}}]})
    async def models(request):return web.json_response({'data':[{'id':a,'max_model_len':8192} for a in binding['models']]})
    app=web.Application();app.router.add_post('/inference/v1/generate',provider);app.router.add_get('/v1/models',models)
    runner=web.AppRunner(app);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start()
    os.environ['LEDGER_CPU_KEY']='synthetic-fixture-not-secret'
    endpoint={**st.native.e.old.planned_endpoint(binding),'url':f'http://127.0.0.1:{site._server.sockets[0].getsockname()[1]}/v1','api_key_env':'LEDGER_CPU_KEY'}
    plan=[{'id':'cpu-'+arm,'arm':arm,'context_window_id':st.prior.context_window_id(context),
           'seed':s.SEEDS[0],'temperature':.5,'client_path':'train'} for arm in ('map','ledger')]
    try:
        async with asyncio.timeout(360):
            for row in plan:
                current.update(arm=row['arm'],root=0,child=0);target=output/row['arm']
                task=adapter.task(context,'Use records.json and batch_contract.py. Return only Answer: N.',1,'cpu-ledger',row)
                env=SingleAgentEnv(SingleAgentEnvConfig.model_validate(adapter.environment()))
                with adapter.installed(binding,target,[row],{context['id']:context}) as interface:
                    async with env.serving():
                        episode=await asyncio.wait_for(env.run_slot(RunSlot(task),interface.e.make_context(endpoint,row)),170)
                        raw=episode.to_record()
                s.write(target/'EPISODE.json',raw)
                roots,turns=st.exporter.episode_turns(raw,target,binding)
                assert len(roots)==2 and len(turns)==6
                events=[json.loads(line) for line in raw['traces'][0]['info']['accumulation_ledger']['raw'].splitlines()]
                delivered=[e for e in events if e['event']=='delivered'];observed=[e for e in events if e['event']=='root_observation']
                assert len(delivered)==4 and sum(e['eligible'] for e in delivered)==3
                last=delivered[-1]['summary'];assert (last['unique_seen'],last['resolved'],last['conflicts'],last['unqueried'])==(2,1,1,1)
                assert last['counts']=={'human being':0,'location':1,'abbreviation':0,'entity':0,'description and abstract concept':0,'numeric value':0}
                assert len(observed)==1 and observed[0]['appended_summary']==(row['arm']=='ledger')
                for event in (e for e in events if e['event']=='child_result'):
                    matches=[v for v in turns if v['role_depth']==1 and v['role_audit']['invocation']==event['child_invocation']]
                    assert len(matches)==1
                    physical=s.read(matches[0]['role_audit']['source_audit_path'])
                    # Decoded native completion includes only the unchanged map (special stop token omitted).
                    assert physical['native_response']['message']['content']==event['raw_answer']
                proofs.append({'arm':row['arm'],'native_graph_turns':len(turns),'root_turns':len(roots),'delivered':4,
                    'source_valid':3,'summary':last,'root_invocation':events[0]['root_invocation'],'actual_observation':observed[0],
                    'synthetic_fixture_only':True})
        left=[c['body'] for c in calls if c['arm']=='map'];right=[c['body'] for c in calls if c['arm']=='ledger']
        assert len(left)==len(right)==6
        assert all(a==b for a,b in zip(left[:5],right[:5],strict=True))
        assert proofs[0]['root_invocation']!=proofs[1]['root_invocation']
        assert proofs[0]['actual_observation']['original_truncated']==proofs[1]['actual_observation']['original_truncated']
        s.write(output/'RESULT.json',{'status':'PASS','proofs':proofs,'initial_root_and_four_child_wires_equal':True,
            'provider_calls':12,'actual_model_calls':0,'gpu_calls':0,'elapsed_seconds':time.time()-started,'cap_seconds':360})
    except BaseException as error:
        s.write(output/'FAILURE.json',{'type':type(error).__name__,'message':str(error),'elapsed_seconds':time.time()-started,'provider_calls':len(calls)});raise
    finally:s.write(output/'PROVIDER_REQUESTS.json',calls);await runner.cleanup()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    asyncio.run(qualify(p.parse_args().output))
