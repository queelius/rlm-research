"""Tiny real CPU Adam/TIS: a candidate no-op changes neither optimizer nor RNG."""
import copy
import random
from pathlib import Path
import pytest
import torch
import study as s
import train as wrapper
import windows

def fixture():
    path=s.CAMPAIGN/'test_training.py'
    with s.aliases({'campaign_common':wrapper.c,'campaign_train':wrapper.impl}):
        return s.load('refill_tiny_fixture',path,s.sha(path))

def equal(a,b):
    if isinstance(a,torch.Tensor):return torch.equal(a,b)
    if isinstance(a,dict):return a.keys()==b.keys() and all(equal(a[k],b[k]) for k in a)
    if isinstance(a,(tuple,list)):return len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
    return a==b

def test_actual_adam_noop_then_new_window_real_update(tmp_path):
    torch.set_num_threads(1);f=fixture();model=f.tiny();t=wrapper.impl;c=wrapper.c
    path=tmp_path/'initial';model.save_pretrained(path,safe_serialization=True)
    old={'step':0,'path':str(path),'adapter_sha256':s.sha(path/'adapter_model.safetensors'),
         'config_sha256':s.sha(path/'adapter_config.json'),'optimizer_sha256':None,'rng_sha256':None,'state_sha256':None}
    recipe=s.read(s.ROOT/'RECIPE.json');opt=t.make_optimizer(model,recipe)
    gen=c.generation_identity('synthetic-cpu-only',1,old,'full32-fixture');gen['candidate_window']=1;gen['generation_id']=s.digest({k:v for k,v in gen.items() if k!='generation_id'})
    first=t.update_generation(model,opt,f.fresh_rows(model,old['adapter_sha256']),tmp_path/'one',recipe,gen,{'fixture':True})
    policy=first['policy'];before=copy.deepcopy(opt.state_dict());rng=torch.get_rng_state().clone();py=random.getstate()
    cursor=windows.transition(1,policy,2,[False]*4,None)
    assert cursor['optimizer_steps']==1 and cursor['next_window']==3 and equal(before,opt.state_dict())
    assert torch.equal(rng,torch.get_rng_state()) and py==random.getstate()
    second=c.generation_identity('synthetic-cpu-only',2,policy,'another-full32-fixture');second['candidate_window']=3;second['generation_id']=s.digest({k:v for k,v in second.items() if k!='generation_id'})
    result=t.update_generation(model,opt,f.fresh_rows(model,policy['adapter_sha256']),tmp_path/'two',recipe,second,{'fixture':True})
    assert t.optimizer_step(opt)==2 and result['policy']['step']==2
    recovered=t.update_generation(model,opt,[],tmp_path/'two',recipe,second,{'fixture':True})
    assert recovered['recovered_checkpoint'] and t.optimizer_step(opt)==2
    with pytest.raises(ValueError):t.update_generation(model,opt,[],tmp_path/'stale',recipe,gen,{'fixture':True})
    assert result['metrics']['child_loss_tokens']==0 and result['metrics']['observation_loss_tokens']==0

def test_inherited_root_masks_and_recovery_are_unchanged(tmp_path,monkeypatch):
    f=fixture()
    f.test_two_fresh_generations_persist_adam_and_recover_without_double_step(tmp_path,monkeypatch)
    f.test_child_turn_and_unmasked_observation_rejected_before_step(tmp_path)
