import importlib.util
from pathlib import Path
import unittest
P=Path(__file__).parent
class ResultTests(unittest.TestCase):
    def load(self):
        self.assertTrue((P/'results.py').exists(),'prospective null/ASCII scoring missing')
        import results
        return results
    def test_whole_ascii_empty_observed_zero_and_unavailable_null(self):
        r=self.load()
        self.assertEqual(r.endpoint('Answer: 9',9,True,True)['score'],1)
        for text in ('','Answer: ９','Reason. Answer: 9','Answer: 9\nmore'):
            self.assertEqual(r.endpoint(text,9,True,True)['score'],0)
        self.assertIsNone(r.endpoint('',9,False,False)['score'])
    def test_cost_reads_cached_input_from_raw_wire_json_string(self):
        r=self.load()
        value={'native_wire_response':{'body':'{"usage":{"prompt_tokens":20,"completion_tokens":3,"prompt_tokens_details":{"cached_tokens":16}}}'}}
        self.assertEqual(r.usage(value),{'input':20,'cached':16,'uncached':4,'output':3})
if __name__=='__main__':unittest.main()
