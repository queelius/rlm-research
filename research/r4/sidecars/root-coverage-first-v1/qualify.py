"""One native rootless CPU fixture: partial coverage then complete counts,5 calls."""
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
    output.mkdir(parents=True,exist_ok=False);started=time.time();calls=[];current={'root':0,'child':0}
    os.sched_setaffinity(0,{34,35});st=s.stack();binding=s.binding('efab')
    tok=create_renderer(load_tokenizer(str(st.prior.BASE)),Qwen3RendererConfig(enable_thinking=True))._tokenizer
    prototype=s.inputs()[0][0]
    context={**prototype,'text':'fixture public records','records':[{'id':'q0001','text':'How many planets?'},
        {'id':'q0002','text':'Which city?'},{'id':'q0003','text':'Who wrote this?'}]}
    codes=["import json\nfrom rlm.api import run as rlm\nfrom batch_contract import request_for\nrecords=json.load(open('records.json'))\nreturned=await rlm(request_for(records[:2]))\nprint(returned.answer)",
           "returned=await rlm(request_for(records[2:]))\nprint(returned.answer)"]
    async def provider(request):
        body=await request.json();calls.append({'body':body});text=tok.decode(body['token_ids'])
        if body['model']==binding['fixed_child']:
            index=current['child'];current['child']+=1
            grammar=body['sampling_params'].get('structured_outputs')
            assert grammar['json']['required']==(['q0001','q0002'] if index==0 else ['q0003'])
            completion=json.dumps({'q0001':'numeric value','q0002':'location'} if index==0 else {'q0003':'human being'},separators=(',',':'))
        else:
            assert body['model']==binding['role_map']['root'] and body['sampling_params'].get('structured_outputs') is None
            index=current['root'];current['root']+=1
            if index:
                suffix=text.rsplit('[Harness accumulation ledger',1)[1]
                assert ('"counts":' in suffix)==(index==2)
                assert ('"partial":false' in suffix)==(index==2)
                assert 'Traceback' not in text
            completion=st.native.tool_action(codes[index]) if index<2 else 'Answer: 1'
        ids=tok.encode(completion,add_special_tokens=False)+[151645]
        return web.json_response({'request_id':f'COVERAGE_CPU_{len(calls)}','choices':[{'token_ids':ids,'finish_reason':'stop',
            'logprobs':{'content':[{'token':f'token_id:{token}','logprob':-.5} for token in ids]}}]})
    async def models(request):return web.json_response({'data':[{'id':a,'max_model_len':8192} for a in binding['models']]})
    app=web.Application();app.router.add_post('/inference/v1/generate',provider);app.router.add_get('/v1/models',models)
    runner=web.AppRunner(app);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start()
    os.environ['COVERAGE_CPU_KEY']='synthetic-fixture-not-secret'
    endpoint={**st.native.e.old.planned_endpoint(binding),'url':f'http://127.0.0.1:{site._server.sockets[0].getsockname()[1]}/v1','api_key_env':'COVERAGE_CPU_KEY'}
    row={'id':'cpu-coverage-first','arm':'coverage_first','weight':'efab','context_id':context['id'],
        'context_window_id':st.prior.context_window_id(context),'seed':s.SEEDS[0],'temperature':.5,'client_path':'train'}
    try:
        async with asyncio.timeout(180):
            task=adapter.task(context,'Use records.json and batch_contract.py. Return only Answer: N.',1,'cpu-coverage',row)
            env=SingleAgentEnv(SingleAgentEnvConfig.model_validate(adapter.environment()))
            with adapter.installed(binding,output,[row],{context['id']:context}) as interface:
                async with env.serving():
                    raw=(await env.run_slot(RunSlot(task),interface.e.make_context(endpoint,row))).to_record()
            s.write(output/'EPISODE.json',raw)
            roots,turns=st.exporter.episode_turns(raw,output,binding)
            assert len(roots)==3 and len(turns)==5 and len(calls)==5
            trace=raw['traces'][0];events=[json.loads(line) for line in trace['info']['accumulation_ledger']['raw'].splitlines()]
            observations=[e for e in events if e['event']=='root_observation']
            assert len(observations)==2
            assert 'counts' not in observations[0]['displayed_summary']
            assert observations[1]['displayed_summary']==observations[1]['summary'] and not observations[1]['summary']['partial']
            for event in observations:
                nodes=[n for n in trace['nodes'] if n.get('message',{}).get('role')=='tool' and n['message'].get('content')==event['actual_content']]
                assert len(nodes)==1 and not nodes[0]['sampled'] and not any(nodes[0]['mask']) and not nodes[0]['logprobs']
            for event in (e for e in events if e['event']=='child_result'):
                matches=[v for v in turns if v['role_depth']==1 and v['role_audit']['invocation']==event['child_invocation']]
                assert len(matches)==1 and s.read(matches[0]['role_audit']['source_audit_path'])['native_response']['message']['content']==event['raw_answer']
            s.write(output/'RESULT.json',{'status':'PASS','provider_calls':5,'actual_model_calls':0,'gpu_calls':0,
                'root_turns':3,'child_turns':2,'native_graph_exact':True,'partial_omits_counts':True,'complete_exposes_all_counts':True,
                'observations':observations,'elapsed_seconds':time.time()-started,'cap_seconds':180,'synthetic_fixture_not_training_data':True})
    except BaseException as error:
        s.write(output/'FAILURE.json',{'type':type(error).__name__,'message':str(error),'elapsed_seconds':time.time()-started,'provider_calls':len(calls)});raise
    finally:s.write(output/'PROVIDER_REQUESTS.json',calls);await runner.cleanup()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);asyncio.run(qualify(p.parse_args().output))
