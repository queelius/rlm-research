import importlib
from pathlib import Path
import unittest

class LearningTests(unittest.TestCase):
    def module(self):
        self.assertTrue((Path(__file__).parent/'joint_learning.py').exists(),'weighted role loss not implemented')
        return importlib.import_module('joint_learning')
    def episode(self,n):
        def turn(kind,i):return dict(id=str(i),kind=kind,input_ids=[10,20,151645],labels=[-100,20,151645],loss_mask=[0,1,1],prompt_length=1,target_tokens=2)
        return dict(episode_id='example',turns={k:turn(k,0) for k in ('first_producer','corrective','terminal')},masked_history_turns=[turn('producer_history',i) for i in range(n-1)])
    def test_equal_trajectory_role_mass_regardless_batch_count(self):
        l=self.module()
        for n in (1,4):
            selected=l.weighted_turns(self.episode(n),'joint')
            self.assertEqual(len(selected),n+2)
            self.assertAlmostEqual(sum(w for t,w in selected if 'producer' in t['kind']),.45)
            self.assertAlmostEqual(sum(w for t,w in selected),1.)
            control=l.weighted_turns(self.episode(n),'reduction_stop')
            self.assertEqual([(t['kind'],w) for t,w in control],[('corrective',.95),('terminal',.05)])
    def test_gate_requires_code_headroom_not_literal_headroom(self):
        l=self.module();rows=[dict(mechanism_nll=.01,target_nll=3.,copied_literals_nll=5.) for _ in range(4)]
        self.assertFalse(l.objective_gate(rows)['pass'])
        for r in rows[:3]:r['mechanism_nll']=.2
        self.assertTrue(l.objective_gate(rows)['pass'])

if __name__=='__main__':unittest.main()
