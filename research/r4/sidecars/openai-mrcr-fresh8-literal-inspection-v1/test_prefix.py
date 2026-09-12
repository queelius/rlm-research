"""One actual environment/native prefix fixture; no model inference or generated tool code."""
import asyncio
import importlib.util
import os
from pathlib import Path
import sys
from aiohttp import web

ROOT=Path(__file__).resolve().parent


def load_modules():
    assert (ROOT/'study.py').exists(),'literal-inspection sidecar absent'
    for name in ('study','checkpoint','collect'):
        spec=importlib.util.spec_from_file_location(name,ROOT/(name+'.py'))
        value=importlib.util.module_from_spec(spec);sys.modules[name]=value;spec.loader.exec_module(value)
    return sys.modules['study'],sys.modules['collect']


def test_actual_environment_uses_only_appended_instruction_and_new_frozen_prefix(tmp_path,monkeypatch):
    asyncio.run(actual_fixture(tmp_path,monkeypatch))


async def actual_fixture(tmp_path,monkeypatch):
    s,c=load_modules()
    from transformers import AutoTokenizer
    from verifiers.v1.env import RunSlot
    monkeypatch.setenv('CUDA_VISIBLE_DEVICES','');monkeypatch.setenv('LITERAL_CPU_KEY','cpu-fixture-only')
    monkeypatch.setenv('PATH',str(s.source().RUNTIME_BIN)+os.pathsep+os.environ.get('PATH',''))
    monkeypatch.setenv('VERIFIERS_CACHE_DIR','/project/alex_phd/cache/verifiers-prime')
    coordinate=s.schedule('train')[0];env=s.environment('train');tasks={v.data.name:v for v in env.taskset}
    old_tasks=s.read(s.CONTROL/'inputs/train/tasks.json');new_tasks=s.read(s.INPUTS/'train/tasks.json')
    old_plan=s.read(s.CONTROL/'inputs/train/PUBLIC.json')['plan'];plan=s.schedule('train')
    assert len(tasks)==len(plan)==32 and [r['seed'] for r in plan]==list(range(202609250000,202609250032))
    for before,after,old_row,row in zip(old_tasks,new_tasks,old_plan,plan):
        assert after['prompt']==before['prompt']+'\n\n'+s.INSPECT_RULE
        assert {k:v for k,v in before.items() if k not in ('name','prompt')}=={k:v for k,v in after.items() if k not in ('name','prompt')}
        assert tasks[row['id']].data.prompt==after['prompt']
        assert {k:v for k,v in row.items() if k not in ('id','study')}=={k:v for k,v in old_row.items() if k not in ('id','study')}
    tokenizer=AutoTokenizer.from_pretrained(str(s.BASE),local_files_only=True);answer='CPU_LITERAL_PREFIX_OK  ';requests=[]
    async def provider(request):
        body=await request.json();requests.append(body);assert request.headers['Authorization']=='Bearer cpu-fixture-only'
        assert body['sampling_params']['temperature']==.5 and body['sampling_params']['max_tokens']==2048
        assert body['sampling_params']['seed']==202609250000
        ids=tokenizer.encode(answer,add_special_tokens=False)+[tokenizer.eos_token_id]
        return web.json_response({'request_id':'CPU_LITERAL_1','usage':{'prompt_tokens':len(body['token_ids']),'completion_tokens':len(ids),'total_tokens':len(body['token_ids'])+len(ids)},
            'choices':[{'token_ids':ids,'finish_reason':'stop','logprobs':{'content':[{'token':'token_id:'+str(i),'logprob':-.5} for i in ids]}}]})
    app=web.Application();app.router.add_post('/inference/v1/generate',provider);runner=web.AppRunner(app);await runner.setup()
    site=web.TCPSite(runner,'127.0.0.1',0);await site.start()
    binding=c.checkpoint.binding('checkpoint32');root=binding['models'][s.ADAPTED_ALIAS]
    assert binding==s.read(s.CONTROL/'outputs/attempt-001/owned-service/BINDING.json')
    endpoint={'model_alias':s.ADAPTED_ALIAS,'host':'127.0.0.1','port':site._server.sockets[0].getsockname()[1],
              'api_key_env':'LITERAL_CPU_KEY','base_model':{'path':str(s.BASE)},
              'adapter':{'path':root['path'],'model_sha256':root['adapter_sha256'],'config_sha256':root['config_sha256']}}
    try:
        with c.hooks.installed(),c.native_checkpoints(tmp_path/'native-calls',set(binding['models'])) as native:
            with c.role_hooks().installed_hooks(binding,tmp_path):
                async with env.serving():episode=await asyncio.wait_for(env.run_slot(RunSlot(tasks[coordinate['id']]),c.model_context(endpoint,coordinate)),180)
        raw=episode.to_record()
    finally:await runner.cleanup()
    prefix=s.read(s.INPUTS/'train/PREFIXES.json')[coordinate['id']]['token_ids']
    old_prefix=s.read(s.CONTROL/'inputs/train/PREFIXES.json')[old_plan[0]['id']]['token_ids']
    assert len(requests)==len(native)==1 and requests[0]['token_ids']==prefix and prefix!=old_prefix
    assert raw['traces'][0]['root_reply']==answer
    s.write_x(tmp_path/'EPISODE.json',raw)
    s.write_x(tmp_path/'PREFIX_PROOF.json',{'all32_environment_tasks_checked':True,'actual_new_native_prefix':True,'old_prefix_rejected':True,
                 'same_checkpoint_binding':True,'same_seed':True,'terminal_spaces_preserved':True,'physical_fake_calls':1,'GPU_calls':0})
