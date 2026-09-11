import importlib.util
import json
from pathlib import Path
import unittest

P=Path(__file__).parent

class ContractTests(unittest.TestCase):
    def module(self):
        self.assertTrue((P/'bridge.py').exists(), 'source-bound broker bridge not implemented')
        spec=importlib.util.spec_from_file_location('bridge',P/'bridge.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        return m
    def test_exact_source_and_depth_gate_prevents_unknown_or_changed_requests(self):
        b=self.module();rows=[{'id':'q0002','text':'How many?'},{'id':'q0009','text':'Where?'}]
        for arm in ('array','map'):
            m=b.match_public(b.batch.request_for(rows),rows)
            self.assertEqual(m['ids'],['q0002','q0009'])
            self.assertIsNone(b.match_public(b.batch.request_for([dict(rows[0],text='changed')]),rows))
            self.assertIsNone(b.match_public(b.batch.request_for([{'id':'q0020','text':'How many?'}]),rows))
            self.assertIn('JSON '+('array' if arm=='array' else 'object'),b.child_prompt(rows,arm))
    def test_projection_preserves_semantic_error_and_rejects_wrong_length_or_duplicate(self):
        b=self.module();ids=['q0002','q0009']
        self.assertEqual(b.project('["location","numeric value"]',ids,'array'),'{"q0002":"location","q0009":"numeric value"}')
        self.assertEqual(b.project('{"q0009":"numeric value","q0002":"location"}',ids,'map'),'{"q0002":"location","q0009":"numeric value"}')
        for raw,arm in [('["location"]','array'),('["LOCATION","location"]','array'),('{"q0002":"location","q0002":"location"}','map')]:
            with self.assertRaises(ValueError):b.project(raw,ids,arm)
    def test_runtime_keeps_original_result_and_logs_delivery_not_just_claim(self):
        b=self.module();from tempfile import TemporaryDirectory
        from dataclasses import dataclass
        @dataclass
        class Result:answer:str;session_dir:str
        rows=[{'id':'q0002','text':'How many?'}]
        with TemporaryDirectory() as d:
            state=b.Bridge('root',{'coordinate':'c','arm':'array','records':rows},Path(d)/'events')
            original=b.batch.request_for(rows)
            self.assertEqual(state.begin('nested','child',original,1),original)
            transformed=state.begin('root','child',original,1)
            self.assertNotEqual(transformed,original)
            result=Result('["location"]','session')
            projected=state.finish('task','root','child',original,result,1)
            self.assertEqual(result.answer,'["location"]')
            self.assertEqual(projected.answer,'{"q0002":"location"}')
            state.deliver('task')
            events=[json.loads(l) for l in (Path(d)/'events').read_text().splitlines()]
            self.assertEqual(events[-1]['event'],'delivered')
            self.assertEqual(events[-1]['raw_answer'],'["location"]')

if __name__=='__main__':unittest.main()
