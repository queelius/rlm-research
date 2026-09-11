"""Tiny CPU tensor tests of real causal CE/optimizer path, no downloaded/model weights."""
import math
import time
import unittest
from types import SimpleNamespace
import torch
import protocol as p
import learning as l

class Tiny(torch.nn.Module):
    def __init__(self):super().__init__();self.bias=torch.nn.Parameter(torch.zeros(151646))
    def forward(self,input_ids,attention_mask,use_cache):return SimpleNamespace(logits=self.bias[None,None,:].expand(*input_ids.shape,-1))

class LearningContracts(unittest.TestCase):
    def test_equal_example_mass_only_selected_current_action_updates(self):
        model=Tiny();optimizer=torch.optim.AdamW(model.parameters(),lr=.0001,weight_decay=0.)
        episodes=[dict(episode_id='a',turns={'corrective':p.row('a',[1,2],[3,151645],'corrective')}),dict(episode_id='b',turns={'corrective':p.row('b',[4,5,6],[7,8,151645],'corrective')})]
        result=l.update(model,optimizer,episodes,'corrective','cpu',time.time()+30)
        self.assertAlmostEqual(result['weighted_ce'],math.log(151646),places=4)
        self.assertEqual(result['target_tokens'],5);self.assertEqual(result['root_turns'],2)
        self.assertEqual([r['nominal_turn_mass'] for r in result['turn_losses']],[.5,.5])
        self.assertEqual({int(x['step']) for x in optimizer.state.values()},{1})
        self.assertGreater(float(model.bias[3].detach()),0);self.assertLess(float(model.bias[1].detach()),0)

    def test_expired_accumulation_never_advances_optimizer(self):
        model=Tiny();optimizer=torch.optim.AdamW(model.parameters(),lr=.0001)
        episode=dict(episode_id='a',turns={'corrective':p.row('a',[1],[2,151645],'corrective')})
        with self.assertRaises(TimeoutError):l.update(model,optimizer,[episode],'corrective','cpu',time.time()-1)
        self.assertFalse(optimizer.state)

if __name__=='__main__':unittest.main()
