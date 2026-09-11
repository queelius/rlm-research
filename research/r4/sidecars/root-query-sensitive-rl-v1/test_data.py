import importlib
from pathlib import Path
import unittest
from collections import Counter

class DataTests(unittest.TestCase):
    def module(self):
        self.assertTrue((Path(__file__).parent/'qsr_data.py').exists(), 'query data not implemented')
        return importlib.import_module('qsr_data')
    def test_truth_uses_scope_distinctness_and_visible_record_weights(self):
        d=self.module();rows=[dict(id='a',user='u0',text='A',weight=2),dict(id='b',user='u0',text='B',weight=5),dict(id='c',user='u1',text='C',weight=3)]
        labels={'a':'human being','b':'human being','c':'entity'}
        self.assertEqual([d.answer(rows,labels,dict(operator=o,users=['u0'],target='human being')) for o in d.OPS],[2,1,7])
        self.assertEqual(d.answer(rows,labels,dict(operator='count',users=['u0','u1'],target='entity')),1)
        self.assertEqual(d.answer(rows,labels,dict(operator='weight',users=['u1'],target='human being')),0)
    def test_actual_source_groups_and_schedule_are_disjoint_and_fixed(self):
        d=self.module();v=d.build();contexts=v['PUBLIC.json'];groups=v['GROUPS.json'];plans=v['PLANS.json']
        self.assertEqual(len(contexts),24);self.assertEqual(sum(len(c['records']) for c in contexts),448)
        ids=[x for c in groups for x in c['group_ids']];self.assertEqual(len(set(ids)),448)
        self.assertFalse(set(ids)&set(v['PROVENANCE.json']['excluded_group_ids']))
        train=[r for rows in plans['training'].values() for r in rows]
        self.assertEqual([len(x) for x in plans['training'].values()],[24]*12);self.assertEqual(len(train),288)
        self.assertEqual(len(plans['readout']),48);self.assertEqual(len({r['seed'] for r in train+plans['readout']}),336)
        self.assertEqual(Counter(r['operator'] for r in train),dict(count=96,distinct=96,weight=96))
        self.assertEqual(sum(r['heldout_cell'] for r in plans['readout']),36)
        self.assertTrue(all(set(r)=={'id','user','text','weight'} for c in contexts for r in c['records']))
        self.assertEqual(v,d.build())
    def test_gold_diagnostics_do_not_select_away_zero_or_equal_answers(self):
        d=self.module();v=d.build();diag=v['DIAGNOSTICS.json']
        self.assertEqual(diag['selection_uses_gold_or_model_outcomes'],False)
        for phase,want in [('training',288),('readout',48)]:
            self.assertEqual(diag[phase]['planned'],want)
            self.assertGreaterEqual(diag[phase]['best_constant_correct'],diag[phase]['zero_correct'])

if __name__=='__main__':unittest.main()
