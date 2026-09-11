"""Actual tiny PEFT/Adam path across7→8→9→16; synthetic CPU evidence only."""
from pathlib import Path

import pytest
import torch

import campaign_common as c
import campaign_train as t

fixture=c.private('broad_cpu_training_fixture',c.OLD/'test_training.py')


def test_actual_sixteen_updates_restore_and_root_only_masks(tmp_path):
    torch.set_num_threads(1)
    model=fixture.tiny()
    before={n:p.detach().clone() for n,p in model.named_parameters() if not p.requires_grad}
    initial=tmp_path/'initial';model.save_pretrained(initial,safe_serialization=True)
    policy={'step':0,'path':str(initial),'adapter_sha256':c.file_hash(initial/'adapter_model.safetensors'),
        'config_sha256':c.file_hash(initial/'adapter_config.json'),'optimizer_sha256':None,'rng_sha256':None,'state_sha256':None}
    recipe=c.read(c.ROOT/'RECIPE.json');opt=t.make_optimizer(model,recipe)
    assert t.optimizer_step(opt)==0
    for step in range(1,17):
        gen=c.generation_identity('cpu-only-not-native-campaign',step,policy,'fresh-fixture-'+str(step))
        rows=fixture.fresh_rows(model,policy['adapter_sha256'])
        if step==9:
            child=fixture.fresh_rows(model,policy['adapter_sha256']);child[0]['turns'][0]['role_depth']=1
            with pytest.raises(ValueError,match='root'):
                t.update_generation(model,opt,child,tmp_path/'invalid-child',recipe,gen,{})
            masked=fixture.fresh_rows(model,policy['adapter_sha256']);masked[0]['turns'][0]['labels'][0]=1
            with pytest.raises(ValueError,match='masked'):
                t.update_generation(model,opt,masked,tmp_path/'invalid-observation',recipe,gen,{})
            assert t.optimizer_step(opt)==8
        output=tmp_path/f'step-{step}'
        result=t.update_generation(model,opt,rows,output,recipe,gen,{'fixture':'CPU only','step':step})
        policy=result['policy']
        assert policy['step']==t.optimizer_step(opt)==step
        assert result['metrics']['child_loss_tokens']==result['metrics']['observation_loss_tokens']==0
        assert result['metrics']['gradient_norm_before_clip']>0 and result['metrics']['trainable_parameter_delta_l2']>0
        if step in (7,8,9,15,16):
            tensors={n:p.detach().clone() for n,p in model.named_parameters()}
            from peft import PeftModel
            model=PeftModel.from_pretrained(fixture.tiny().unload(),policy['path'],is_trainable=True,autocast_adapter_dtype=True)
            assert all(torch.equal(tensors[n],p) for n,p in model.named_parameters())
            opt=t.make_optimizer(model,recipe)
            t.restore_optimizer(opt,policy,[n for n,p in model.named_parameters() if p.requires_grad])
            assert t.optimizer_step(opt)==step
            again=t.update_generation(model,opt,[],output,recipe,gen,{'fixture':'CPU only','step':step})
            assert again['recovered_checkpoint'] and t.optimizer_step(opt)==step
    assert all(torch.equal(before[n],p) for n,p in model.named_parameters() if not p.requires_grad)
