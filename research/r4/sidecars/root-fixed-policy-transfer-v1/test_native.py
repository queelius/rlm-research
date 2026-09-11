import unittest
import json
import transfer_study as s
import transfer_data as d

class NativeTests(unittest.TestCase):
    def test_new_prompt_rendering_is_exact_original_free_contract(self):
        self.assertTrue((s.ROOT/'inputs/PROMPTS_ACCURATE.json').exists(),'native inputs absent')
        renderer=s.stack().native.renderer();template=s.read(s.ROOT/'inputs/NATIVE_TEMPLATE.json')
        public={c['id']:c for c in s.read(s.ROOT/'inputs/PUBLIC.json')};prompts=s.read(s.ROOT/'inputs/PROMPTS_ACCURATE.json')
        for row in s.read(s.ROOT/'inputs/FREE_PLAN.json'):
            text=d.prompt(public[row['context_id']],row)
            tokens=renderer.render([template['system'],dict(role='user',content=text)],tools=json.loads(template['tools_ordered_json']),add_generation_prompt=True).token_ids
            self.assertEqual(prompts[row['id']],dict(prompt=text,token_ids=tokens))
            self.assertLessEqual(len(tokens)+2048,8192)
        oldrows=s.read(s.OLD/'inputs/FREE_PLAN.json');oldpublic={c['id']:c for c in s.read(s.OLD/'inputs/PUBLIC.json')};oldprompts=s.read(s.OLD/'inputs/PROMPTS_ACCURATE.json')
        for row in oldrows:self.assertEqual(d.prompt(oldpublic[row['context_id']],row),oldprompts[row['id']]['prompt'])
    def test_fixed4_adapters_and_actual_child_binding(self):
        self.assertTrue((s.ROOT/'transfer_binding.py').exists(),'fixed binding absent')
        import transfer_binding as b
        expected={'unchanged':'66cce4009628ff7d8e047f08e6fb3a29febdbf8fb3ed8303871f69860f1151d5','joint':'ffa49801af0cfc03daa0de51ccb3beed03b068d7f8c1b94ad57e418c2429fd00','reduction_stop':'eaa80a9f7243a2ceb283c954b7091ad0ab5838831c46c0c9e18a050fe32c81ac'}
        from unittest.mock import patch
        original=s.sha
        with patch.object(s,'sha',side_effect=lambda p:'0'*64 if p==s.ROOT/'READY.json' else original(p)):
            for arm,pin in expected.items():
                chosen=b.selected(arm);self.assertEqual(chosen['adapter_sha256'],pin)
                value=b.binding(arm,chosen);self.assertEqual(value['models'][value['role_map']['root']]['adapter_sha256'],pin)
                self.assertEqual(value['models'][value['fixed_child']]['adapter_sha256'],s.CHILD_SHA)
                self.assertEqual(value['fixed_policy_transfer']['source_training_ready'],str(s.OLD/'READY.json'))

if __name__=='__main__':unittest.main()
