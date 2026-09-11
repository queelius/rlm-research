"""Tiny CPU actual numerical step/noop, not GPU or model validation."""
import math
import time
from types import SimpleNamespace
import torch
import pytest
import od_protocol as p
import od_learning as l
import od_train as t

class Tiny(torch.nn.Module):
    def __init__(self):super().__init__();self.bias=torch.nn.Parameter(torch.zeros(151646))
    def forward(self,input_ids,attention_mask,use_cache):return SimpleNamespace(logits=self.bias[None,None,:].expand(*input_ids.shape,-1))
def episode(n):
    turn=lambda kind,i:p.row(str(i),[1,2],[i,151645],kind)
    return dict(episode_id=str(n),turns=dict(first_producer=turn('first_producer',3),corrective=turn('corrective',4),terminal=turn('terminal',5)),masked_history_turns=[turn('producer_history',6+i) for i in range(n-1)])
def test_real_adam_step_and_expired_noop():
    torch.set_num_threads(1);model=Tiny();optimizer=torch.optim.AdamW(model.parameters(),lr=1e-4,weight_decay=0.)
    result=l.update(model,optimizer,[episode(1),episode(4)],'joint','cpu',time.time()+30)
    assert result['weighted_ce']==pytest.approx(math.log(151646),abs=1e-4)
    assert result['root_turns']==9 and result['mass_sum']==pytest.approx(1.)
    assert {int(v['step']) for v in optimizer.state.values()}=={1}
    before=model.bias.detach().clone()
    with pytest.raises(TimeoutError):l.update(model,optimizer,[episode(4)],'joint','cpu',time.time()-1)
    assert torch.equal(before,model.bias) and {int(v['step']) for v in optimizer.state.values()}=={1}
def test_projection_and_failed_physical_attempt_cost():
    rows=[dict(roles=[dict(forward_seconds=.1)]*3) for _ in range(6)]
    assert t.projection(rows)==pytest.approx(.3*72*6*3+300)
    cost=p.physical_cost([dict(paid_model_call=False,physical_request_attempt=True,body=dict(token_ids=[1,2]))])
    assert cost['calls']==1 and cost['input_tokens']==2 and cost['output_unknown_calls']==1
