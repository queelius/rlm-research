"""CPU contracts; no model weights, provider calls, or sampled code execution."""
import asyncio
import json
import unittest
from unittest.mock import patch
import protocol as p
import study as s

class Contracts(unittest.TestCase):
    def test_current_action_masks_reject_history_and_terminal(self):
        import learning
        good=p.row('a',[3,4],[5,151645],'corrective')
        self.assertEqual(learning.validate_turn(good),2)
        bad={**good,'labels':[3,-100,5,151645]}
        with self.assertRaises(ValueError):learning.validate_turn(bad)
        with self.assertRaises(ValueError):learning.selected_turn({'turns':{'terminal':good}},'terminal')

    def test_gate_uses_mechanism_not_copied_payload(self):
        import learning
        rows=[{'mechanism_nll':.2,'target_nll':.1} for _ in range(8)]
        self.assertTrue(learning.objective_gate(rows)['pass'])
        rows=[{'mechanism_nll':.001,'target_nll':4.} for _ in range(8)]
        self.assertFalse(learning.objective_gate(rows)['pass'])
        with self.assertRaises(ValueError):learning.objective_gate(rows[:7])

    def test_shared_environment_episode_does_not_reinstall_global_hooks(self):
        import collect
        class Env:
            async def run_slot(self,*args):return 'ran'
        class Interface:
            class e:
                @staticmethod
                def make_context(*args):return 'context'
        self.assertEqual(asyncio.run(collect.native_slot(Env(),Interface(),'task',{}, {},99)), 'ran')

    def test_visible_wrong_child_labels_retained_and_no_hidden_state(self):
        c={'records':[{'id':'a'},{'id':'b'}]}
        pieces,merged=p.visible_maps(['{"a":"human being"}','{"b":"location"}\nKeyError: bad'],c)
        self.assertEqual(merged,{'a':'human being','b':'location'})
        code,_=p.correction(pieces,{'users':['u02']},'human being')
        # Execute only our deterministic authored correction, with genuine-shaped fixture records.
        from io import StringIO
        with patch('builtins.open',return_value=StringIO('[{"id":"a","user":"u02"},{"id":"b","user":"u00"}]')),patch('sys.stdout',new_callable=StringIO) as out:
            exec(compile(code,'authored-correction-fixture','exec'),{})
        self.assertEqual(out.getvalue(),'1\n')
        with self.assertRaises(ValueError):p.visible_maps(['{"a":"human being","a":"location"}'],c)

    def test_membership_and_fixed_early_crossing(self):
        rows=s.read(s.ROOT/'inputs/TRAIN_PLAN.json');public=s.read(s.ROOT/'inputs/PUBLIC.json')
        self.assertEqual(len(rows),32);self.assertEqual(sum(r['metadata_error'] for r in rows),8)
        self.assertEqual({r['width'] for r in rows[:8]},{4,16})
        self.assertEqual({r['family'] for r in rows[:8]},{'single_user','union'})
        train={g for c in public if c['stratum']=='train' for g in c['group_ids']}
        test={g for c in public if c['stratum']!='train' for g in c['group_ids']}
        self.assertEqual(len(train),128);self.assertFalse(train&test)
        self.assertEqual(len(s.read(s.ROOT/'inputs/FREE_PLAN.json')),32)
        self.assertEqual(len(s.read(s.ROOT/'inputs/CONTROLLED_PLAN.json')),16)

    def test_error_probe_never_poisoned_first_producer_control(self):
        rows=s.read(s.ROOT/'inputs/TRAIN_PLAN.json')
        for row in rows:
            self.assertNotIn('synthetic user metadata',p.producer(row,0))
        self.assertEqual(sum(p.layout(r)['child_calls'] for r in rows),80)
        self.assertEqual(sum(p.layout(r)['error_turns'] for r in rows),8)
        self.assertEqual(sum(p.layout(r)['root_turns'] for r in rows),152)

    def test_replay_checks_sampling_as_well_as_prompt(self):
        body={'model':'c32','token_ids':[1,2],'sampling_params':{'seed':4,'max_tokens':200},'cache_salt':'0'}
        p.verify_replay(body,dict(body))
        changed={**body,'sampling_params':{'seed':5,'max_tokens':200}}
        with self.assertRaises(ValueError):p.verify_replay(body,changed)

if __name__=='__main__':unittest.main()
