"""Actual native transport regression; only the model HTTP provider is faked."""

import asyncio
from contextlib import nullcontext
import importlib.util
import json
import os
from pathlib import Path
import sys

from aiohttp import web
import pytest

ROOT=Path(__file__).resolve().parent
PRIOR=ROOT.parent/'openai-mrcr-procedural-sft-continue32-eval-v1'


def prior_modules():
    old=dict(sys.modules)
    modules={}
    try:
        for name in ('study','checkpoint','collect'):
            spec=importlib.util.spec_from_file_location(name,PRIOR/(name+'.py'))
            module=importlib.util.module_from_spec(spec)
            sys.modules[name]=module;spec.loader.exec_module(module);modules[name]=module
    finally:
        for name in ('study','checkpoint','collect'):
            if name in old:sys.modules[name]=old[name]
            else:sys.modules.pop(name,None)
    return modules


def active_hooks():
    if not (ROOT/'hooks.py').exists() or os.environ.get('TERMINAL_STRIP_CONTROL')=='1':
        return nullcontext()
    spec=importlib.util.spec_from_file_location('terminal_strip_test_hooks',ROOT/'hooks.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.installed()


@pytest.mark.parametrize('text,gold,want_exact',[
    ('  MARK\ncurly ’ target  ','  MARK\ncurly ’ target  ',True),
    ('MARK exact  \n\n','MARK exact  ',False),
    ("MARK wrong ' apostrophe",'MARK wrong ’ apostrophe',False),
    ('<tool_call>{bad json}</tool_call>','MARK valid answer',False),
])
def test_native_tool_then_final_preserves_content_without_repair(tmp_path,monkeypatch,text,gold,want_exact):
    async def run():
        from verifiers.v1.env import RunSlot
        from transformers import AutoTokenizer
        modules=prior_modules();s=modules['study'];c=modules['collect'].source
        os.environ['PATH']=str(s.source().RUNTIME_BIN)+os.pathsep+os.environ.get('PATH','')
        os.environ.setdefault('VERIFIERS_CACHE_DIR','/project/alex_phd/cache/verifiers-prime')
        coordinate=s.schedule('held')[0]
        env=s.environment('held')
        task=next(t for t in env.taskset if t.data.name==coordinate['id'])
        tokenizer=AutoTokenizer.from_pretrained(str(s.BASE),local_files_only=True)
        # Authored fixed fixture code, never generated code and no retrieval/gold execution.
        replies=['<tool_call>\n'+json.dumps({'name':'ipython','arguments':{'code':"print('CPU_TOOL_OK')"}})+'\n</tool_call>',text]
        requests=[]
        async def provider(request):
            body=await request.json();requests.append(body)
            assert len(requests)<=2
            ids=tokenizer.encode(replies[len(requests)-1],add_special_tokens=False)+[tokenizer.eos_token_id]
            return web.json_response({'request_id':'CPU_TERMINAL_'+str(len(requests)),
                'usage':{'prompt_tokens':len(body['token_ids']),'completion_tokens':len(ids),'total_tokens':len(body['token_ids'])+len(ids)},
                'choices':[{'token_ids':ids,'finish_reason':'stop','logprobs':{'content':[{'token':'token_id:'+str(t),'logprob':-.5} for t in ids]}}]})
        app=web.Application();app.router.add_post('/inference/v1/generate',provider)
        runner=web.AppRunner(app);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start()
        endpoint={'model_alias':s.ADAPTED_ALIAS,'base_model':{'path':str(s.BASE)},'adapter':None,
                  'host':'127.0.0.1','port':site._server.sockets[0].getsockname()[1],'api_key_env':'TERMINAL_CPU_KEY'}
        monkeypatch.setenv('TERMINAL_CPU_KEY','not-a-real-secret')
        try:
            with active_hooks(), c.native_checkpoints(tmp_path/'native-calls',{s.ADAPTED_ALIAS}) as native:
                async with env.serving():
                    episode=await asyncio.wait_for(env.run_slot(RunSlot(task),c.model_context(endpoint,coordinate)),180)
            raw=episode.to_record()
        finally:
            await runner.cleanup()
        prefix=s.read(s.input_dir('held')/'PREFIXES.json')[coordinate['id']]['token_ids']
        marker='  MARK' if gold.startswith('  MARK') else 'MARK'
        derived=c.inspect_trace(raw,{'answer':gold,'random_string_to_prepend':marker},native,prefix)
        s.write_x(tmp_path/'EPISODE.json',raw);s.write_x(tmp_path/'DERIVED.json',derived)
        s.write_x(tmp_path/'PROVIDER_REQUESTS.json',requests)
        assert len(requests)==2 and len(native)==2
        assert any('CPU_TOOL_OK' in ((n.get('message') or {}).get('content') or '') for n in raw['traces'][0]['nodes'] if (n.get('message') or {}).get('role')=='tool')
        if text=='<tool_call>{bad json}</tool_call>':
            assert native[-1]['response']['message']['content'] is None
            assert raw['traces'][0]['root_reply']==''
            assert derived['failure_class']=='model_invalid_terminal'
        else:
            assert native[-1]['response']['message']['content']==text
            assert raw['traces'][0]['root_reply']==text
        assert derived['raw_exact'] is want_exact
        if want_exact:assert derived['reward']==1.0
        assert derived['initial_root_prefix_verified'] and derived['native_mapping_complete']
    asyncio.run(run())


def test_reasoning_boundary_and_invalid_tool_status_are_unchanged():
    from transformers import AutoTokenizer
    from renderers.qwen3 import Qwen3Renderer
    s=prior_modules()['study'];tokenizer=AutoTokenizer.from_pretrained(str(s.BASE),local_files_only=True)
    renderer=Qwen3Renderer(tokenizer)
    for text in ('<think> thoughts \n</think>\n\n  FINAL  \n',
                 '<tool_call>{bad json}</tool_call>'):
        ids=tokenizer.encode(text,add_special_tokens=False)+[tokenizer.eos_token_id]
        old=renderer.parse_response(ids)
        with active_hooks():new=renderer.parse_response(ids)
        assert new.reasoning_content==old.reasoning_content
        assert new.tool_calls==old.tool_calls
        if not old.tool_calls:assert new.content=='  FINAL  '


def test_hooks_restore_original_parser_after_scope():
    from transformers import AutoTokenizer
    from renderers.qwen3 import Qwen3Renderer
    s=prior_modules()['study'];tokenizer=AutoTokenizer.from_pretrained(str(s.BASE),local_files_only=True)
    renderer=Qwen3Renderer(tokenizer)
    ids=tokenizer.encode('  untouched boundary  ',add_special_tokens=False)+[tokenizer.eos_token_id]
    assert renderer.parse_response(ids).content=='untouched boundary'
    with active_hooks():assert renderer.parse_response(ids).content=='  untouched boundary  '
    assert renderer.parse_response(ids).content=='untouched boundary'
