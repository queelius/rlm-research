import importlib
import unittest
from pathlib import Path

class DataTests(unittest.TestCase):
    def build(self):
        self.assertTrue((Path(__file__).parent/'transfer_data.py').exists(),'new panel builder absent')
        return importlib.import_module('transfer_data').build()
    def test_panel_is_disjoint_from_qsr_and_named_history(self):
        v=self.build();public=v['PUBLIC.json'];groups=v['GROUPS.json'];proof=v['PROVENANCE.json']
        ids=[g for c in groups for g in c['group_ids']]
        self.assertEqual((len(public),len(ids),len(set(ids))),(4,64,64))
        self.assertTrue(all(len(c['records'])==16 for c in public))
        self.assertFalse(set(ids)&set(proof['qsr_group_ids']))
        self.assertFalse(set(ids)&set(proof['historical_excluded_group_ids']))
        self.assertEqual(len(proof['remaining_pool_group_ids']),78)
        self.assertEqual(len(proof['qsr_group_ids']),448)
        self.assertTrue(all(set(r)=={'id','user','text'} for c in public for r in c['records']))
        self.assertEqual([c['target'] for c in public],['NUM','HUM','NUM','HUM'])
    def test_free_rows_have_two_queries_two_seeds_without_batch_intervention(self):
        rows=self.build()['FREE_PLAN.json'];self.assertEqual(len(rows),16)
        self.assertEqual(len({r['seed'] for r in rows}),16)
        for cid in {r['context_id'] for r in rows}:
            selected=[r for r in rows if r['context_id']==cid]
            self.assertEqual({(tuple(r['users']),r['repeat']) for r in selected},{(('u03',),0),(('u03',),1),(('u01','u03'),0),(('u01','u03'),1)})
        self.assertTrue(all('width' not in r for r in rows))

if __name__=='__main__':unittest.main()
