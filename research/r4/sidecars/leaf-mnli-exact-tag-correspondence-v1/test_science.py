"""Prospective exact-tag grammar and unchanged-prompt contracts."""
import copy,unittest
import protocol as p
import study as s
class ScienceTests(unittest.TestCase):
    def setUp(self):
        self.context=p.contexts()[0]
        self.row=p.plan()[0]
    def test_exact_per_position_tags_and_all_label_options(self):
        for arm in p.ARMS:
            schema=p.schema(self.context,arm)['json']
            self.assertEqual(schema['minItems'],48);self.assertEqual(schema['maxItems'],48)
            self.assertIs(schema['items'],False)
            self.assertEqual(len(schema['prefixItems']),48)
            for item,tag in zip(schema['prefixItems'],p.expected_tags(self.context,arm),strict=True):
                self.assertEqual(item['properties']['tag'],{'type':'string','const':tag})
                self.assertEqual(item['properties']['label']['enum'],list(p.LABELS))
                self.assertEqual(item['required'],['tag','label'])
                self.assertFalse(item['additionalProperties'])
    def test_gold_mutation_cannot_change_request_or_grammar(self):
        changed=copy.deepcopy(self.context)
        for record in changed['records']:record['gold_label']='DO_NOT_LEAK_GOLD'
        self.assertEqual(p.request(changed,self.row),p.request(self.context,self.row))
    def test_exact_ancestor_prompt_and_fresh_paired_plan(self):
        old=s.read(s.SOURCE/'PLAN.json');old_requests=s.read(s.SOURCE/'REQUESTS.json')
        plan=p.plan();self.assertEqual(len(plan),32)
        self.assertTrue({r['seed'] for r in plan}.isdisjoint({r['seed'] for r in old}))
        for row in plan:
            ancestor=next(r for r in old if r['context_index']==row['context_index'] and r['arm']==row['arm'])
            self.assertEqual(p.request(p.contexts()[row['context_index']],row)['messages'],old_requests[ancestor['id']]['messages'])
        for block in range(16):
            pair=[r for r in plan if r['block']==block]
            self.assertEqual({r['arm'] for r in pair},set(p.ARMS))
            self.assertEqual(len({r['seed'] for r in pair}),1)
    def test_strict_gate_and_named_diagnostic_are_not_repaired(self):
        import scoring
        row={**self.row,'arm':'shift17'};tags=p.expected_tags(self.context,'shift17')
        output=[dict(tag=tag,label=r['gold_label']) for tag,r in zip(tags,self.context['records'],strict=True)]
        score=scoring.score({'content':s.serialize(output)},self.context,row['arm'])
        self.assertTrue(score['contract_valid']);self.assertEqual(score['strict_correct'],48)
        output[0]['tag']=self.context['records'][0]['id']
        broken=scoring.score({'content':s.serialize(output)},self.context,row['arm'])
        self.assertFalse(broken['contract_valid']);self.assertEqual(broken['strict_correct'],0)
        self.assertIsNone(broken['shifted_named_disagree_items'])
if __name__=='__main__':unittest.main()
