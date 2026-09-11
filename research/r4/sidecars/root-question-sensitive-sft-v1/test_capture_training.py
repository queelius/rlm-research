"""Real native capture feeds current-action loss; authored CPU responses only."""
import asyncio
import json
import time
from pathlib import Path
import pytest

@pytest.mark.parametrize('slot',['T1','M1','J1'])
def test_native_capture_to_real_weighted_current_action_loss(tmp_path,monkeypatch,slot):
    assert Path(__file__).with_name('qs_collect.py').exists(),'capture/training aliases absent'
    import qs_study as s
    import qs_collect as c
    import qs_learning as l
    import qs_binding as b
    import torch
    from aiohttp import web
    from types import SimpleNamespace
    torch.set_num_threads(1)
    monkeypatch.setenv('QS_CPU_KEY','AUTHORED_CPU_NOT_CREDENTIAL');monkeypatch.setenv('STRICT_RLM_CALIBRATION_API_KEY','AUTHORED_CPU_NOT_CREDENTIAL')
    async def fixture():
        row=next(r for r in s.read(s.ROOT/'inputs/TRAIN_PLAN.json') if r['context_id'].endswith('00') and r['slot']==slot)
        context=next(x for x in s.read(s.ROOT/'inputs/PUBLIC.json') if x['id']==row['context_id']);binding=b.binding('unchanged');tokenizer=s.stack().native.renderer()._tokenizer;calls=[]
        labels={r['id']:row['target'] if i%3 else (row['target_b'] or 'location') for i,r in enumerate(context['records'])}
        async def provider(request):
            body=await request.json();calls.append(body);assert body['model']==binding['fixed_child']
            ids=body['sampling_params']['structured_outputs']['json']['required'];assert set(ids)==set(labels) and len(ids)==16
            tokens=tokenizer.encode(json.dumps(labels),add_special_tokens=False)+[151645]
            return web.json_response(dict(request_id='QS_CPU_CHILD',usage=dict(prompt_tokens=len(body['token_ids']),completion_tokens=len(tokens)),choices=[dict(token_ids=tokens,finish_reason='stop',logprobs=dict(content=[dict(token=f'token_id:{v}',logprob=-.5) for v in tokens]))]))
        async def models(request):return web.json_response(dict(data=[dict(id=a,root=v['path'],max_model_len=8192) for a,v in binding['models'].items()]))
        app=web.Application();app.router.add_post('/inference/v1/generate',provider);app.router.add_get('/v1/models',models);runner=web.AppRunner(app);await runner.setup();site=web.TCPSite(runner,'127.0.0.1',0);await site.start()
        descriptor=dict(host='127.0.0.1',port=site._server.sockets[0].getsockname()[1],api_key_env='QS_CPU_KEY')
        try:
            output=tmp_path/'capture';await c.implementation().episode(row,context,binding,descriptor,output,time.time()+120,'capture')
            teacher=s.read(output/'TEACHER.json');weighted=l.weighted_turns(teacher,'joint')
            assert len(calls)==1 and len(weighted)==3 and [w for t,w in weighted]==[.45,.50,.05]
            assert teacher['scalar']==s.answer(context['records'],labels,row) and teacher['prefix_ids_verified']
            assert all(t['labels'][:t['prompt_length']]==[-100]*t['prompt_length'] for t,w in weighted)
            assert all(t['labels'][t['prompt_length']:]==t['input_ids'][t['prompt_length']:] for t,w in weighted)
            assert all(t['span_indices']['mechanism'] and not t['span_indices']['payload'] for t,w in weighted if t['kind']!='terminal')
            physical=[s.read(p) for p in sorted((output/'physical').glob('*.json'))];assert sum(bool(x.get('physical_request_attempt')) for x in physical)==1
            assert sum(x['origin'].startswith('authored') for x in physical)==3
            roots=[x for x in physical if x['body']['model']==binding['role_map']['root']]
            assert roots[0]['body']['token_ids']==s.read(s.ROOT/'inputs/PROMPTS_ACCURATE.json')[row['id']]['token_ids']
            assert all(x['body']['sampling_params']['max_tokens']==2048 and x['body']['sampling_params']['temperature']==.5 and x['body']['sampling_params']['top_p']==1 for x in roots)
            # Keep real captured native IDs, sequence lengths, masks and role weights. Only the
            # toy numerical vocabulary is modulo31 at cross-entropy; no scientific model claim.
            class Tiny(torch.nn.Module):
                def __init__(self):super().__init__();self.bias=torch.nn.Parameter(torch.zeros(31))
                def forward(self,input_ids,attention_mask,use_cache):return SimpleNamespace(logits=self.bias[None,None,:].expand(*input_ids.shape,-1))
            import torch.nn.functional as F
            original=F.cross_entropy
            with monkeypatch.context() as patch:
                patch.setattr(F,'cross_entropy',lambda logits,target,**kw:original(logits,target%31,**kw))
                model=Tiny();optimizer=torch.optim.AdamW(model.parameters(),lr=1e-4,weight_decay=0.)
                result=l.update(model,optimizer,[teacher],'joint','cpu',time.time()+30)
            assert result['root_turns']==3 and result['mass_sum']==pytest.approx(1.)
            assert result['target_tokens']==sum(len(t['input_ids'])-t['prompt_length'] for t,w in weighted)
            assert {int(v['step']) for v in optimizer.state.values()}=={1}
            if slot=='J1':
                from test_train_owner import exercise_actual_trainer_entry_from_native_teacher
                exercise_actual_trainer_entry_from_native_teacher(output/'TEACHER.json',tmp_path/'training',monkeypatch)
        finally:await runner.cleanup()
    asyncio.run(fixture())

def test_nearzero_primitive_NLL_is_not_an_admission_failure():
    assert Path(__file__).with_name('qs_learning.py').exists(),'cost-only gate absent'
    import qs_learning as l
    assert l.objective_gate([dict(mechanism_nll=0.,target_nll=0.) for _ in range(6)])['pass']
    with pytest.raises(ValueError):l.objective_gate([dict(mechanism_nll=float('nan'),target_nll=0.) for _ in range(6)])
