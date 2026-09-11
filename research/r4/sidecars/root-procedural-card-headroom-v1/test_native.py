"""Actual native acquisition, observed map, executed grouped operation and native final."""
import asyncio
import json
from pathlib import Path
import time
import pytest

@pytest.mark.parametrize('arm',['U','P'])
def test_actual_two_stage_native_prefix_and_execution(tmp_path,monkeypatch,arm):
    assert Path(__file__).with_name('inputs').exists(),'actual frozen48 native inputs absent'
    import ph_study as s
    import ph_collect as c
    from aiohttp import web
    monkeypatch.setenv('STRICT_RLM_CALIBRATION_API_KEY','CPU_FIXTURE_NOT_CREDENTIAL');monkeypatch.setenv('PROCEDURAL_CPU_KEY','CPU_FIXTURE_NOT_CREDENTIAL')
    async def fixture():
        row=next(r for r in s.read(s.ROOT/'inputs/FREE_PLAN.json') if r['operator']=='maximum_weight' and r['card_arm']==arm)
        context=next(x for x in s.read(s.ROOT/'inputs/PUBLIC.json') if x['id']==row['context_id']);binding=s.binding()
        tokenizer=s.stack().native.renderer()._tokenizer;roots=[];children=[]
        target=row['target'];other='entity' if target!='entity' else 'location'
        labels={r['id']:target if i%3==0 else other for i,r in enumerate(context['records'])}
        users={r['user'] for r in context['records']}
        expected=max(sum(r['weight'] for r in context['records'] if r['user']==u and labels[r['id']]==target) for u in users)
        code1='import json\nfrom rlm.api import run as rlm\nfrom batch_contract import request_for, strict_map\nrecords=json.load(open("records.json"))\nchild=await rlm(request_for(records))\nlabels=strict_map(child.answer,[r["id"] for r in records])\nprint(json.dumps(labels,sort_keys=True))'
        code2='totals={r["user"]:0 for r in records}\nfor record in records:\n    if labels[record["id"]]=='+repr(target)+':\n        totals[record["user"]]+=record["weight"]\nanswer=max(totals.values(),default=0)\nprint(answer)'
        async def provider(request):
            body=await request.json()
            if body['model']==binding['role_map']['root']:
                roots.append(body);assert body['sampling_params']['max_tokens']==2048 and body['sampling_params']['temperature']==.5
                if len(roots)==1:assert body['token_ids']==s.read(s.ROOT/'inputs/PROMPTS_ACCURATE.json')[row['id']]['token_ids']
                assert len(roots)<=3
                if len(roots)==2:assert json.loads(c.implementation().messages(tokenizer.decode(body['token_ids']))[-1])==labels
                if len(roots)==3:assert c.implementation().messages(tokenizer.decode(body['token_ids']))[-1].strip()==str(expected)
                reply=s.stack().native.tool_action(code1 if len(roots)==1 else code2) if len(roots)<3 else 'Answer: '+str(expected)
            else:
                assert body['model']==binding['fixed_child'];children.append(body)
                ids=body['sampling_params']['structured_outputs']['json']['required'];assert set(ids)==set(labels)
                reply=json.dumps(labels)
            ids=tokenizer.encode(reply,add_special_tokens=False)+[151645]
            return web.json_response(dict(request_id='PH_CPU_'+str(len(roots)+len(children)),usage=dict(prompt_tokens=len(body['token_ids']),completion_tokens=len(ids)),choices=[dict(token_ids=ids,finish_reason='stop',logprobs=dict(content=[dict(token=f'token_id:{v}',logprob=-.5) for v in ids]))]))
        async def models(request):return web.json_response(dict(data=[dict(id=a,root=v['path'],max_model_len=8192) for a,v in binding['models'].items()]))
        app=web.Application();app.router.add_post('/inference/v1/generate',provider);app.router.add_get('/v1/models',models);runner=web.AppRunner(app);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start()
        descriptor=dict(host='127.0.0.1',port=site._server.sockets[0].getsockname()[1],api_key_env='PROCEDURAL_CPU_KEY')
        try:
            await c.implementation().episode(row,context,binding,descriptor,tmp_path/'native',time.time()+120,'free')
            result=s.read(tmp_path/'native/RESULT.json');assert result['available'] and result['final_branch_token_identity_verified'] and result['reply']=='Answer: '+str(expected)
            assert len(roots)==3 and len(children)==1
            assert result['gold']==s.answer(context['records'],s.read(s.ROOT/'inputs/HOST_GOLD.json')[context['id']]['labels'],row)
        finally:await runner.cleanup()
    asyncio.run(fixture())
