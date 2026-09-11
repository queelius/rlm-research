import copy
import json
import unittest
import mn_protocol as p
import mn_scoring as scoring
import mn_study as s

class ScienceTests(unittest.TestCase):
    def test_exact_frozen_contexts_and_public_id_scope(self):
        self.assertEqual(s.sha(s.ROOT/'DATA.json'),s.SELECTED_SHA)
        contexts=p.contexts();self.assertEqual(len(contexts),16)
        self.assertEqual(len({g for c in contexts for g in c['premise_groups']}),256)
        self.assertEqual(len({r['id'] for c in contexts for r in c['records']}),768)
        self.assertTrue(all(len(c['records'])==48 for c in contexts))
        old={g for c in s.read(s.BASE/'DATA.json')['contexts'] for g in c['premise_groups']}
        self.assertFalse(old & {g for c in contexts for g in c['premise_groups']})

    def test_pair_schedule_and_every_label_allowed(self):
        plan=p.plan();self.assertEqual(len(plan),32)
        for block in range(16):
            rows=[r for r in plan if r['block']==block]
            self.assertEqual({r['arm'] for r in rows},{'matching','constant'})
            self.assertEqual({r['seed'] for r in rows},{981621101+block})
        for arm in p.ARMS:
            schema=p.schema(p.contexts()[0],arm)['json']
            self.assertEqual((schema['minItems'],schema['maxItems'],schema['items']),(48,48,False))
            self.assertTrue(all(x['properties']['label']['enum']==list(p.LABELS) for x in schema['prefixItems']))

    def test_actual_exact_ancestor_request_boundary(self):
        with s.aliases({'study':s}):old=s.load('mn_new_test_exact_protocol',s.SOURCE/'protocol.py',s.PINS['protocol.py'])
        for arm in p.ARMS:
            context=p.contexts()[0];row={**p.plan()[0],'arm':arm}
            old.expected_tags=p.expected_tags
            self.assertEqual(p.request(context,row),old.request(context,row))
            changed=copy.deepcopy(context)
            for i,r in enumerate(changed['records']):r['gold_label']=p.LABELS[(i*7+1)%3];r['original_pairID']='HIDDEN-GOLD-SUFFIX'
            self.assertEqual(p.request(changed,row),p.request(context,row))
            body=p.request(context,row);self.assertNotIn('tools',body)
            visible=json.loads(body['messages'][1]['content'].split('Input records (id, premise, hypothesis, requested_tag):\n')[1])
            self.assertTrue(all(set(r)=={'id','premise','hypothesis','requested_tag'} for r in visible))

    def test_strict_and_shape_only_are_separate_no_salvage(self):
        context=p.contexts()[0]
        for arm in p.ARMS:
            values=[dict(tag=tag,label=row['gold_label']) for tag,row in zip(p.expected_tags(context,arm),context['records'],strict=True)]
            good=scoring.score(dict(content=s.serialize(values)),context,arm)
            self.assertEqual(good['strict_correct'],48);self.assertEqual(good['shape_positional_correct'],48)
            values[0]['tag']='m000000000000'
            broken=scoring.score(dict(content=s.serialize(values)),context,arm)
            self.assertEqual(broken['strict_correct'],0);self.assertEqual(broken['shape_positional_correct'],48)
            values[0]['tag']=[]
            self.assertEqual(scoring.score(dict(content=s.serialize(values)),context,arm)['strict_correct'],0)
        self.assertIsNone(scoring.missing(context)['strict_correct'])

    def test_token_prefix_proof_uses_actual_ids_not_encoding_mapping_length(self):
        value=s.read(s.ROOT/'CPU_NATIVE.json')
        self.assertEqual(value['max_input_tokens'],4088)
        self.assertEqual(value['max_input_plus_output'],7160)
        self.assertTrue(value['all32_request_boundary_equal_to_exact_source'])
        self.assertEqual(value['tools_advertised'],0)
        self.assertTrue(value['selection_label_mutation_rechecked'])

if __name__=='__main__':unittest.main()
