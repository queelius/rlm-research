"""Actual unchanged-init and fresh-Adam dose semantics; no GPU."""
from pathlib import Path
import importlib

def test_same_data_init_and_actual_fresh_Adam_tenfold_step():
    assert (Path(__file__).parent/'study.py').exists(),'dose branch not implemented'
    s=importlib.import_module('study');c=importlib.import_module('core');t=importlib.import_module('train')
    import torch
    assert s.LEARNING_RATE==.001 and s.SEED==s.original.SEED and s.INIT_SEED==s.original.INIT_SEED
    assert s.INPUTS==s.original.INPUTS and s.CONFIG_SOURCE==s.original.CONFIG_SOURCE
    model=torch.nn.Linear(2,1,bias=False);initial={'weight':torch.tensor([[.2,-.3]])};grad={'weight':torch.tensor([[.5,-.25]])}
    first=c.math.apply_fresh_adam_branch(model,initial,grad,learning_rate=.0001)
    low=model.weight.detach().clone()
    second=c.math.apply_fresh_adam_branch(model,initial,grad,learning_rate=s.LEARNING_RATE)
    high=model.weight.detach().clone()
    assert first['optimizer_state_empty_before_step'] and second['optimizer_state_empty_before_step']
    assert first['optimizer_state_steps']==second['optimizer_state_steps']==[1]
    assert torch.allclose(high-initial['weight'],10*(low-initial['weight']),atol=2e-7,rtol=1e-4)
    snapshot={'layer.lora_A.default.weight':torch.tensor([[1.,2.]]),'layer.lora_B.default.weight':torch.zeros(1,1)}
    c.exact_initial(snapshot,snapshot)
    bad={**snapshot,'layer.lora_A.default.weight':snapshot['layer.lora_A.default.weight']+.01}
    try:c.exact_initial(bad,snapshot)
    except AssertionError:pass
    else:raise AssertionError('nonidentical initialization accepted')
    assert t.implementation.s is s and t.implementation.core is c
