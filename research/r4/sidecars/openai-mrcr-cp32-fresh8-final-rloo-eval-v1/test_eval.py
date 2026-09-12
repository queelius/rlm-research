"""Real 64 task/setup/payload seams plus exact 12-replay/20-skip qualification."""
from pathlib import Path
import importlib
import asyncio
import copy
import hashlib
import pytest
ROOT=Path(__file__).resolve().parent

def modules():
    assert (ROOT/'study.py').exists(), 'three-panel evaluator not implemented'
    return tuple(importlib.import_module(n) for n in ('study','checkpoint','collect'))

def test_actual64_environment_payload_and_sampler_bindings():
    s,c,collector=modules()
    for phase,count,original,original_phase in [('held',32,s.replica,'cp32'),('long',16,s.prior.long,'long'),('fourneedle',16,s.four,'long')]:
        plan=s.schedule(phase);assert plan==original.schedule(original_phase) and len(plan)==count
        env=s.environment(phase);tasks=list(env.taskset);assert {t.data.name for t in tasks}=={r['id'] for r in plan}
        class Runtime:
            def __init__(self):self.files={}
            async def write(self,path,data):self.files[path]=data
            async def read(self,path):return self.files[path]
        async def check_setups():
            for task in tasks:
                rt=Runtime();await task.setup(None,rt)
                assert hashlib.sha256(rt.files['/context.json']).hexdigest()==task.data.document_sha256
        asyncio.run(check_setups())
        prefixes=s.read(s.input_dir(phase)/'PREFIXES.json')
        for row in plan:
            endpoint={'model_alias':s.ADAPTED_ALIAS,'host':'127.0.0.1','port':1,'api_key_env':'FIXTURE_KEY','base_model':{'path':str(s.BASE)}}
            sampling=collector.source.model_context(endpoint,row).sampling.model_dump(mode='json')
            assert sampling['temperature']==.5 and sampling['seed']==row['seed'] and sampling['max_tokens']==2048
            assert prefixes[row['id']]['token_ids']
    assert sorted(r['seed'] for r in s.schedule('held'))==list(range(202609270000,202609270032))
    assert collector.source.study is s and collector.source.checkpoint is c
    assert collector.source.verify_ready is collector.verify_ready

def test_actual_input_replay_inventory_rejects_missing_nonzero_and_credited_zero():
    s,c,_=modules();rows=s.train.validate_inputs(s.read(s.train.INPUTS))
    pre={'episodes':[],'detached_token_weights':[]};replay={'passed':True,'optimizer_steps':0,'replay':[],'episodes':[],'zero_advantage_skipped':20,'nonzero_final_actions':12}
    for i,row in enumerate(rows):
        active=row['advantage']!=0;values=row['root_turns'][0]['old_logprobs'] if active else []
        pre['episodes'].append([values] if active else []);pre['detached_token_weights'].append([[1.]*len(values)] if active else [])
        replay['episodes'].append({'episode_id':row['episode_id'],'reward':row['reward'],'advantage':row['advantage'],
                                  'selected_HF_logprobs':values,**({'zero_advantage_skipped':True} if not active else {})})
        if active:replay['replay'].append({'episode_id':row['episode_id'],'index':i,'passed':True,'tokens':len(values)})
    c.verify_replay(rows,pre,replay)
    bad=copy.deepcopy(replay);bad['replay'].pop()
    with pytest.raises(AssertionError):c.verify_replay(rows,pre,bad)
    bad=copy.deepcopy(pre);zero=next(i for i,r in enumerate(rows) if r['advantage']==0);bad['episodes'][zero]=[[-1.]]
    with pytest.raises(AssertionError):c.verify_replay(rows,bad,replay)
