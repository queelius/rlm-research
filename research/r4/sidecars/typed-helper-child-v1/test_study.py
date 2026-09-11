import unittest
import collections
import copy
import experiment as e
import hooks
import results

class StudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.tasks=e.make_tasks();cls.plan=e.build_plan(cls.tasks)

    def test_all_36_and_balanced_triple_work_units(self):
        self.assertEqual(len(self.plan),36)
        chunks=[self.plan[i:i+3] for i in range(0,36,3)]
        self.assertEqual(len({r['seed'] for r in self.plan}),12)
        self.assertEqual(set(collections.Counter(tuple(r['arm'] for r in chunk) for chunk in chunks).values()),{2})
        for chunk in chunks:
            self.assertEqual(len({r['matched_id'] for r in chunk}),1)
            self.assertEqual({r['arm'] for r in chunk},set(e.ARMS))
        source=e.u.receipt.collector_source()
        self.assertIn('range(0, len(plan), 3)',source)
        self.assertIn('plan[offset : offset + 3]',source)
        self.assertNotIn('plan[offset : offset + 2]',source)
        self.assertEqual(e.collector().IMAGE_ID,'sha256:'+e.IMAGE)

    def test_root_prompt_interface_and_context_equal(self):
        for task in self.tasks.values():
            self.assertEqual(e.with_prompt(task,'restored_raw').data,e.with_prompt(task,'typed').data)
        binding=e.binding_for(e.c.read(e.UPTAKE/'SPEC.json')['policies']['step8'])
        context=e.make_context(e.old.planned_endpoint(binding),self.plan[0])
        self.assertEqual(context.client.headers[e.HEADER],self.plan[0]['id'])
        self.assertNotIn('structured_outputs',context.sampling.model_dump())

    def test_bad_trusted_metadata_rejected_and_root_alias_retained(self):
        h={'x-rlm-role-depth':'0','x-rlm-role-invocation':'cpu','x-rlm-role-request-id':'a'*32,'x-rlm-role-kind':'ordinary'}
        body={'model':'root','messages':[{'role':'user','content':'lookalike'}]}
        self.assertEqual(hooks.role.route(copy.deepcopy(body),h,'child',{'root':'root','children':['child']})['actual_alias'],'root')
        for change in ({'x-rlm-role-depth':'2'},{'x-rlm-role-kind':'compaction'},{'x-rlm-role-request-id':'bad'}):
            with self.assertRaises(ValueError): hooks.role.route(copy.deepcopy(body),{**h,**change},'child',{'root':'root','children':['child']})
        with self.assertRaises(ValueError): hooks.role.route(body,{},'child',{'root':'root','children':['child']})

    def test_completed_scored_empty_is_zero_not_infrastructure_null(self):
        episode={'ok':True,'traces':[{'ok':True,'is_completed':True,'root_reply':'','metrics':{'strict_terminal_valid':False,'official_correctness':0},'rewards':{'correctness':{'score':0}},'calls':[],'nodes':[]}]}
        self.assertEqual(results.episode_metrics(episode,0)['strict_reward'],0)
        self.assertIsNone(results.episode_metrics({'ok':False,'traces':[]},0)['strict_reward'])
        summary=results.summarize([],self.plan)
        self.assertEqual(summary['primary']['unknown_pairs'],12)
        self.assertEqual([r['planned'] for r in summary['cells']],[12,12,12])

if __name__=='__main__': unittest.main()
