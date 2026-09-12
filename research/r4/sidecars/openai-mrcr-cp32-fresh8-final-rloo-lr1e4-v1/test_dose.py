"""The exact prior objective/input/seed, with a10x fresh-Adam step and real bindings."""
from pathlib import Path
import importlib
import torch
torch.set_num_threads(2)

def test_same_source_masks_and_actual_lr_branch():
    assert (Path(__file__).parent/'train.py').exists(), 'dose arm not implemented'
    s=importlib.import_module('study');c=importlib.import_module('core');t=importlib.import_module('train')
    assert s.INPUTS==s.original.INPUTS and s.sha(s.INPUTS)==s.original.sha(s.original.INPUTS)
    assert s.SEED==s.original.SEED and s.CHECKPOINT==s.original.CHECKPOINT
    rows=s.validate_inputs(s.read(s.INPUTS));assert len(rows)==32
    assert sum(r['advantage']!=0 for r in rows)==12
    assert sum(len(x['action_ids']) for r in rows for x in r['root_turns'])==5056
    assert t.implementation.study is s and t.implementation.core is c and c.scorer.study is s
    values=torch.tensor([-.2,-.3],requires_grad=True)
    assert torch.allclose(torch.autograd.grad(c.loss(values,[1.,1.],-1/3),values)[0],torch.tensor([1/96,1/96]))
    torch.manual_seed(7);m=torch.nn.Linear(2,2,bias=False);initial=c.math.snapshot_trainable(m)
    grad={n:torch.tensor([[.2,-.4],[.1,-.3]]) for n in initial}
    old=c.math.apply_fresh_adam_branch(m,initial,grad,learning_rate=s.original.LEARNING_RATE)
    old_values=c.math.snapshot_trainable(m)
    new=c.math.apply_fresh_adam_branch(m,initial,grad,learning_rate=s.LEARNING_RATE)
    new_values=c.math.snapshot_trainable(m)
    assert s.LEARNING_RATE==1e-4 and s.LEARNING_RATE/s.original.LEARNING_RATE==10
    assert old['optimizer_state_steps']==new['optimizer_state_steps']==[1]
    assert old['optimizer_state_empty_before_step'] and new['optimizer_state_empty_before_step']
    for n,v in initial.items():assert torch.allclose(new_values[n]-v,10*(old_values[n]-v),rtol=.004,atol=3e-7)
    a=old['optimizer'].state_dict();b=new['optimizer'].state_dict()
    assert a['param_groups'][0]['lr']==1e-5 and b['param_groups'][0]['lr']==1e-4
    for ident,state in a['state'].items():
        for name,value in state.items():assert torch.equal(value,b['state'][ident][name])
