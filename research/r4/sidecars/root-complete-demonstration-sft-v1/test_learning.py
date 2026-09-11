import importlib.util
from pathlib import Path
import pytest

def module():
    path=Path(__file__).with_name('learning.py')
    assert path.exists(),'new learning implementation missing'
    spec=importlib.util.spec_from_file_location('learning',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def test_terminal_mask_rejects_empty_and_masks_entire_observation_prefix():
    m=module();row=m.terminal_row('a',[1,2,3,4],[5,151645],{'authentic_scalar':7})
    assert row['labels']==[-100,-100,-100,-100,5,151645]
    assert row['loss_mask']==[0,0,0,0,1,1]
    with pytest.raises(ValueError):m.terminal_row('a',[],[5,151645],{})
    with pytest.raises(ValueError):m.terminal_row('a',[1]*8192,[5,151645],{})

def test_tiny_actual_peft_action_gradient_coefficient_unchanged_and_real_step(tmp_path):
    import torch
    from transformers import GPT2Config,GPT2LMHeadModel
    from peft import LoraConfig,get_peft_model,PeftModel
    m=module();torch.manual_seed(19)
    model=get_peft_model(GPT2LMHeadModel(GPT2Config(vocab_size=32,n_layer=1,n_head=2,n_embd=16,n_positions=64,resid_pdrop=0.,embd_pdrop=0.,attn_pdrop=0.)),LoraConfig(r=2,lora_alpha=4,target_modules=['c_attn'],lora_dropout=0,task_type='CAUSAL_LM'))
    def row(name,target):return {'id':name,'input_ids':[1,2]+target,'prompt_length':2,'labels':[-100,-100]+target,'loss_mask':[0,0]+[1]*len(target)}
    episodes=[{'episode_id':'x','turns':[row('a',[3,4,5]),row('t',[6])]}, {'episode_id':'y','turns':[row('b',[7]),row('u',[8,9])]}]
    optimizer=torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],lr=1e-4,weight_decay=0)
    before={n:p.detach().clone() for n,p in model.named_parameters()}
    before_state={n:p.detach().clone() for n,p in model.state_dict().items()}
    metric=m.update(model,optimizer,episodes,'cpu',terminal_weight=.1)
    losses=metric['turn_losses'];assert [r['nominal_turn_mass'] for r in losses]==[.5,.05,.5,.05]
    assert losses[0]['coefficient_fp32']==pytest.approx(1/6)
    assert losses[2]['coefficient_fp32']==pytest.approx(.5)
    assert metric['action_target_tokens']==4 and metric['terminal_target_tokens']==3
    assert metric['root_turns']==4 and {int(v['step']) for v in optimizer.state.values()}=={1}
    assert any(not torch.equal(p,before[n]) for n,p in model.named_parameters() if p.requires_grad)
    assert all(torch.equal(p,before[n]) for n,p in model.named_parameters() if not p.requires_grad)
    model.save_pretrained(tmp_path/'adapter',safe_serialization=True)
    torch.save(optimizer.state_dict(),tmp_path/'adam.pt');saved=torch.load(tmp_path/'adam.pt',weights_only=True)
    assert {int(v['step']) for v in saved['state'].values()}=={1}
    # Reuse the same frozen base tensors, then load the actual saved LoRA.
    from peft import get_peft_model_state_dict
    expected={k:v.clone() for k,v in get_peft_model_state_dict(model).items()}
    model.load_state_dict(before_state)
    control=torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],lr=1e-4,weight_decay=0)
    action_only=m.update(model,control,episodes,'cpu',terminal_weight=0.)
    assert action_only['terminal_target_tokens']==0 and action_only['action_objective']==pytest.approx(metric['action_objective'])
    assert [r['coefficient_fp32'] for r in action_only['turn_losses']]==[losses[0]['coefficient_fp32'],losses[2]['coefficient_fp32']]
    base=model.unload();loaded=PeftModel.from_pretrained(base,tmp_path/'adapter',is_trainable=True)
    from safetensors.torch import load_file
    assert all(torch.equal(expected[k],v) for k,v in get_peft_model_state_dict(loaded).items())
    restored=torch.optim.AdamW([p for p in loaded.parameters() if p.requires_grad],lr=1e-4,weight_decay=0);restored.load_state_dict(saved)
    assert {int(v['step']) for v in restored.state.values()}=={1}
    for old_state,new_state in zip(saved['state'].values(),restored.state.values()):
        for key in ('exp_avg','exp_avg_sq'):assert torch.equal(old_state[key],new_state[key])
    assert all(torch.isfinite(p).all() for p in loaded.parameters())
