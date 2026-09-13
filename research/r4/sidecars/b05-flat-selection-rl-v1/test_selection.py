"""Two bounded fixtures: actual array token boundaries and zero-B real HF update."""
from pathlib import Path
import importlib

def modules():
    assert (Path(__file__).parent/'core.py').exists(),'selection core absent'
    return importlib.import_module('study'),importlib.import_module('core')

def test_actual_native_array_mask_never_selects_gold_or_eos():
    s,c=modules();data=s.read(s.INPUTS);rows=s.validate_inputs(data)
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained(str(s.BASE),local_files_only=True)
    assert len(rows)==18 and sum(r['advantage']!=0 for r in rows)==8
    for row in rows:
        turn=row['root_turns'][0];mask,receipt=s.array_mask(turn['action_ids'],tokenizer)
        assert mask==row['selection_mask'] and not mask[-1]
        assert receipt==row['mask_receipt']
        assert turn['action_ids'][-1] in (151645,151643)
        assert row['actual_loss_mask']==[0]*len(turn['prompt_ids'])+mask
    pure=s.reward(set(),{'a'},{'a','b'})
    assert pure==.5 and s.reward({'a','b'},{'a'},{'a','b'})==.5

def test_actual_zero_B_HF_gradient_mask_Adam_and_rng(tmp_path):
    s,c=modules()
    import torch
    from transformers import Qwen3Config,Qwen3ForCausalLM
    torch.set_num_threads(1);torch.manual_seed(47)
    base=Qwen3ForCausalLM(Qwen3Config(vocab_size=32,hidden_size=16,intermediate_size=32,num_hidden_layers=1,
        num_attention_heads=2,num_key_value_heads=1,head_dim=8,attention_dropout=0.))
    base.config._name_or_path=str(s.BASE)
    model=c.initialize(base);model.train()
    turn={'prompt_ids':[1,2,3],'action_ids':[4,5,6,7],'input_ids':[1,2,3,4,5,6,7],
          'labels':[-100]*3+[4,5,6,7],'loss_mask':[0]*3+[1]*4,'old_logprobs':[-3.]*4}
    enabled=c.selected_logprobs(model,turn,require_grad=False)
    with model.disable_adapter():disabled=c.selected_logprobs(model,turn,require_grad=False)
    assert torch.equal(enabled,disabled)
    initial=c.math.snapshot_trainable(model);c.save_rng(tmp_path/'rng.pt',torch)
    reference=torch.rand(4);c.restore_rng(tmp_path/'rng.pt',torch);assert torch.equal(torch.rand(4),reference)
    values=c.selected_logprobs(model,turn,require_grad=True);values.retain_grad()
    loss=c.selection_loss(values,[1.]*4,.25,[0,1,1,0]);loss.backward()
    assert torch.equal(values.grad,torch.tensor([0.,-.25/18,-.25/18,0.]))
    gradients={n:p.grad.clone() for n,p in model.named_parameters() if p.requires_grad}
    assert all(torch.count_nonzero(v)==0 for n,v in gradients.items() if '.lora_A.' in n)
    assert any(torch.count_nonzero(v)>0 for n,v in gradients.items() if '.lora_B.' in n)
    branch=c.math.apply_fresh_adam_branch(model,initial,gradients,learning_rate=1e-4)
    assert branch['optimizer_state_steps']==[1] and branch['optimizer_state_empty_before_step']
    assert any(not torch.equal(p.detach(),initial[n]) for n,p in model.named_parameters() if p.requires_grad)
    assert c.replay_check(enabled.tolist(),enabled.tolist())['passed']
    assert not c.replay_check((enabled+.01).tolist(),enabled.tolist())['passed']
