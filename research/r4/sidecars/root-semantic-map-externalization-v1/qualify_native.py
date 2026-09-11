"""Two real ACP/IPython CPU fixtures with authored transport, never scientific models."""
import argparse
import asyncio
import json
import os
from pathlib import Path
import time
from aiohttp import web
import sm_study as s
import sm_protocol as p
import sm_native as n
import sm_collect as c

async def qualify(output):
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv,SingleAgentEnvConfig
    output.mkdir(parents=True,exist_ok=False);started=time.time();value=p.build();context=value['PUBLIC.json'][0]
    rows=[{**row,'id':'SM_CPU_'+str(i)} for i,row in enumerate(value['PLAN.json'][:2])];query=value['QUERIES.json'][rows[0]['task_name']]
    labels={r['id']:query['query']['target'] for r in context['records']};maps=json.dumps(labels,indent=2)
    tasks={r['id']:n.task(context,query['question'],r,maps) for r in rows};expectations={r['id']:n.expected(tasks[r['id']],r) for r in rows}
    binding=s.binding();root=binding['role_map']['root'];child=binding['fixed_child'];tokenizer=s.qnative().stack().native.renderer()._tokenizer
    calls=[];counts={};ids=[r['id'] for r in context['records'][:4]];expected_scalar=p.answer(context['records'],labels,query['query'])
    code=('import json\nfrom rlm.api import run as rlm\nfrom batch_contract import request_for, strict_map\nrecords = json.load(open("records.json"))\nlabels = json.load(open("labels.json"))\nquery = open("query.txt").read()\nbatch = records[:4]\nchild = await rlm(request_for(batch))\nnew_prediction = strict_map(child.answer, [r["id"] for r in batch])\nanswer = sum(labels[r["id"]] == '+repr(query['query']['target'])+' for r in records if r["user"] in '+repr(query['query']['users'])+')\nprint(answer)')
    active=[None]
    async def provider(request):
        body=await request.json();calls.append(dict(coordinate=active[0],body=body));identifier=active[0]
        if body['model']==child:
            grammar=body['sampling_params']['structured_outputs']['json'];assert grammar['required']==ids
            reply=json.dumps({key:'entity' for key in ids})
        else:
            assert body['model']==root and 'structured_outputs' not in body['sampling_params'] and body['sampling_params']['max_tokens']==2048
            count=counts.get(identifier,0);counts[identifier]=count+1
            if count==0:assert body['token_ids']==expectations[identifier]['token_ids']
            reply=s.qnative().stack().native.tool_action(code) if count==0 else 'Answer: '+str(expected_scalar)
        tokens=tokenizer.encode(reply,add_special_tokens=False)+[151645]
        return web.json_response(dict(request_id='SM_CPU_ONLY_'+str(len(calls)),usage=dict(prompt_tokens=len(body['token_ids']),completion_tokens=len(tokens),total_tokens=len(body['token_ids'])+len(tokens)),choices=[dict(token_ids=tokens,finish_reason='stop',logprobs=dict(content=[dict(token=f'token_id:{t}',logprob=-.5) for t in tokens]))]))
    async def models(request):return web.json_response(dict(data=[dict(id=alias,max_model_len=8192) for alias in binding['models']]))
    app=web.Application();app.router.add_post('/inference/v1/generate',provider);app.router.add_get('/v1/models',models);runner=web.AppRunner(app);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start()
    endpoint=dict(url=f'http://127.0.0.1:{site._server.sockets[0].getsockname()[1]}/v1',model=root,renderer_model=str(s.qnative().stack().prior.BASE),api_key_env='SM_CPU_PROVIDER_KEY')
    before={k:os.environ.get(k) for k in ('STRICT_RLM_CALIBRATION_API_KEY','SM_CPU_PROVIDER_KEY')}
    for key in before:os.environ[key]='cpu-fixture-not-credential'
    try:
        interface=n.interface(output);attestations=[]
        with n.installed(interface,binding,output,rows,{context['id']:context},expectations):
            env=SingleAgentEnv(SingleAgentEnvConfig.model_validate(n.environment_config(interface)))
            async with env.serving():
                for row in rows:
                    active[0]=row['id'];raw=(await asyncio.wait_for(env.run_slot(RunSlot(tasks[row['id']]),n.make_context(interface,endpoint,row)),120)).to_record();s.write(output/(row['id']+'.json'),raw)
                    trace=raw['traces'][0];roles={k:v for k,v in c.audits(output).items() if v['coordinate']['id']==row['id']};capture,indices=c.metrics().final_capture(trace,roles)
                    assert c.terminal(trace,capture,expected_scalar)['reward']==1 and len(roles)==3
                    assert sum(r['depth']>0 for r in roles.values())==1
                    attestation=trace['info']['semantic_map_setup'];assert attestation['plain_query']==query['question'];attestations.append(attestation['file_sha256'])
                    assert any(node['message'].get('role')=='tool' and str(expected_scalar) in node['message'].get('content','') for node in trace['nodes'])
        assert len(calls)==6 and attestations[0]==attestations[1]
        s.write(output/'RESULT.json',dict(passed=True,actual_native_episodes=2,native_calls=6,child_calls=2,root_calls=4,common_file_sha256=attestations[0],actual_model_calls=0,gpu_calls=0,model_service_calls=0,all_first_prefixes_and_final_branches_verified=True,root_role_unchanged=True,authored_code=code,elapsed_seconds=time.time()-started,source_sha256={str(path):s.sha(path) for path in s.ROOT.glob('*.py')}))
        print(dict(passed=True,cpu_native_calls=6,elapsed_seconds=time.time()-started))
    except BaseException as error:s.write(output/'FAILURE.json',dict(type=type(error).__name__,message=str(error)));raise
    finally:
        s.write(output/'PROVIDER_REQUESTS.json',calls);await runner.cleanup()
        for key,value in before.items():
            if value is None:os.environ.pop(key,None)
            else:os.environ[key]=value
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();asyncio.run(qualify(args.output))
