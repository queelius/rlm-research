import copy,unittest
import protocol as p

class ScienceTests(unittest.TestCase):
    def test_plan_is_48_balanced_paired_endpoints(self):
        rows=p.plan();self.assertEqual(len(rows),48)
        for block in range(16):
            x=[r for r in rows if r['block']==block]
            self.assertEqual({r['arm'] for r in x},set(p.ARMS));self.assertEqual(len({r['seed'] for r in x}),1)
    def test_alien_dictionary_is_one_to_one_collision_free_and_length_matched(self):
        tok=p.s.tokenizer()
        for c in p.contexts():
            visible={r['id'] for r in c['records']}; alien=p.alien_tags(c)
            self.assertEqual(len(alien),len(set(alien)));self.assertTrue(visible.isdisjoint(alien))
            shifted=p.expected_tags(c,'shift17')
            self.assertEqual([len(tok.encode(x,add_special_tokens=False)) for x in alien],[len(tok.encode(x,add_special_tokens=False)) for x in shifted])
    def test_decoder_has_exact_tags_and_free_labels(self):
        c=p.contexts()[0]
        for arm in p.ARMS:
            schema=p.schema(c,arm)['json'];self.assertEqual(len(schema['prefixItems']),48)
            for item,tag in zip(schema['prefixItems'],p.expected_tags(c,arm),strict=True):
                self.assertEqual(item['properties']['tag'],{'type':'string','const':tag})
                self.assertEqual(item['properties']['label']['enum'],list(p.LABELS))
    def test_gold_never_changes_request(self):
        c=p.contexts()[0]; changed=copy.deepcopy(c)
        for r in changed['records']:r['gold_label']='HIDDEN'
        for arm in p.ARMS:
            row={**p.plan()[0],'arm':arm};self.assertEqual(p.request(c,row),p.request(changed,row))
if __name__=='__main__':unittest.main()
