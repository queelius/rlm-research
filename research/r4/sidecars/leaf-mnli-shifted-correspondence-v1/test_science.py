import copy,json,unittest
import protocol as p
import scoring

class ScienceTests(unittest.TestCase):
    def fixture(self):
        records=[]
        labels=p.LABELS
        for i in range(48):records.append(dict(id=f'm{i:012x}',premise=f'premise {i}',hypothesis=f'hypothesis {i}',gold_label=labels[i%3]))
        return {'records':records,'index':0}
    def test_plan_and_fixed_shift(self):
        plan=p.plan();self.assertEqual(len(plan),32);self.assertEqual({r['arm'] for r in plan},set(p.ARMS))
        self.assertEqual(len({r['seed'] for r in plan}),16)
        ctx=self.fixture();self.assertEqual(p.expected_tags(ctx,'shift17'),[r['id'] for r in ctx['records'][17:]]+[r['id'] for r in ctx['records'][:17]])
    def test_common_prompt_only_requested_tag_assignment_changes(self):
        ctx=self.fixture();row=dict(seed=7,arm='matching');a=p.request(ctx,row);b=p.request(ctx,{**row,'arm':'shift17'})
        self.assertEqual({k:v for k,v in a.items() if k!='messages'},{k:v for k,v in b.items() if k!='messages'})
        self.assertEqual(a['messages'][0],b['messages'][0]);self.assertNotIn('shift17',json.dumps(b))
        def strip(body):
            value=copy.deepcopy(body);text=value['messages'][1]['content'];prefix,raw=text.rsplit('\n',1);records=json.loads(raw)
            for r in records:r.pop('requested_tag')
            value['messages'][1]['content']=prefix+'\n'+json.dumps(records,separators=(',',':'));return value
        self.assertEqual(strip(a),strip(b))
    def test_strict_contract_and_named_diagnostic(self):
        ctx=self.fixture();tags=p.expected_tags(ctx,'shift17');out=[]
        by_id={r['id']:r['gold_label'] for r in ctx['records']}
        for tag in tags:out.append(dict(tag=tag,label=by_id[tag]))
        result=scoring.score({'content':json.dumps(out)},ctx,'shift17')
        self.assertTrue(result['contract_valid']);self.assertEqual(result['strict_correct'],0)
        self.assertEqual(result['shifted_named_correct_disagree'],result['shifted_named_disagree_items'])
        out[0]['tag']=ctx['records'][0]['id'];result=scoring.score({'content':json.dumps(out)},ctx,'shift17')
        self.assertEqual(result['strict_correct'],0);self.assertTrue(result['shape_valid']);self.assertFalse(result['contract_valid'])
    def test_completed_invalid_zero_missing_null(self):
        ctx=self.fixture();self.assertIsNone(scoring.missing(ctx)['strict_correct'])
        self.assertEqual(scoring.score({'content':'prose'},ctx,'matching')['strict_correct'],0)
        self.assertEqual(scoring.score({'tool_calls':[{'function':{}}]},ctx,'matching')['strict_correct'],0)

if __name__=='__main__':unittest.main()

