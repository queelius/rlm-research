"""Authored CPU native runtime fixture, never scientific sampled-code execution."""
import asyncio
import importlib.util
import json
from pathlib import Path
import time

def test_authored_native_file_child_reduction_final(tmp_path,monkeypatch):
    path=Path(__file__).with_name('ct_collect.py');assert path.exists(),'qualified free collector missing'
    import ct_study as s
    import ct_collect as c
    from aiohttp import web
    monkeypatch.setenv('STRICT_RLM_CALIBRATION_API_KEY','CPU_FIXTURE_NOT_CREDENTIAL');monkeypatch.setenv('DOSE_CPU_KEY','CPU_FIXTURE_NOT_CREDENTIAL')
    async def fixture():
        row=next(r for r in s.read(s.ROOT/'inputs/FREE_PLAN.json') if r['stratum']=='root_new' and r['operator']=='conditional_weight')
        context=next(x for x in s.read(s.ROOT/'inputs/PUBLIC.json') if x['id']==row['context_id']);binding=s.binding('sft6')
        tokenizer=s.stack().native.renderer()._tokenizer;roots=[];children=[]
        fixture_labels={r['id']:row['target'] if i<4 else row['target_b'] for i,r in enumerate(context['records'])}
        a_users={r['user'] for r in context['records'][:4]}
        expected=sum(r['weight'] for r in context['records'][4:] if r['user'] in a_users)
        assert len(a_users)==4 and expected>0
        code1='import json\nfrom rlm.api import run as rlm\nfrom batch_contract import request_for, strict_map\nrecords=json.load(open("records.json"))\nchild=await rlm(request_for(records))\nlabels=strict_map(child.answer,[r["id"] for r in records])\nprint(json.dumps(labels,sort_keys=True))'
        code2=f'eligible={{r["user"] for r in records if labels[r["id"]]=={row["target"]!r}}}\nanswer=sum(r["weight"] for r in records if r["user"] in eligible and labels[r["id"]]=={row["target_b"]!r})\nprint(answer)'
        async def provider(request):
            body=await request.json()
            if body['model']==binding['role_map']['root']:
                roots.append(body);assert body['sampling_params']['max_tokens']==2048
                if len(roots)==1:
                    assert body['token_ids']==s.read(s.ROOT/'inputs/PROMPTS_ACCURATE.json')[row['id']]['token_ids'];reply=s.stack().native.tool_action(code1)
                elif len(roots)==2:reply=s.stack().native.tool_action(code2)
                elif len(roots)==3:reply='Answer: '+str(expected)
                else:raise AssertionError('unexpected root request')
            else:
                assert body['model']==binding['fixed_child'];children.append(body)
                ids=body['sampling_params']['structured_outputs']['json']['required'];assert set(ids)=={r['id'] for r in context['records']}
                reply=json.dumps({key:fixture_labels[key] for key in ids})
            ids=tokenizer.encode(reply,add_special_tokens=False)+[151645]
            return web.json_response(dict(request_id='DOSE_CPU_'+str(len(roots)+len(children)),usage=dict(prompt_tokens=len(body['token_ids']),completion_tokens=len(ids)),choices=[dict(token_ids=ids,finish_reason='stop',logprobs=dict(content=[dict(token=f'token_id:{v}',logprob=-.5) for v in ids]))]))
        async def models(request):return web.json_response(dict(data=[dict(id=a,root=v['path'],max_model_len=8192) for a,v in binding['models'].items()]))
        app=web.Application();app.router.add_post('/inference/v1/generate',provider);app.router.add_get('/v1/models',models);runner=web.AppRunner(app);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start()
        descriptor=dict(host='127.0.0.1',port=site._server.sockets[0].getsockname()[1],api_key_env='DOSE_CPU_KEY')
        try:
            await c.implementation().episode(row,context,binding,descriptor,tmp_path/'native',time.time()+120,'free')
            result=s.read(tmp_path/'native/RESULT.json');assert result['available'] and result['final_branch_token_identity_verified'] and result['reply']=='Answer: '+str(expected)
            assert result['gold']==s.answer(context['records'],s.read(s.ROOT/'inputs/HOST_GOLD.json')[context['id']]['labels'],row)
            assert len(roots)==3 and len(children)==1
            trace=s.read(tmp_path/'native/EPISODE.json')['traces'][0]
            assert any(str(expected) in str(n['message'].get('content')) for n in trace['nodes'] if n['message'].get('role')=='tool')
        finally:await runner.cleanup()
    asyncio.run(fixture())
