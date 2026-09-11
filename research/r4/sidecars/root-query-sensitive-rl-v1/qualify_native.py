"""One authored CPU native proof; synthetic provider likelihoods never scientific."""
import asyncio
import json
import os
import time
from aiohttp import web
import qsr_study as s
import qsr_native as n

async def qualify():
    from verifiers.v1.env import RunSlot
    from verifiers.v1.envs.single_agent import SingleAgentEnv,SingleAgentEnvConfig
    output=s.ROOT/'qualification-native-001';output.mkdir(exist_ok=False);started=time.time()
    public,host=s.data();context=public[0];plan=s.candidate_plan(1);row={**plan[0],'id':'QSR_CPU_NATIVE_HEX4','seed':981381901}
    taskinfo=s.read(s.ROOT/'inputs/TASKS.json')[row['task_name']];task=n.make_task(context,taskinfo['question'],host[context['id']]['answers'][row['family']],row['task_name'])
    old=s.read(s.SIDE/'leaf-role-routing-v1/BOUND_WEIGHTS.json');child='strict-rlm-qwen3-4b-role-sft-selected-v1';root='qsr-CPU-root-low66c';initial=s.fixed_start()
    binding={**old,'models':{root:{k:initial[k] for k in ('path','adapter_sha256','config_sha256')},child:old['models'][child]},'role_map':dict(root=root,children=[child]),'fixed_child':child,'qualification_only':True}
    renderer=n.stack().native.renderer();tokenizer=renderer._tokenizer;calls=[];expected_ids=[r['id'] for r in context['records'][:4]]
    code='import json\nfrom rlm.api import run as rlm\nfrom batch_contract import request_for, strict_map\nrecords = json.load(open("records.json"))\nbatch = records[:4]\nchild = await rlm(request_for(batch))\nlabels = strict_map(child.answer, [r["id"] for r in batch])\nprint(labels)'
    async def provider(request):
        body=await request.json();calls.append(body)
        if body['model']==child:
            grammar=body['sampling_params']['structured_outputs']['json']
            assert list(grammar['properties'])==expected_ids and grammar['required']==expected_ids
            reply=json.dumps({key:'entity' for key in expected_ids})
        else:
            assert 'structured_outputs' not in body['sampling_params']
            reply=n.stack().native.tool_action(code) if len(calls)==1 else 'Answer: 0'
        ids=tokenizer.encode(reply,add_special_tokens=False)+[151645]
        return web.json_response(dict(request_id=f'QSR_CPU_ONLY_{len(calls)}',usage=dict(prompt_tokens=len(body['token_ids']),completion_tokens=len(ids),total_tokens=len(body['token_ids'])+len(ids)),choices=[dict(token_ids=ids,finish_reason='stop',logprobs=dict(content=[dict(token=f'token_id:{v}',logprob=-.5) for v in ids]))]))
    async def models(request):return web.json_response(dict(data=[dict(id=alias,max_model_len=8192) for alias in binding['models']]))
    app=web.Application();app.router.add_post('/inference/v1/generate',provider);app.router.add_get('/v1/models',models);runner=web.AppRunner(app);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start()
    endpoint=dict(url=f'http://127.0.0.1:{site._server.sockets[0].getsockname()[1]}/v1',model=root,renderer_model=n.stack().prior.BASE.as_posix(),api_key_env='QSR_CPU_PROVIDER_KEY')
    before={k:os.environ.get(k) for k in ('STRICT_RLM_CALIBRATION_API_KEY','QSR_CPU_PROVIDER_KEY')}
    os.environ['STRICT_RLM_CALIBRATION_API_KEY']='cpu-fixture-not-credential';os.environ['QSR_CPU_PROVIDER_KEY']='cpu-fixture-not-credential'
    try:
        interface=n.interface(output)
        with interface.installed(binding,output,[row],{context['id']:context}):
            env=SingleAgentEnv(SingleAgentEnvConfig.model_validate(interface.e.environment_config()))
            async with env.serving():raw=(await asyncio.wait_for(env.run_slot(RunSlot(task),interface.e.make_context(endpoint,row)),180)).to_record()
        s.write(output/'EPISODE.json',raw)
        assert len(calls)==3 and calls[0]['token_ids']==taskinfo['first_prompt_token_ids']
        assert raw['traces'][0]['root_reply']=='Answer: 0'
        roots,evidence=n.exact_turns(raw,output,binding,qualification=True)
        assert len(roots)==2 and len(evidence)==3 and sum(t['credited'] for t in evidence)==2
        assert all(t['labels'][:t['prompt_length']]==[-100]*t['prompt_length'] for t in roots)
        try:n.exact_turns(raw,output,binding)
        except ValueError as error:assert 'qualification' in str(error)
        else:raise AssertionError('CPU provider accepted as scientific RL likelihood')
        s.write(output/'RESULT.json',dict(status='PASS',provider_calls=3,root_calls=2,child_calls=1,ids=expected_ids,all_four_public_fields=True,typed_exact_ids=True,actual_native_prefix_equal=True,current_root_suffix_only=True,synthetic_science_admission_rejected=True,authored_code=code,gpu_calls=0,actual_model_calls=0,elapsed_seconds=time.time()-started))
        print(dict(status='PASS',cpu_fake_provider_calls=3,actual_model_calls=0,elapsed_seconds=time.time()-started))
    except BaseException as error:
        s.write(output/'FAILURE.json',dict(type=type(error).__name__,message=str(error),elapsed_seconds=time.time()-started));raise
    finally:
        s.write(output/'PROVIDER_REQUESTS.json',calls);await runner.cleanup()
        for key,value in before.items():
            if value is None:os.environ.pop(key,None)
            else:os.environ[key]=value

if __name__=='__main__':asyncio.run(qualify())
