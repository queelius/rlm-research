"""Real small CPU optimizer protects moments, name order, RNG and next-step continuity."""
import importlib.util
from pathlib import Path
import random
import torch
import pytest

def module():
    path=Path(__file__).with_name('dose_train.py')
    assert path.exists(), 'exact continuation restorer not implemented'
    spec=importlib.util.spec_from_file_location('dose_test_train',path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def fixture():
    p=torch.nn.Parameter(torch.tensor([1.,2.]));o=torch.optim.AdamW([p],lr=1e-4,weight_decay=0.)
    for _ in range(6):o.zero_grad();p.square().sum().backward();o.step()
    state=o.state_dict();names=[{'name':'x.lora_A.default.weight','shape':[2],'dtype':'torch.float32'}]
    return p,o,state,names

def test_saved_moments_and_next_update_match_uninterrupted():
    m=module();p,o,state,names=fixture();q=torch.nn.Parameter(p.detach().clone());new=torch.optim.AdamW([q],lr=1e-4,weight_decay=0.)
    m.restore_state(new,[('x.lora_A.default.weight',q)],state,names,6)
    assert torch.equal(new.state[q]['exp_avg'],o.state[p]['exp_avg'])
    assert torch.equal(new.state[q]['exp_avg_sq'],o.state[p]['exp_avg_sq'])
    for value,opt in [(p,o),(q,new)]:opt.zero_grad();value.square().sum().backward();opt.step()
    assert torch.equal(p,q)
    assert int(new.state[q]['step'])==7

def test_bad_mapping_step_and_recipe_rejected():
    m=module();p,o,state,names=fixture()
    with pytest.raises(ValueError):m.restore_state(o,[('wrong',p)],state,names,6)
    with pytest.raises(ValueError):m.restore_state(o,[(names[0]['name'],p)],state,names,5)
    state['param_groups'][0]['lr']=2e-5
    with pytest.raises(ValueError):m.restore_state(o,[(names[0]['name'],p)],state,names,6)

def test_rng_restore_after_intervening_cpu_diagnostic():
    m=module();random.seed(15);torch.manual_seed(16)
    state={'python':random.getstate(),'torch':torch.get_rng_state(),'cuda':[]}
    expected=(random.random(),torch.rand(3));random.random();torch.rand(30)
    m.restore_rng(state,'cpu')
    assert random.random()==expected[0] and torch.equal(torch.rand(3),expected[1])

def test_actual_frozen504_checkpoint_ancestry_and_moments():
    m=module();s=m.s;state=s.read(s.START/'state.json')
    checked=m.checkpoint(s.START,state['identity'],state['previous_state_sha256'],6)
    assert checked['step']==6 and checked['corpus_sha256']=='207d36997fe82c390a82e3b27c4e3ad863ba5fdc07f00574cbd2084e80792ea9'
