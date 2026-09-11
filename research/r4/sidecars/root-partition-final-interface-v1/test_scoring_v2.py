"""One wrong-route versus corrupted-native regression, plus exact amended argv."""
import json
import unittest
from copy import deepcopy
import study as s
import protocol as p

class Amendment(unittest.TestCase):
    def test_verified_tool_route_is_observed_zero_but_mismatch_stays_null(self):
        import scoring_v2
        tokenizer=s.tokenizer();code='print(2)';envelope='<tool_call>\n'+json.dumps({'name':'ipython','arguments':{'code':code}})+'\n</tool_call>'
        ids=tokenizer.encode(envelope,add_special_tokens=False)+[151645]
        source={'actual_native_prompt_token_ids':[1,2]}
        raw={'model':s.MODEL['alias'],'prompt_token_ids':[1,2],'usage':{'prompt_tokens':2,'completion_tokens':len(ids)},'choices':[{'token_ids':ids,'finish_reason':'tool_calls','message':{'role':'assistant','content':None,'tool_calls':[{'type':'function','function':{'name':'ipython','arguments':json.dumps({'code':code})}}]}}]}
        content,finish,usage=scoring_v2.verified_response(raw,{},source,tokenizer)
        score=p.score(content,['c01'],finish)
        self.assertTrue(score['available']);self.assertEqual(score['reward'],0)
        bad=deepcopy(raw);bad['choices'][0]['message']['tool_calls'][0]['function']['arguments']=json.dumps({'code':'print(3)'})
        score=p.score(None,['c01'],None,available=False)
        with self.assertRaises(ValueError):scoring_v2.verified_response(bad,{},source,tokenizer)
        self.assertIsNone(score['reward'])

    def test_amended_owner_and_collector_namespace_agree(self):
        import owner_v2
        argv=owner_v2.collector_argv(s.ATTEMPT/'owned-service',s.ATTEMPT,999)
        self.assertEqual(argv[1],str(s.ROOT/'collect_v2.py'))
        self.assertEqual(owner_v2.validate_argv(argv)['output'],s.ATTEMPT/'rollout')
        old=argv[:];old[1]=str(s.ROOT/'collect.py')
        with self.assertRaises(ValueError):owner_v2.validate_argv(old)

if __name__=='__main__':unittest.main()
