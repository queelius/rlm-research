import importlib
from pathlib import Path
import unittest

class DataTests(unittest.TestCase):
    def module(self):
        self.assertTrue((Path(__file__).parent/'broad_study.py').exists(),'public task adapter missing')
        return importlib.import_module('broad_study')
    def test_only_public_lines_determine_records_and_positional_ids(self):
        s=self.module();text='Date: 2000-01-01 || User: 7 || Instance: Who wrote this?\nDate: 2000-01-02 || User: 1 || Instance: How many?\n'
        self.assertEqual(s.public_records(text),[dict(id='q0001',user='7',text='Who wrote this?'),dict(id='q0002',user='1',text='How many?')])
        with self.assertRaises(ValueError):s.public_records('ID: hidden || LABEL: human being\n')
    def test_fixed_window_and_heldout_plans_are_not_refill_or_operator_mix(self):
        s=self.module();public,host=s.data();plans=s.build_plans(public)
        self.assertEqual(len(plans['training']),16)
        self.assertTrue(all(len(rows)==24 for rows in plans['training'].values()))
        self.assertEqual(len(plans['validation']),16);self.assertEqual(len(plans['transfer']),48)
        from collections import Counter
        rows=[r for rows in plans['training'].values() for r in rows]
        self.assertEqual(len({r['seed'] for r in rows}),384)
        self.assertEqual(set(Counter(r['context_id'] for r in rows).values()),{16})
        by_id={c['id']:c for c in public}
        self.assertTrue(all(sorted({by_id[r['context_id']]['size'] for r in batch})==[16,32,64] for batch in plans['training'].values()))
        self.assertEqual({by_id[r['context_id']]['size'] for r in plans['transfer'] if r['stratum']=='transfer-size'},{128,256})
        self.assertFalse({r['context_id'] for r in rows}&{r['context_id'] for r in plans['validation']+plans['transfer']})

if __name__=='__main__':unittest.main()
