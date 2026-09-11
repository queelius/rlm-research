import importlib
import json
import unittest
from pathlib import Path
import tempfile
import transfer_study as s

class EntryTests(unittest.TestCase):
    def modules(self):
        self.assertTrue((s.ROOT/'owner.py').exists(),'new owner absent')
        return importlib.import_module('owner'),importlib.import_module('collect')
    def test_exact_owner_cli_can_only_dispatch_free16(self):
        o,c=self.modules();stage=s.ATTEMPT/'service-joint';out=s.ATTEMPT/'joint/free'
        argv=o.collector_argv(stage,out,1234.)
        args=c.parse_args(argv[2:]);self.assertEqual((args.mode,args.plan,args.stop),('free','FREE_PLAN.json',16))
        self.assertEqual(args.output,out);self.assertEqual(args.binding,stage/'BINDING.json')
        with self.assertRaises(ValueError):c.validate_args(type('Args',(),{**vars(args),'mode':'capture'})())
    def test_all48_planned_before_service_and_wrong_output_rejected(self):
        o,c=self.modules();rows=o.planned_inventory(s.ATTEMPT)
        self.assertEqual(len(rows),48);self.assertTrue(all(r['reward'] is None and not r['available'] for r in rows))
        self.assertEqual({r['arm'] for r in rows},{'unchanged','joint','reduction_stop'})
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):o.check_output(Path(d)/'wrong')
    def test_physical_rejection_is_attempt_not_completion_or_measured_billing(self):
        o,c=self.modules();rows=[dict(physical_request_attempt=True,body=dict(token_ids=[1,2]),status=400,error={'message':'context length'}),dict(physical_request_attempt=True,body=dict(token_ids=[1]),status=200,response={'choices':[{'token_ids':[3,4]}]})]
        cost=c.physical_cost(rows)
        self.assertEqual((cost['physical_request_attempts'],cost['returned_native_completions'],cost['input_tokens'],cost['output_tokens_known']),(2,1,3,2))
        self.assertEqual(cost['output_usage_unknown_attempts'],1);self.assertIsNone(cost['provider_billing'])
    def test_native_final_is_strict_and_missing_stays_null(self):
        o,c=self.modules();actual=dict(status='returned',native_response=dict(finish_reason='stop',message=dict(content='maybe 2',tool_calls=[])))
        self.assertEqual(c.original.metrics.score(dict(root_reply='maybe 2'),actual,2)['reward'],0)
        self.assertIsNone(c.original.metrics.score(dict(root_reply='Answer: 2'),actual,2)['reward'])
    def test_ready_identity_round_trip(self):
        value={'z':1,'a':{'y':2,'b':3}}
        self.assertEqual(s.digest(value),s.digest(json.loads(json.dumps(value,sort_keys=True))))

if __name__=='__main__':unittest.main()
