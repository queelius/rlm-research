"""Tiny CPU exercise of actual shifted losses and a complete multi-role optimizer update."""
import math
import time
import unittest
from types import SimpleNamespace
import torch
import joint_protocol as p
import joint_learning as l

class Tiny(torch.nn.Module):
    def __init__(self):super().__init__();self.bias=torch.nn.Parameter(torch.zeros(151646))
    def forward(self,input_ids,attention_mask,use_cache):return SimpleNamespace(logits=self.bias[None,None,:].expand(*input_ids.shape,-1))

class TensorTests(unittest.TestCase):
    def episode(self,n):
        turn=lambda kind,i:p.row(str(i),[1,2],[i,151645],kind)
        return dict(episode_id=str(n),turns=dict(first_producer=turn('first_producer',3),corrective=turn('corrective',4),terminal=turn('terminal',5)),masked_history_turns=[turn('producer_history',6+i) for i in range(n-1)])
    def test_complete_weighted_update_has_equal_trajectory_mass_and_one_adam_step(self):
        model=Tiny();optimizer=torch.optim.AdamW(model.parameters(),lr=.0001,weight_decay=0.)
        result=l.update(model,optimizer,[self.episode(1),self.episode(4)],'joint','cpu',time.time()+30)
        self.assertAlmostEqual(result['weighted_ce'],math.log(151646),places=4)
        self.assertEqual(result['root_turns'],9);self.assertEqual(result['target_tokens'],18)
        self.assertAlmostEqual(result['mass_sum'],1.)
        self.assertAlmostEqual(sum(r['nominal_turn_mass'] for r in result['turn_losses'] if r['episode_id']=='1'),.5)
        self.assertEqual({int(x['step']) for x in optimizer.state.values()},{1})
        self.assertGreater(float(model.bias[4].detach()),0);self.assertLess(float(model.bias[1].detach()),0)
    def test_expired_multi_role_pass_never_advances_optimizer(self):
        model=Tiny();optimizer=torch.optim.AdamW(model.parameters(),lr=.0001)
        with self.assertRaises(TimeoutError):l.update(model,optimizer,[self.episode(4)],'joint','cpu',time.time()-1)
        self.assertFalse(optimizer.state)

if __name__=='__main__':unittest.main()
