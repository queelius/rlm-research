import json,unittest
import scoring,protocol as p
class ScoringTests(unittest.TestCase):
    def test_correct_labels_all_fixed_tag_arms(self):
        c=p.contexts()[0]
        for arm in p.ARMS:
            values=[dict(tag=t,label=r['gold_label']) for t,r in zip(p.expected_tags(c,arm),c['records'])]
            x=scoring.score({'content':json.dumps(values)},c,arm)
            self.assertEqual(x['strict_correct'],48);self.assertTrue(x['contract_valid'])
    def test_wrong_visible_named_oracle_is_not_alignment_repair(self):
        c=p.contexts()[0];byid={r['id']:r['gold_label'] for r in c['records']};tags=p.expected_tags(c,'wrong')
        values=[dict(tag=t,label=byid[t]) for t in tags];x=scoring.score({'content':json.dumps(values)},c,'wrong')
        self.assertGreater(x['shifted_named_disagree_items'],0);self.assertEqual(x['shifted_named_correct_disagree'],x['shifted_named_disagree_items']);self.assertLess(x['strict_correct'],48)
    def test_short_array_known_zero_and_missing_null(self):
        c=p.contexts()[0];x=scoring.score({'content':'[]'},c,'wrong')
        self.assertTrue(x['available']);self.assertEqual(x['strict_correct'],0);self.assertIsNone(scoring.missing(c)['strict_correct'])
if __name__=='__main__':unittest.main()
