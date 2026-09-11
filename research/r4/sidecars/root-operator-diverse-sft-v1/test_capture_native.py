"""Trusted authored CPU native graph; fake provider, no scientific model execution."""
import asyncio
import json
import time
from aiohttp import web
import od_study as s
import od_collect as c
import od_learning as l

def test_actual_capture_root_child_root_current_turns(tmp_path,monkeypatch):
    monkeypatch.setenv('OD_CPU_KEY','qualification-not-credential')
    monkeypatch.setenv('STRICT_RLM_CALIBRATION_API_KEY','qualification-not-credential')
    async def fixture():
        plan=s.read(s.ROOT/'inputs/TRAIN_PLAN.json');row=next(r for r in plan if r['operator']=='weight' and r['width']==4)
        context=next(x for x in s.read(s.ROOT/'inputs/PUBLIC.json') if x['id']==row['context_id'])
        binding=s.read(s.read(s.ROOT/'inputs/START_BINDING.json')['lineage_receipt_path'])
        tokenizer=s.stack().native.renderer()._tokenizer;calls=[]
        async def provider(request):
            body=await request.json();calls.append(body)
            assert body['model']==binding['fixed_child']
            grammar=body['sampling_params']['structured_outputs']['json'];ids=grammar['required']
            assert len(ids)==4 and all(len(i)==13 and i.startswith('q') for i in ids)
            reply=json.dumps({key:row['target'] for key in ids});tokens=tokenizer.encode(reply,add_special_tokens=False)+[151645]
            return web.json_response(dict(request_id=f'OD_CPU_CHILD_{len(calls)}',usage=dict(prompt_tokens=len(body['token_ids']),completion_tokens=len(tokens),total_tokens=len(body['token_ids'])+len(tokens)),choices=[dict(token_ids=tokens,finish_reason='stop',logprobs=dict(content=[dict(token=f'token_id:{i}',logprob=-.5) for i in tokens]))]))
        async def models(request):return web.json_response(dict(data=[dict(id=alias,root=value['path'],max_model_len=8192) for alias,value in binding['models'].items()]))
        app=web.Application();app.router.add_post('/inference/v1/generate',provider);app.router.add_get('/v1/models',models)
        runner=web.AppRunner(app);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start()
        descriptor=dict(host='127.0.0.1',port=site._server.sockets[0].getsockname()[1],api_key_env='OD_CPU_KEY')
        try:
            output=tmp_path/'capture';await c.implementation().episode(row,context,binding,descriptor,output,time.time()+120,'capture')
            teacher=s.read(output/'TEACHER.json');turns=l.weighted_turns(teacher,'joint')
            assert len(calls)==4 and len(turns)==6 and teacher['prefix_ids_verified']
            assert teacher['scalar']==s.answer(context['records'],{r['id']:row['target'] for r in context['records']},row)
            assert all(t['labels'][:t['prompt_length']]==[-100]*t['prompt_length'] for t,w in turns)
            assert all(t['span_indices']['mechanism'] for t,w in turns if t['kind']!='terminal')
            physical=[s.read(p) for p in (output/'physical').glob('*.json')]
            assert all(r['body']['sampling_params']['max_tokens']==2048 for r in physical if r['body']['model']==binding['role_map']['root'])
            assert sum(bool(r.get('physical_request_attempt')) for r in physical)==4
            assert sum(r['origin'].startswith('authored') for r in physical)==6
        finally:await runner.cleanup()
    asyncio.run(fixture())
