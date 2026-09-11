import copy,unittest
import protocol as p,scoring,study as s
class ScoringTests(unittest.TestCase):
    def test_alien_exact_contract_scores_displayed_labels(self):
        c=p.contexts()[0];values=[{'tag':t,'label':r['gold_label']} for t,r in zip(p.expected_tags(c,'alien'),c['records'],strict=True)]
        out=scoring.score({'content':s.serialize(values)},c,'alien');self.assertTrue(out['contract_valid']);self.assertEqual(out['strict_correct'],48);self.assertIsNone(out['shifted_named_disagree_items'])
    def test_wrong_alien_tag_gates_whole_semantic_score(self):
        c=p.contexts()[0];values=[{'tag':t,'label':r['gold_label']} for t,r in zip(p.expected_tags(c,'alien'),c['records'],strict=True)];values[0]['tag']=c['records'][0]['id']
        out=scoring.score({'content':s.serialize(values)},c,'alien');self.assertFalse(out['contract_valid']);self.assertEqual(out['strict_correct'],0)
    def test_shift_named_diagnostic_remains_shift_only(self):
        c=p.contexts()[0];tags=p.expected_tags(c,'shift17');byid={r['id']:r['gold_label'] for r in c['records']};values=[{'tag':t,'label':byid[t]} for t in tags]
        out=scoring.score({'content':s.serialize(values)},c,'shift17');self.assertTrue(out['contract_valid']);self.assertGreater(out['shifted_named_disagree_items'],0);self.assertEqual(out['shifted_named_correct_disagree'],out['shifted_named_disagree_items'])
if __name__=='__main__':unittest.main()
