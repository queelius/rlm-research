"""Authored CPU provider through actual ACP/IPython; no sampled code/model service."""
import argparse
import asyncio
import json
import os
from pathlib import Path
import time
from aiohttp import web
import study as s
import protocol as p
import native as n
import collect as c

async def qualify(output):
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv,SingleAgentEnvConfig
    output.mkdir(parents=True,exist_ok=False);started=time.time();value=p.build();original=next(r for r in value['PLAN.json'] if r['root']=='released_reference');context=next(c for c in value['PUBLIC.json'] if c['id']==original['context_id'])
    rows=[{**original,'id':'WARM_REFERENCE_CPU_0'}]
    tasks={r['id']:n.task(context,value['QUERIES.json'][r['task_name']]['question'],r) for r in rows}
    expected={r['id']:n.expected(tasks[r['id']],r) for r in rows};binding=s.binding('released_reference');root=binding['role_map']['root'];child=binding['fixed_child']
    tokenizer=s.qnative().stack().native.renderer()._tokenizer;calls=[];root_counts={};ids=[r['id'] for r in context['records'][:4]]
    code='import json\nfrom rlm.api import run as rlm\nfrom batch_contract import request_for, strict_map\nrecords = json.load(open("records.json"))\nbatch = records[:4]\nchild = await rlm(request_for(batch))\nlabels = strict_map(child.answer, [r["id"] for r in batch])\nprint(labels)'
    active=[None]
    async def provider(request):
        body=await request.json();calls.append(dict(coordinate=active[0],body=body));row_id=active[0]
        if body['model']==child:
            grammar=body['sampling_params']['structured_outputs']['json']
            assert list(grammar['properties'])==ids and grammar['required']==ids
            reply=json.dumps({key:'entity' for key in ids})
        else:
            assert body['model']==root and 'structured_outputs' not in body['sampling_params'] and body['sampling_params']['max_tokens']==2048
            count=root_counts.get(row_id,0);root_counts[row_id]=count+1
            if count==0:assert body['token_ids']==expected[row_id]['token_ids']
            reply=s.qnative().stack().native.tool_action(code) if count==0 else 'Answer: 0'
        tokens=tokenizer.encode(reply,add_special_tokens=False)+[151645]
        return web.json_response(dict(request_id='WARM_REFERENCE_CPU_ONLY_'+str(len(calls)),usage=dict(prompt_tokens=len(body['token_ids']),completion_tokens=len(tokens),total_tokens=len(body['token_ids'])+len(tokens)),choices=[dict(token_ids=tokens,finish_reason='stop',logprobs=dict(content=[dict(token=f'token_id:{t}',logprob=-.5) for t in tokens]))]))
    async def models(request):return web.json_response(dict(data=[dict(id=alias,max_model_len=8192) for alias in binding['models']]))
    app=web.Application();app.router.add_post('/inference/v1/generate',provider);app.router.add_get('/v1/models',models)
    runner=web.AppRunner(app);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start()
    endpoint=dict(url=f'http://127.0.0.1:{site._server.sockets[0].getsockname()[1]}/v1',model=root,renderer_model=str(s.qnative().stack().prior.BASE),api_key_env='WARM_REFERENCE_CPU_PROVIDER_KEY')
    before={k:os.environ.get(k) for k in ('STRICT_RLM_CALIBRATION_API_KEY','WARM_REFERENCE_CPU_PROVIDER_KEY')}
    for key in before:os.environ[key]='cpu-fixture-not-credential'
    try:
        interface=n.interface(output);episodes=[]
        with n.installed(interface,binding,output,rows,{context['id']:context},expected):
            env=SingleAgentEnv(SingleAgentEnvConfig.model_validate(n.environment_config(interface)))
            async with env.serving():
                for row in rows:
                    active[0]=row['id'];raw=(await asyncio.wait_for(env.run_slot(RunSlot(tasks[row['id']]),n.make_context(interface,endpoint,row)),120)).to_record()
                    s.write(output/(row['id']+'.json'),raw);episodes.append(raw)
                    trace=raw['traces'][0];assert trace['root_reply']=='Answer: 0',raw
                    roles={k:v for k,v in c.audits(output).items() if v['coordinate']['id']==row['id']}
                    capture,indices=c.metrics().final_capture(trace,roles)
                    assert c.terminal(trace,capture,0)['reward']==1
                    assert len(roles)==3 and sum(r['depth']>0 for r in roles.values())==1
                    assert trace['info']['warm_reference_setup']['file_sha256']['records.json']==__import__('hashlib').sha256(json.dumps(context['records'],ensure_ascii=False).encode()).hexdigest()
                    child_record=next(v for v in roles.values() if v['depth']>0)
                    assert child_record['actual_alias']==child
        assert len(calls)==3
        records=list(c.audits(output).values());assert c.cost(records)['returned_native_completions']==3
        first=next(v for v in records if v.get('first_prefix_verified'))
        assert first['native_request']['messages'][0]==expected[rows[0]['id']]['messages'][0]
        s.write(output/'RESULT.json',dict(passed=True,actual_native_episodes=1,native_calls=3,child_calls=1,root_calls=2,all_first_prefixes_verified=True,child_typed_grammar_unchanged=True,child_system_unchanged=True,exact_public_files=True,authored_code=code,gpu_calls=0,model_service_calls=0,elapsed_seconds=time.time()-started,source_sha256={str(s.ROOT/name):s.sha(s.ROOT/name) for name in ('study.py','protocol.py','native.py','collect.py','qualify_native.py')}))
        print(dict(passed=True,native_calls=3,elapsed_seconds=time.time()-started))
    except BaseException as error:
        s.write(output/'FAILURE.json',dict(type=type(error).__name__,message=str(error),elapsed_seconds=time.time()-started));raise
    finally:
        s.write(output/'PROVIDER_REQUESTS.json',calls);await runner.cleanup()
        for key,value in before.items():
            if value is None:os.environ.pop(key,None)
            else:os.environ[key]=value
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();asyncio.run(qualify(args.output))
