import json
import unittest


class InterfaceTests(unittest.TestCase):
    def test_all_facts_order_and_accurate_formats(self):
        import protocol as p
        for world in p.worlds():
            packages = {a: p.evidence(world, a, []) for a in p.REPRESENTATIONS}
            self.assertEqual(packages['T']['text'], packages['F']['text'])
            self.assertEqual(packages['F']['files'], packages['I']['files'])
            self.assertEqual(packages['T']['files']['evidence.dat'], p.record_text(world['records']))
            typed = json.loads(packages['I']['text'])
            self.assertEqual([[x['record_id'], x['customer_id'], x['product']] for x in typed], world['records'])
            self.assertTrue(all(list(x) == ['record_id', 'customer_id', 'product'] for x in typed))
            for arm, package in packages.items():
                prompt = p.prompt(world, package)
                self.assertIn('same purchase facts', prompt)
                self.assertIn('JSON array of objects' if arm == 'I' else 'sentence lines', prompt)
                self.assertEqual(package['acquisition_ids'], [])
                self.assertEqual(set(package['files']), {'evidence.dat'})

    def test_24_paired_fixed_slots_and_order(self):
        import protocol as p
        plan = p.plan(p.worlds())
        self.assertEqual(len(plan), 24)
        self.assertEqual(len({r['id'] for r in plan}), 24)
        self.assertEqual(len({r['seed'] for r in plan}), 8)
        for block in range(8):
            group = [r for r in plan if r['block'] == block]
            self.assertEqual({r['representation'] for r in group}, {'T', 'F', 'I'})
            self.assertEqual(len({r['seed'] for r in group}), 1)
            self.assertTrue(all(r['python'] for r in group))
        self.assertEqual(plan, p.plan(p.worlds()))
        self.assertTrue(all(p.null_row(r, 'planned')['reward'] is None for r in plan))

    def test_strict_answer_not_episode_completion(self):
        import collect as c
        trace = {'root_reply': '[]', 'is_completed': True}
        self.assertIsNone(c.terminal_score(trace, None, [], ['c1'])['reward'])
        capture = {'status': 'returned', 'native_response': {'finish_reason': 'length', 'message': {'content': '[]'}}}
        self.assertEqual(c.terminal_score(trace, capture, [], ['c1'])['reward'], 1)
        capture['native_response']['message']['content'] = 'different'
        self.assertIsNone(c.terminal_score(trace, capture, [], ['c1'])['reward'])


if __name__ == '__main__': unittest.main()
