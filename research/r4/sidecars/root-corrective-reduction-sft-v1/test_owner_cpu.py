"""Scoped ownership/endpoint contract tests with no service/process launch."""
import tempfile
import unittest
from unittest.mock import patch
import study as s
import owner
import collect

class OwnerContracts(unittest.TestCase):
    def test_missing_credential_stops_before_output_or_any_owned_action(self):
        with patch.object(s,'runtime',side_effect=ValueError('credential missing')),patch.object(s,'verify',side_effect=AssertionError('must not verify after credential failure')):
            with self.assertRaisesRegex(ValueError,'credential missing'):owner.execute(s.ATTEMPT)
        self.assertFalse(s.ATTEMPT.exists())

    def test_native_final_text_and_no_tools_required_even_after_http_success(self):
        capture={'status':'returned','native_response':{'finish_reason':'stop','message':{'content':'Answer: 2','tool_calls':[]}}}
        self.assertEqual(collect.metrics.score({'root_reply':'Answer: 2'},capture,2)['reward'],1)
        self.assertIsNone(collect.metrics.score({'root_reply':'Answer: 3'},capture,3)['reward'])
        capture['native_response']['message']['tool_calls']=[{'name':'ipython'}]
        self.assertIsNone(collect.metrics.score({'root_reply':'Answer: 2'},capture,2)['reward'])

    def test_completed_malformed_final_is_zero_not_null(self):
        capture={'status':'returned','native_response':{'finish_reason':'stop','message':{'content':'maybe 2','tool_calls':[]}}}
        result=collect.metrics.score({'root_reply':'maybe 2'},capture,2)
        self.assertTrue(result['available']);self.assertEqual(result['reward'],0)

if __name__=='__main__':unittest.main()
