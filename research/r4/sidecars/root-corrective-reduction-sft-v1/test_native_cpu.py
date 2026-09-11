"""Actual native tokenizer/template CPU qualification; no containers or model calls."""
import json
import unittest
import protocol as p
import study as s

class NativeContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.native=s.stack().native;cls.renderer=cls.native.renderer();cls.tokenizer=cls.renderer._tokenizer

    def test_frozen_accurate_prompt_prefixes_match_native_renderer(self):
        template=s.read(s.ROOT/'inputs/NATIVE_TEMPLATE.json');tools=json.loads(template['tools_ordered_json'])
        for value in s.read(s.ROOT/'inputs/PROMPTS_ACCURATE.json').values():
            tokens=self.renderer.render([template['system'],{'role':'user','content':value['prompt']}],tools=tools,add_generation_prompt=True).token_ids
            self.assertEqual(tokens,value['token_ids'])
            self.assertIn('fields id, user, and text',value['prompt'])
            self.assertNotIn('Each has id, synthetic user metadata',value['prompt'])

    def test_real_suffix_offsets_partition_code_not_copied_map_literals(self):
        code,_=p.correction([{'q0001':'human being','q0002':'numeric value'}],{'users':['u02']},'human being')
        wire=self.native.tool_action(code);spans,ids=p.target_spans(self.tokenizer,wire,code)
        self.assertEqual(ids,self.tokenizer.encode(wire,add_special_tokens=False)+[151645])
        self.assertEqual(sorted(i for values in spans.values() for i in values),list(range(len(ids))))
        mechanism=self.tokenizer.decode([ids[i] for i in spans['mechanism']]);payload=self.tokenizer.decode([ids[i] for i in spans['payload']])
        self.assertIn('requested_ids',mechanism);self.assertIn('record_id',mechanism)
        self.assertNotIn('q0001',mechanism);self.assertIn('q0001',payload)
        self.assertNotIn('human being',mechanism)
        self.assertIn('human being',self.tokenizer.decode([ids[i] for i in spans['copied_literals']]))

    def test_unchanged_checkpoint_is_real_low66c_with_unchanged_child(self):
        import binding
        chosen=binding.selected('unchanged');self.assertEqual(chosen['adapter_sha256'],s.START_SHA)
        self.assertEqual(s.sha(s.START/'adapter_model.safetensors'),s.START_SHA)

if __name__=='__main__':unittest.main()
