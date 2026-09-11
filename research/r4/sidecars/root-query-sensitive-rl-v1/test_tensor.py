import copy
import importlib
from pathlib import Path
import pytest
import torch
import qsr_study as s
import qsr_common as common

def test_real_root_adam_checkpoint_noop_restore_and_masks(tmp_path):
    assert (s.ROOT/'qsr_train.py').exists(), 'qualified trainer binding not implemented'
    w=importlib.import_module('qsr_train');t=w.impl;c=common.c;torch.set_num_threads(1)
    p=s.CAMPAIGN/'test_training.py'
    with s.aliases({'campaign_common':c,'campaign_train':t}):f=s.load('qsr_tiny_fixture',p,s.sha(p))
    model=f.tiny();original=tmp_path/'initial';model.save_pretrained(original,safe_serialization=True)
    policy=dict(step=0,path=str(original),adapter_sha256=s.sha(original/'adapter_model.safetensors'),config_sha256=s.sha(original/'adapter_config.json'),optimizer_sha256=None,rng_sha256=None,state_sha256=None)
    recipe=s.read(s.ROOT/'RECIPE.json');opt=t.make_optimizer(model,recipe)
    def gen(step,old,window):
        v=c.generation_identity('synthetic-cpu-not-science',step,old,'fixture');v['candidate_window']=window;v['generation_id']=s.digest({k:v for k,v in v.items() if k!='generation_id'});return v
    g=gen(1,policy,1);rows=f.fresh_rows(model,policy['adapter_sha256'])
    bad=copy.deepcopy(rows);bad[0]['turns'][0]['role_depth']=1
    with pytest.raises(ValueError,match='root'):t.update_generation(model,opt,bad,tmp_path/'bad-child',recipe,g,{})
    bad=copy.deepcopy(rows);bad[0]['turns'][0]['labels'][0]=1
    with pytest.raises(ValueError,match='masked'):t.update_generation(model,opt,bad,tmp_path/'bad-mask',recipe,g,{})
    first=t.update_generation(model,opt,rows,tmp_path/'one',recipe,g,{'fixture':True});p1=first['policy'];rng=torch.get_rng_state().clone()
    cursor=common.transition(1,p1,2,None);assert cursor['policy']==p1 and t.optimizer_step(opt)==1 and torch.equal(rng,torch.get_rng_state())
    recovered=t.update_generation(model,opt,[],tmp_path/'one',recipe,g,{'fixture':True});assert recovered['recovered_checkpoint'] and t.optimizer_step(opt)==1
    from peft import PeftModel
    model2=PeftModel.from_pretrained(f.tiny().unload(),p1['path'],is_trainable=True,autocast_adapter_dtype=True);opt2=t.make_optimizer(model2,recipe)
    t.restore_optimizer(opt2,p1,[name for name,p in model2.named_parameters() if p.requires_grad]);assert t.optimizer_step(opt2)==1
    second=t.update_generation(model2,opt2,f.fresh_rows(model2,p1['adapter_sha256']),tmp_path/'two',recipe,gen(2,p1,3),{'fixture':True})
    assert second['policy']['step']==2 and second['metrics']['child_loss_tokens']==0 and second['metrics']['observation_loss_tokens']==0
