"""Focused actual final-mask/fixed-baseline math and HF replay/update checks."""
from pathlib import Path
import importlib
import torch
torch.set_num_threads(2)

ROOT=Path(__file__).resolve().parent

def modules():
    assert (ROOT/'train.py').exists(), 'fixed-baseline trainer not implemented'
    return tuple(importlib.import_module(n) for n in ('study','core','train'))

def test_actual32_final_masks_and_fixed_baseline_do_not_apply_rloo():
    s,c,t=modules();data=s.read(s.INPUTS);rows=s.validate_inputs(data)
    assert len(rows)==32 and len({x['group_id'] for x in rows})==8
    assert [x['advantage'] for x in rows].count(.5)==28
    assert [x['advantage'] for x in rows].count(-.5)==4
    assert sum(len(x['root_turns'][0]['action_ids']) for x in rows)==10420
    assert sum(len(x['zero_loss_root_turns'][0]['action_ids']) for x in rows)==6716
    assert all(not any(x['zero_loss_root_turns'][0]['loss_mask']) for x in rows)
    values=torch.tensor([-.2,-.3],requires_grad=True)
    positive=c.loss(values,[1,1],.5);negative=c.loss(values,[1,1],-.5)
    assert torch.isclose(positive,torch.tensor(.5*.5/32))
    assert torch.isclose(negative,torch.tensor(-.5*.5/32))
    assert torch.equal(torch.autograd.grad(negative,values)[0],torch.tensor([.5/32,.5/32]))

def test_tiny_actual_hf_replay_failure_stops_before_fresh_adam(tmp_path):
    s,c,t=modules()
    from transformers import Qwen3Config,Qwen3ForCausalLM
    from peft import LoraConfig,get_peft_model
    torch.manual_seed(123)
    config=Qwen3Config(vocab_size=32,hidden_size=16,intermediate_size=32,num_hidden_layers=1,
                       num_attention_heads=2,num_key_value_heads=1,head_dim=8,max_position_embeddings=64,
                       attention_dropout=0.0)
    config._attn_implementation='sdpa'
    model=get_peft_model(Qwen3ForCausalLM(config),LoraConfig(r=2,lora_alpha=4,lora_dropout=0,
        target_modules=['q_proj','v_proj'],task_type='CAUSAL_LM'))
    model.train();model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False});model.enable_input_require_grads()
    rows=[]
    for i in range(32):
        action=[3,4] if i<28 else [5,4];prompt=[1,2]
        turn={'input_ids':prompt+action,'prompt_ids':prompt,'action_ids':action,'old_logprobs':[-1.,-1.],
              'labels':[-100,-100]+action,'loss_mask':[0,0,1,1],'diagnostic_token_parts':['body','eos']}
        turn['old_logprobs']=c.selected_logprobs(model,turn,require_grad=False).detach().tolist()
        rows.append({'episode_id':str(i),'group_id':str(i//4),'reward':int(i<28),'advantage':.5 if i<28 else -.5,'root_turns':[turn]})
    initial=c.math.snapshot_trainable(model)
    baseline,weights,diagnostics=t.qualify(model,rows)
    broken=[[list(turn) for turn in sample] for sample in baseline];broken[0][0][0]+=.001
    bad=t.accumulate(model,rows,broken,weights,tmp_path/'bad')
    assert not bad['passed'] and bad['optimizer_steps']==0
    assert all(torch.equal(v,c.math.snapshot_trainable(model)[k]) for k,v in initial.items())
    good=t.accumulate(model,rows,baseline,weights,tmp_path/'good')
    assert good['passed'] and good['gradient_norm_before_clip']>0
    branch=c.math.apply_fresh_adam_branch(model,initial,good['gradients'],learning_rate=1e-5)
    assert branch['optimizer_state_steps']==[1] and branch['optimizer_state_empty_before_step']
    assert any(not torch.equal(v,c.math.snapshot_trainable(model)[k]) for k,v in initial.items())
