import importlib
import json
from pathlib import Path
import unittest
import joint_study as s
import joint_protocol as p

class NativeTests(unittest.TestCase):
    def test_first_four_and_full_plans_have_actual_role_counts_and_split(self):
        self.assertTrue((s.ROOT/'prepare.py').exists(),'fixed plans not implemented')
        plans=importlib.import_module('prepare').plans()
        train,free,control,diagnostic=(plans[k] for k in ('TRAIN_PLAN.json','FREE_PLAN.json','CONTROLLED_PLAN.json','DIAGNOSTIC_PLAN.json'))
        self.assertEqual([len(x) for x in (train,free,control,diagnostic)],[16,16,8,4])
        self.assertEqual({(r['width'],r['family']) for r in train[:4]},{(4,'single_user'),(4,'union'),(16,'single_user'),(16,'union')})
        self.assertEqual(sum(16//r['width'] for r in train),40)
        self.assertEqual(sum(p.layout(r)['root_turns'] for r in train),72)
        self.assertEqual(sum(16//r['width'] for r in control),20)
        public=s.read(s.BASE_CORRECTIVE/'inputs/PUBLIC.json')
        groups={c['id']:set(c['group_ids']) for c in public}
        self.assertFalse(set.union(*(groups[r['context_id']] for r in train))&set.union(*(groups[r['context_id']] for r in control)))
    def test_code_span_nll_excludes_query_and_category_literals(self):
        n=s.stack().native;tok=n.renderer()._tokenizer
        code,_=p.correction([],dict(variable='live_labels',users=['u03']),'numeric value')
        wire=n.tool_action(code);spans,ids=p.target_spans(tok,wire,code)
        self.assertEqual(ids,tok.encode(wire,add_special_tokens=False)+[151645])
        self.assertEqual(sorted(i for v in spans.values() for i in v),list(range(len(ids))))
        mechanism=tok.decode([ids[i] for i in spans['mechanism']]);literal=tok.decode([ids[i] for i in spans['copied_literals']])
        self.assertIn('live_labels',mechanism);self.assertIn('requested_ids',mechanism)
        self.assertNotIn('numeric value',mechanism);self.assertNotIn('u03',mechanism)
        self.assertIn('numeric value',literal);self.assertIn('u03',literal);self.assertEqual(spans['payload'],[])
    def test_frozen_prompts_match_actual_native_and_accurate_fields(self):
        self.assertTrue((s.ROOT/'inputs/PROMPTS_ACCURATE.json').exists(),'native prompts not prepared')
        n=s.stack().native;renderer=n.renderer();template=s.read(s.ROOT/'inputs/NATIVE_TEMPLATE.json')
        for value in s.read(s.ROOT/'inputs/PROMPTS_ACCURATE.json').values():
            actual=renderer.render([template['system'],dict(role='user',content=value['prompt'])],tools=json.loads(template['tools_ordered_json']),add_generation_prompt=True).token_ids
            self.assertEqual(actual,value['token_ids']);self.assertIn('fields id, user, and text',value['prompt'])

if __name__=='__main__':unittest.main()
