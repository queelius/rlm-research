import copy
import json
import unittest


class ScienceTests(unittest.TestCase):
    def fixture(self):
        import protocol as p
        return {'records':[dict(id='m123456789abc',premise='A cat sleeps.',hypothesis='An animal sleeps.',gold_label='entailment'),
                           dict(id='mabc123def456',premise='A cat sleeps.',hypothesis='No animal sleeps.',gold_label='contradiction')],
                'index':0}, 'mdeadbeef1234'

    def test_primary_requires_tags_shape_diagnostic_does_not(self):
        import scoring as q
        ctx,constant=self.fixture();out=[{'tag':r['id'],'label':r['gold_label']} for r in ctx['records']]
        score=q.score({'content':json.dumps(out)},ctx,'matching',constant)
        self.assertEqual(score['strict_correct'],2)
        out[0]['tag']=constant
        score=q.score({'content':json.dumps(out)},ctx,'matching',constant)
        self.assertEqual(score['strict_correct'],0);self.assertEqual(score['shape_positional_correct'],2)
        self.assertEqual(score['tag_position_matches'],1);self.assertFalse(score['contract_valid'])

    def test_invalid_zero_missing_null_and_no_reordering(self):
        import scoring as q
        ctx,constant=self.fixture()
        self.assertIsNone(q.missing(ctx)['strict_correct'])
        self.assertEqual(q.score({'content':'prose'},ctx,'matching',constant)['strict_correct'],0)
        self.assertEqual(q.score({'tool_calls':[{'function':{}}]},ctx,'matching',constant)['strict_correct'],0)
        out=[{'tag':r['id'],'label':r['gold_label']} for r in reversed(ctx['records'])]
        self.assertEqual(q.score({'content':json.dumps(out)},ctx,'matching',constant)['strict_correct'],0)
        self.assertEqual(q.score({'content':json.dumps(out)},ctx,'matching',constant)['shape_positional_correct'],0)

    def test_duplicate_keys_bad_labels_and_cardinality_rejected(self):
        import scoring as q
        ctx,constant=self.fixture()
        for text in ('[]','[{"tag":"a","tag":"b","label":"entailment"}]',
                     json.dumps([{'tag':r['id'],'label':'unknown'} for r in ctx['records']])):
            result=q.score({'content':text},ctx,'matching',constant)
            self.assertEqual(result['strict_correct'],0);self.assertFalse(result['shape_valid'])

    def test_source_id_ignores_original_ids_and_labels(self):
        import protocol as p
        a={'premise':'Cat sleeps.','hypothesis':'An animal rests.','pairID':'123e','label':0}
        b={**a,'pairID':'987c','label':2}
        self.assertEqual(p.public_id(a),p.public_id(b))

    def test_requests_hide_gold_source_metadata_and_pair_decoders(self):
        import protocol as p
        ctx,constant=self.fixture();ctx['records'][0].update(pairID='FORBIDDEN_PAIRID',promptID=999,genre='FORBIDDEN_GENRE')
        row={'seed':123,'arm':'matching','decoder':'free'}
        free=p.request(ctx,row,constant);structured=p.request(ctx,{**row,'decoder':'shape'},constant)
        self.assertEqual(free,{k:v for k,v in structured.items() if k!='structured_outputs'})
        changed=copy.deepcopy(ctx)
        for r in changed['records']:r['gold_label']='neutral'
        self.assertEqual(p.request(changed,row,constant),free)
        text=json.dumps(free)
        self.assertNotIn('FORBIDDEN',text);self.assertNotIn('gold_label',text);self.assertNotIn('tools',free)
        self.assertEqual(p.schema(48),p.schema(48))
        self.assertNotIn('const',json.dumps(p.schema(48)));self.assertNotIn('uniqueItems',json.dumps(p.schema(48)))


if __name__=='__main__':unittest.main()
