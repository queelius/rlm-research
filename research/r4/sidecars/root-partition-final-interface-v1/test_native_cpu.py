"""Actual cached tokenizer and native completion identity checks, CPU-only."""
import json
import unittest
from copy import deepcopy
import study as s
import protocol as p
import collect

class NativeContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.tokenizer=s.tokenizer()

    def test_all_inputs_preserve_original_prompt_and_exact_pair(self):
        sources=s.read(s.ROOT/'INPUTS.json');plan=s.read(s.ROOT/'PLAN.json');requests=s.read(s.ROOT/'REQUESTS.json')
        self.assertEqual(len(sources),12);self.assertEqual(len(plan),24)
        self.assertEqual(len({x['world_id'] for x in sources}),4)
        self.assertEqual(sum(len(x['acquisitions']) for x in sources),24)
        for source in sources:
            original=s.read(source['historical_call_path'])
            self.assertEqual(source['messages'],original['request']['messages'])
            actual=self.tokenizer.apply_chat_template(source['messages'],tokenize=True,add_generation_prompt=True,return_dict=False)
            self.assertEqual(actual,source['historical_prompt_token_ids']);self.assertEqual(actual,source['actual_native_prompt_token_ids'])
            pair={row['decoder']:deepcopy(requests[row['id']]) for row in plan if row['source_id']==source['id']}
            pair['exact'].pop('structured_outputs');self.assertEqual(pair['free'],pair['exact'])

    def test_real_completion_ids_must_agree_with_text_and_usage(self):
        source={'actual_native_prompt_token_ids':[1,2]};body={'model':s.MODEL['alias']}
        tokens=self.tokenizer.encode('["c01"]',add_special_tokens=False)
        raw={'model':s.MODEL['alias'],'prompt_token_ids':[1,2],'usage':{'prompt_tokens':2,'completion_tokens':len(tokens)},'choices':[{'token_ids':tokens,'finish_reason':'length','message':{'role':'assistant','content':'["c01"]'}}]}
        content,finish,usage=collect.verified_response(raw,body,source,self.tokenizer)
        self.assertEqual(p.score(content,['c01'],finish)['reward'],1)
        bad=deepcopy(raw);bad['choices'][0]['message']['content']='["c02"]'
        with self.assertRaises(ValueError):collect.verified_response(bad,body,source,self.tokenizer)
        bad=deepcopy(raw);bad['prompt_token_ids']=[1,3]
        with self.assertRaises(ValueError):collect.verified_response(bad,body,source,self.tokenizer)

    def test_domain_schema_does_not_supply_order_distinctness_or_cardinality(self):
        import jsonschema
        schema=p.request({'messages':[]},1,'exact','base')['structured_outputs']['json']
        for value in ([],['c12'],['c12','c01'],['c01','c01'],p.CUSTOMERS):jsonschema.validate(value,schema)
        with self.assertRaises(jsonschema.ValidationError):jsonschema.validate(['c13'],schema)

    def test_installed_native_grammar_accepts_arbitrary_domain_arrays(self):
        import xgrammar
        from vllm.entrypoints.openai.chat_completion.protocol import ChatCompletionRequest
        body=next(v for v in s.read(s.ROOT/'REQUESTS.json').values() if 'structured_outputs' in v)
        ChatCompletionRequest.model_validate(body)
        compiler=xgrammar.GrammarCompiler(xgrammar.TokenizerInfo.from_huggingface(self.tokenizer),max_threads=2)
        compiled=compiler.compile_json_schema(body['structured_outputs']['json'])
        for value in ([],['c12'],['c12','c01'],['c01','c01'],p.CUSTOMERS):
            matcher=xgrammar.GrammarMatcher(compiled)
            self.assertTrue(matcher.accept_string(json.dumps(value)));self.assertTrue(matcher.is_completed())
        matcher=xgrammar.GrammarMatcher(compiled);self.assertFalse(matcher.accept_string('["c13"]'))

if __name__=='__main__':unittest.main()
