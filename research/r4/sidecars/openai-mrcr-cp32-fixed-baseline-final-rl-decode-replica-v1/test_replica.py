from pathlib import Path
import importlib
import asyncio
import pytest

ROOT=Path(__file__).resolve().parent
def modules():
    assert (ROOT/'study.py').exists(),'paired decoding replica not implemented'
    return tuple(importlib.import_module(n) for n in ('study','checkpoint','collect','owner'))

def test_actual32_payloads_new_paired_seeds_and_both_model_bindings():
    s,c,collect,owner=modules();plan=s.schedule('cp32')
    assert plan==s.schedule('updated') and len(plan)==32
    assert len({x['record_id'] for x in plan})==16
    assert sorted(x['seed'] for x in plan)==list(range(202609270000,202609270032))
    original={x['id']:x for x in s.prior.schedule('held')}
    tasks={x['name']:x for x in s.read(s.input_dir('cp32')/'tasks.json')}
    old_tasks={x['name']:x for x in s.read(s.prior.input_dir('held')/'tasks.json')}
    prefixes=s.read(s.input_dir('cp32')/'PREFIXES.json');old_prefixes=s.read(s.prior.input_dir('held')/'PREFIXES.json')
    for coord in plan:
        old=original[coord['source_coordinate_id']]
        task=dict(tasks[coord['id']]);task['name']=old['id']
        assert task==old_tasks[old['id']] and prefixes[coord['id']]==old_prefixes[old['id']]
        assert coord['seed']==202609270000+2*old['row_index']+old['repeat']
    for arm in s.CAPS:
        binding=c.binding(arm)
        endpoint={'model_alias':binding['role_map']['root'],'host':'127.0.0.1','port':1,'api_key_env':'FIXTURE_KEY','base_model':{'path':str(s.BASE)}}
        m=collect.source.model_context(endpoint,plan[0]);sampling=m.sampling.model_dump(mode='json')
        assert m.model==binding['role_map']['root'] and sampling['seed']==202609270000
        assert sampling['temperature']==.5 and sampling['max_tokens']==2048
    assert collect.source.study is s and collect.source.checkpoint is c
    assert collect.source.verify_ready is collect.verify_ready and owner.source.study is s
    suite=s.dependencies();expected=s.SIDE/'runtime-an22-5801-v1/service_wrapper_v2.py'
    assert suite.SERVE==suite.life.ALLOCATION_SERVICE==expected

def test_wrong_or_unsupported_arm_cannot_bind_fixed_models():
    s,c,_,_=modules()
    with pytest.raises(ValueError):c.binding('best')
    old=c.binding('cp32');new=c.binding('updated')
    assert old['role_map']['root']!=new['role_map']['root']
    assert old['models'][s.BASE_ALIAS]==new['models'][s.BASE_ALIAS]
    assert old['models'][old['role_map']['root']]['adapter_sha256']==s.prior.train.ADAPTER_SHA
    assert new['models'][new['role_map']['root']]['adapter_sha256']=='8be37cf68604a58930cdae1f4270b5eb330b908b70082661f3745d10d4c437c4'
