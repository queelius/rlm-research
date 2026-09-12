"""Actual checkpoint/native/entry seams; only model HTTP output is simulated."""
import asyncio
import importlib
import json
import os
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parent

def modules():
    assert (ROOT/'collect.py').exists(), 'checkpoint16 collector not implemented'
    return tuple(importlib.import_module(n) for n in ('study','checkpoint','collect'))

def test_cp16_actual_binding_and_inner_entry_after_real_verification(tmp_path,monkeypatch):
    s,k,c=modules();receipt=k.verify_checkpoint();binding=k.binding('checkpoint16')
    assert receipt['selected_step']==16 and receipt['optimizer_state_steps']==[16]
    assert binding['role_map']['root']=='Qwen3-4B-Instruct-2507-mrcr-procedural-sft-step16'
    assert binding['models'][binding['role_map']['root']]['adapter_sha256']=='9f68605f023d637bfecc088e169eea0a31d0ea2b4e88a9db56a3e5d74dc2c9e5'
    with pytest.raises(ValueError):k.binding('checkpoint32')
    values=s.schedule('train');assert [v['seed'] for v in values]==list(range(202609200000,202609200032))
    old=s.read(s.ORIGINAL/'inputs/train/PREFIXES.json');new=s.read(s.input_dir('train')/'PREFIXES.json')
    old_plan=s.read(s.ORIGINAL/'inputs/train/PUBLIC.json')['plan']
    for a,b in zip(old_plan,values,strict=True):
        assert a['record_id']==b['record_id'] and a['repeat']==b['repeat'] and a['seed']==b['seed']
        assert old[a['id']]['token_ids']==new[b['id']]['token_ids']
    endpoint=tmp_path/'endpoint.json';endpoint.write_text('{}')
    class Reached(Exception):pass
    def boundary(arm):
        assert arm=='checkpoint16';raise Reached()
    inner=c.source.source
    assert inner.run.__globals__['verify_ready'] is c.verify_ready
    monkeypatch.setattr(inner.checkpoint,'binding',boundary)
    with pytest.raises(Reached):asyncio.run(c.run('train','checkpoint16',endpoint,tmp_path/'unused',10**10))
    assert not (tmp_path/'unused').exists()

def test_actual_native_cp16_alias_tool_then_final_preserves_boundaries(tmp_path,monkeypatch):
    s,k,c=modules()
    async def run():
        from aiohttp import web
        from transformers import AutoTokenizer
        from verifiers.v1.env import RunSlot
        os.environ['PATH']=str(s.source().RUNTIME_BIN)+os.pathsep+os.environ.get('PATH','')
        os.environ.setdefault('VERIFIERS_CACHE_DIR','/project/alex_phd/cache/verifiers-prime')
        coordinate=s.schedule('train')[0];env=s.environment('train')
        task=next(t for t in env.taskset if t.data.name==coordinate['id'])
        tok=AutoTokenizer.from_pretrained(str(s.BASE),local_files_only=True)
        final='MARK native cp16 fixture  '
        replies=['<tool_call>\n'+json.dumps({'name':'ipython','arguments':{'code':"print('CPU_CP16_OK')"}})+'\n</tool_call>',final]
        requests=[]
        async def provider(request):
            body=await request.json();requests.append(body);assert len(requests)<=2
            ids=tok.encode(replies[len(requests)-1],add_special_tokens=False)+[tok.eos_token_id]
            return web.json_response({'request_id':'CPU_CP16_'+str(len(requests)),
                'usage':{'prompt_tokens':len(body['token_ids']),'completion_tokens':len(ids),'total_tokens':len(body['token_ids'])+len(ids)},
                'choices':[{'token_ids':ids,'finish_reason':'stop','logprobs':{'content':[{'token':'token_id:'+str(t),'logprob':-.5} for t in ids]}}]})
        app=web.Application();app.router.add_post('/inference/v1/generate',provider)
        runner=web.AppRunner(app);await runner.setup();server=web.TCPSite(runner,'127.0.0.1',0);await server.start()
        binding=k.binding('checkpoint16');root=binding['models'][s.ADAPTED_ALIAS]
        endpoint={'model_alias':s.ADAPTED_ALIAS,'base_model':{'path':str(s.BASE)},
                  'adapter':{'path':root['path'],'model_sha256':root['adapter_sha256'],'config_sha256':root['config_sha256']},
                  'host':'127.0.0.1','port':server._server.sockets[0].getsockname()[1],'api_key_env':'CP16_CPU_ONLY_KEY'}
        monkeypatch.setenv('CP16_CPU_ONLY_KEY','cpu-no-secret')
        try:
            with c.hooks.installed(),c.native_checkpoints(tmp_path/'native-calls',{s.ADAPTED_ALIAS}) as native:
                async with env.serving():
                    ep=await asyncio.wait_for(env.run_slot(RunSlot(task),c.model_context(endpoint,coordinate)),180)
            raw=ep.to_record()
        finally:await runner.cleanup()
        prefix=s.read(s.input_dir('train')/'PREFIXES.json')[coordinate['id']]['token_ids']
        derived=c.original_inspect_trace(raw,{'answer':final,'random_string_to_prepend':'MARK'},native,prefix)
        s.write_x(tmp_path/'EPISODE.json',raw);s.write_x(tmp_path/'DERIVED.json',derived);s.write_x(tmp_path/'REQUESTS.json',requests)
        assert len(native)==2 and derived['root_actions_returned']==2 and derived['child_actions_returned']==0
        assert requests[0]['token_ids']==prefix and requests[0]['model']==s.ADAPTED_ALIAS
        assert native[-1]['response']['message']['content']==raw['traces'][0]['root_reply']==final
        assert derived['raw_exact'] and derived['native_mapping_complete'] and derived['initial_root_prefix_verified']
        assert any('CPU_CP16_OK' in ((n.get('message') or {}).get('content') or '') for n in raw['traces'][0]['nodes'] if (n.get('message') or {}).get('role')=='tool')
    asyncio.run(run())
