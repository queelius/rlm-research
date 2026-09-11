"""Real native fixture and composed entry: detects wrong aliases, prompts and lost ledger."""
import asyncio
import json
from pathlib import Path
import sys
import time
import pytest

def modules():
    assert Path(__file__).with_name('ae_study.py').exists(),'qualified accumulation study missing'
    import ae_study as s
    return s

def test_files_gold_independence_and_native_prefixes():
    s=modules()
    context=dict(id='CPU',size=2,index=0,stratum='root_new',native_context_id=981799901,records=[dict(id='qa',user='u0',text='Who wrote it?',weight=3),dict(id='qb',user='u1',text='Where is it?',weight=5)])
    context['text']=''.join(json.dumps(r,sort_keys=True)+'\n' for r in context['records'])
    row=dict(id='CPU-task',question='Across all records, how many questions request a human being?',operator='count',target='human being')
    class Memory:
        def __init__(self):self.files={}
        async def write(self,name,data):self.files[name]=data
    async def files(task):
        memory=Memory();await task.setup(None,memory);return memory.files
    original=asyncio.run(files(s.o.qnative().make_task(context,row['question'],0,row['id'])))
    for arm in ('B','C'):
        task=s.make_task(context,{**row,'accumulation_arm':arm},0)
        changed=s.make_task(context,{**row,'accumulation_arm':arm,'gold':'PRIVATE'},9999)
        actual=asyncio.run(files(task))
        assert set(actual)==set(original)
        assert all(actual[k]==original[k] for k in original if k!='batch_contract.py')
        assert actual==asyncio.run(files(changed))
        assert s.o.qnative().first_prefix(task)==s.o.qnative().first_prefix(changed)
        assert actual['batch_contract.py']!=original['batch_contract.py']

def test_exact_owner_collector_main(monkeypatch):
    s=modules()
    assert Path(__file__).with_name('ae_owner.py').exists(),'bounded32 owner missing'
    import ae_owner as o
    import ae_collect as c
    argv=o.collector_argv(Path('/CPU/service-sft24'),Path('/CPU/sft24/free'),123.)
    module=c.implementation();args=module.parse_args(argv[2:])
    assert (args.mode,args.plan,args.start,args.stop)==('free','FREE_PLAN.json',0,32)
    async def run(args):
        import od_study,od_binding
        assert od_study is s and od_binding is s and args.output==Path('/CPU/sft24/free')
    monkeypatch.setattr(module,'run',run);monkeypatch.setattr(sys,'argv',argv[1:]);c.main()

@pytest.mark.parametrize('arm',['B','C'])
def test_actual_native_two_children_reassignment_snapshot_final(tmp_path,monkeypatch,arm):
    s=modules()
    import ae_collect as c
    from aiohttp import web
    monkeypatch.setenv('STRICT_RLM_CALIBRATION_API_KEY','CPU_FIXTURE_NOT_CREDENTIAL');monkeypatch.setenv('ACCUMULATION_CPU_KEY','CPU_FIXTURE_NOT_CREDENTIAL')
    async def fixture():
        row=next(r for r in s.read(s.ROOT/'inputs/FREE_PLAN.json') if r['records']==128 and r['operator']=='count' and r['accumulation_arm']==arm)
        context=next(x for x in s.read(s.ROOT/'inputs/PUBLIC.json') if x['id']==row['context_id']);binding=s.binding()
        tokenizer=s.stack().native.renderer()._tokenizer;roots=[];children=[]
        labels={r['id']:'entity' for r in context['records'][:4]}
        first=context['records'][0]['id'];expected_keys=2 if arm=='B' else 4
        code1='import json\nfrom rlm.api import run as rlm\nfrom batch_contract import request_for, strict_map\nrecords=json.load(open("records.json"))\npart=records[:2]\nchild=await rlm(request_for(part))\nlabels=strict_map(child.answer,[r["id"] for r in part])\nprint(json.dumps(labels,sort_keys=True))\nlabels[records[0]["id"]]="location"'
        code2='part=records[2:4]\nchild=await rlm(request_for(part))\nlabels=strict_map(child.answer,[r["id"] for r in part])\nprint(json.dumps(labels,sort_keys=True))'
        async def provider(request):
            body=await request.json()
            if body['model']==binding['role_map']['root']:
                roots.append(body);assert body['sampling_params']['max_tokens']==2048
                if len(roots)==1:assert body['token_ids']==s.read(s.ROOT/'inputs/PROMPTS_ACCURATE.json')[row['id']]['token_ids']
                assert len(roots)<=3
                if len(roots)==3:
                    text=tokenizer.decode(body['token_ids']);observations=c.implementation().messages(text)
                    latest=json.loads(observations[-1]);assert len(latest)==expected_keys
                    assert (first in latest)==(arm=='C')
                    if arm=='C':assert latest[first]=='entity'
                reply=s.stack().native.tool_action(code1 if len(roots)==1 else code2) if len(roots)<3 else 'Answer: 0'
            else:
                assert body['model']==binding['fixed_child'];children.append(body)
                ids=body['sampling_params']['structured_outputs']['json']['required'];assert len(ids)==2
                reply=json.dumps({key:labels[key] for key in ids})
            ids=tokenizer.encode(reply,add_special_tokens=False)+[151645]
            return web.json_response(dict(request_id='AE_CPU_'+str(len(roots)+len(children)),usage=dict(prompt_tokens=len(body['token_ids']),completion_tokens=len(ids)),choices=[dict(token_ids=ids,finish_reason='stop',logprobs=dict(content=[dict(token=f'token_id:{v}',logprob=-.5) for v in ids]))]))
        async def models(request):return web.json_response(dict(data=[dict(id=a,root=v['path'],max_model_len=8192) for a,v in binding['models'].items()]))
        app=web.Application();app.router.add_post('/inference/v1/generate',provider);app.router.add_get('/v1/models',models);runner=web.AppRunner(app);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start()
        descriptor=dict(host='127.0.0.1',port=site._server.sockets[0].getsockname()[1],api_key_env='ACCUMULATION_CPU_KEY')
        try:
            await c.implementation().episode(row,context,binding,descriptor,tmp_path/'native',time.time()+120,'free')
            result=s.read(tmp_path/'native/RESULT.json');assert result['available'] and result['final_branch_token_identity_verified'] and result['reply']=='Answer: 0'
            assert len(roots)==3 and len(children)==2
            trace=s.read(tmp_path/'native/EPISODE.json')['traces'][0]
            ledger=trace['info']['decoder_ledger'];assert ledger['raw'] is not None
            events=[json.loads(line) for line in ledger['raw'].splitlines()]
            assert len(events)==2 and len(events[-1]['returned'])==expected_keys and all(x['ok'] for x in events)
            assert not any('.decoder_calls.jsonl' in tokenizer.decode(b['token_ids']) for b in roots)
        finally:await runner.cleanup()
    asyncio.run(fixture())
