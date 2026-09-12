"""Catch wrong RLOO denominator, accidental zero-row gradients and replay-before-step failure."""
from pathlib import Path
import importlib
import torch
torch.set_num_threads(2)
ROOT=Path(__file__).resolve().parent

def modules():
    assert (ROOT/'train.py').exists(), 'fresh8 RLOO trainer not implemented'
    return tuple(importlib.import_module(n) for n in ('study','core','train'))

def test_actual_source_rloo_masks_and_fixed32_denominator():
    s,c,t=modules();rows=s.validate_inputs(s.read(s.INPUTS))
    assert len(rows)==32 and sum(x['reward'] for x in rows)==7
    assert [x['advantage'] for x in rows].count(0.)==20
    assert [x['advantage'] for x in rows].count(1.)==3
    assert [x['advantage'] for x in rows].count(-1/3)==9
    assert sum(len(x['root_turns']) for x in rows)==12
    assert all(not any(turn['loss_mask']) for row in rows for turn in row['zero_loss_root_turns'])
    values=torch.tensor([-.2,-.3],requires_grad=True)
    loss=c.loss(values,[1.,1.],-1/3)
    assert torch.allclose(torch.autograd.grad(loss,values)[0],torch.tensor([1/96,1/96]))

def test_real_tiny_hf_zero_skip_and_replay_failure_no_step(tmp_path):
    s,c,t=modules()
    from transformers import Qwen3Config,Qwen3ForCausalLM
    from peft import LoraConfig,get_peft_model
    torch.manual_seed(123)
    config=Qwen3Config(vocab_size=32,hidden_size=16,intermediate_size=32,num_hidden_layers=1,
        num_attention_heads=2,num_key_value_heads=1,head_dim=8,max_position_embeddings=64,attention_dropout=0.)
    config._attn_implementation='sdpa'
    model=get_peft_model(Qwen3ForCausalLM(config),LoraConfig(r=2,lora_alpha=4,lora_dropout=0,
        target_modules=['q_proj','v_proj'],task_type='CAUSAL_LM'))
    model.train();model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':False});model.enable_input_require_grads()
    rows=[]
    for i in range(32):
        active=i<12;reward=int(i%4==0) if active else 0;adv=(1. if reward else -1/3) if active else 0.
        action=[3,4] if reward else [5,4];prompt=[1,2]
        turn={'input_ids':prompt+action,'prompt_ids':prompt,'action_ids':action,'labels':[-100,-100]+action,
              'loss_mask':[0,0,1,1],'diagnostic_token_parts':['whitespace','eos'],'old_logprobs':[-1.,-1.]}
        turn['old_logprobs']=c.selected_logprobs(model,turn,require_grad=False).detach().tolist()
        rows.append({'episode_id':str(i),'group_id':str(i//4),'reward':reward,'advantage':adv,
                     'baseline':.25 if active else 0.,'root_turns':[turn] if active else []})
    initial=c.math.snapshot_trainable(model);baseline,weights,diag=t.qualify(model,rows)
    assert baseline[12:]==[[]]*20 and weights[12:]==[[]]*20
    broken=[[list(turn) for turn in sample] for sample in baseline];broken[0][0][0]+=.001
    bad=t.accumulate(model,rows,broken,weights,tmp_path/'bad')
    assert not bad['passed'] and bad['optimizer_steps']==0
    assert all(torch.equal(v,c.math.snapshot_trainable(model)[k]) for k,v in initial.items())
    good=t.accumulate(model,rows,baseline,weights,tmp_path/'good')
    assert good['passed'] and len(good['replay'])==12 and good['zero_advantage_skipped']==20
    branch=c.math.apply_fresh_adam_branch(model,initial,good['gradients'],learning_rate=1e-5)
    assert branch['optimizer_state_steps']==[1] and branch['optimizer_state_empty_before_step']
    assert any(not torch.equal(v,c.math.snapshot_trainable(model)[k]) for k,v in initial.items())
