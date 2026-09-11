import importlib
from pathlib import Path
import unittest

class TrainingTests(unittest.TestCase):
    def module(self,name):
        self.assertTrue((Path(__file__).parent/(name+'.py')).exists(),name+' not implemented')
        return importlib.import_module(name)
    def test_noop_window_does_not_advance_adam_and_update_requires_next_cursor(self):
        c=self.module('qsr_common');old=dict(step=3,adapter_sha256='same')
        cursor=c.transition(7,old,8,None)
        self.assertEqual(cursor['policy'],old);self.assertEqual(cursor['optimizer_steps'],3);self.assertEqual(cursor['completed_windows'],8)
        self.assertEqual(c.transition(8,old,9,dict(step=4,adapter_sha256='new'))['optimizer_steps'],4)
        with self.assertRaises(ValueError):c.transition(8,old,9,dict(step=5,adapter_sha256='new'))
        with self.assertRaises(ValueError):c.transition(8,old,10,None)
        g=c.c.generation_identity('fixture',9,dict(step=8),'plan');g['candidate_window']=12;g['generation_id']=c.s.digest({k:v for k,v in g.items() if k!='generation_id'})
        self.assertEqual(c.c.check_generation(g,dict(step=8),8),9)
    def test_returned_capped_final_scored_but_unreturned_and_tool_loop_are_null(self):
        m=self.module('qsr_metrics')
        self.assertEqual(m.score_message('Answer: 7','Answer: 7',[], 'length',7)['reward'],1)
        self.assertEqual(m.score_message('prose','prose',[], 'stop',7)['reward'],0)
        self.assertIsNone(m.score_message('Answer: 7','Answer: 8',[], 'stop',7)['reward'])
        self.assertIsNone(m.score_message('', '',[dict(name='ipython')], 'stop',7)['reward'])
        self.assertIsNone(m.score_message(None,None,[],None,7)['reward'])
    def test_paired_summary_keeps_unknown_pair_out_of_wins_losses(self):
        m=self.module('qsr_metrics');self.assertTrue(hasattr(m,'paired_summary'),'paired endpoint summary not implemented')
        rows=[]
        for arm,rewards in [('unchanged',[1,0,None]),('trained',[0,1,1])]:
            for i,reward in enumerate(rewards):rows.append(dict(phase='readout',arm=arm,coordinate=dict(id=str(i),context_id='shared',heldout_cell=i<2,records=16),reward=reward,available=reward is not None))
        result=m.paired_summary(rows)
        self.assertEqual(result['paired'],dict(wins=1,losses=1,ties=0,unknown=1))
        self.assertEqual(result['policies']['unchanged']['success_bounds'],[1,2]);self.assertEqual(result['context_clusters'],1)

if __name__=='__main__':unittest.main()
