import collections
import unittest
import experiment as e
import contract
import driver
import results

class Tests(unittest.TestCase):
    def test_24_physical_32_logical_sharing_and_call_budget(self):
        contexts=e.c.read(e.PRIOR/'inputs/PUBLIC.json');plan,refs=e.plan_for(contexts)
        self.assertEqual((len(plan),len(refs)),(24,32));self.assertEqual(len({r['id'] for r in plan}),24)
        self.assertEqual(collections.Counter(r['arm'] for r in plan),dict.fromkeys(e.ARMS,8))
        self.assertEqual(sorted(collections.Counter(r['execution_id'] for r in refs).values()),[1]*16+[2]*8)
        for offset in range(0,24,3):self.assertEqual(len({r['block'] for r in plan[offset:offset+3]}),1)
        calls=0;distinct=set()
        for r in plan:
            ctx=contexts[r['context_index']]
            selected=ctx['records'] if r['controller']=='all16' else [x for x in ctx['records'] if x['user']==ctx['query_user']]
            self.assertEqual(len(selected),128 if r['controller']=='all16' else 8)
            calls+=(len(selected)+15)//16
            for i in range(0,len(selected),16):
                batch=selected[i:i+16];prompt=contract.batch.request_for(batch);distinct.add(prompt)
                match=contract.match_request(prompt,e.catalogs(contexts)[str(r['context_window_id'])]);self.assertTrue(match['matched'])
                ids=[x['id'] for x in batch];schema=match['schema']
                self.assertEqual(schema['required'],ids);self.assertEqual(list(schema['properties']),ids)
                self.assertFalse(schema['additionalProperties'])
                for value in schema['properties'].values():self.assertEqual(value,{'type':'string','enum':contract.LABELS})
        self.assertEqual(calls,136)
        self.assertEqual(len(distinct),36)
    def test_sampler_root_boundary_and_concurrent_decisions(self):
        d=contract.Decisions();ctx=e.c.read(e.PRIOR/'inputs/PUBLIC.json')[0];catalog=e.catalogs([ctx])['1800']
        for i in (0,1):
            m={'depth':1,'invocation':str(i),'kind':'ordinary'};prompt=contract.batch.request_for(ctx['records'][i:i+1])
            result=d.choose('c','user_all',m,[{'role':'user','content':prompt}],catalog)
            self.assertEqual(result['requested_ids'],[ctx['records'][i]['id']]);self.assertTrue(result['apply'])
        root=d.choose('c','user_all',{'depth':0,'invocation':'root','kind':'ordinary'},[{'role':'user','content':prompt}],catalog)
        self.assertFalse(root['apply'])
    def test_inclusive_caps_and_original_task_bytes(self):
        self.assertEqual(driver.collection_deadline(100,200),1640)
        self.assertLessEqual(driver.collection_deadline(100,1500),1660)
        self.assertEqual(e.environment_config()['agent']['runtime']['image'],e.IMAGE)
        for name,task in e.make_tasks().items():
            arm='user_all' if name.endswith('user') else 'global_shared'
            self.assertEqual(e.with_prompt(task,arm).data,task.data)

    def test_operator_unanswered_remains_null_and_numeric_success_observable(self):
        raw={'traces':[{'is_completed':True,'root_reply':'','task':{'data':{'answer':'[1]'}}}]}
        self.assertIsNone(results.episode_metrics(raw,0)['strict_reward'])
        raw['traces'][0]['root_reply']='Answer: 1'
        self.assertEqual(results.episode_metrics(raw,0)['strict_reward'],1)
        raw['traces'][0]['root_reply']='wrong'
        self.assertEqual(results.episode_metrics(raw,0)['strict_reward'],0)

if __name__=='__main__':unittest.main()
