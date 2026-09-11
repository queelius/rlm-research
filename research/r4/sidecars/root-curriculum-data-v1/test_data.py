"""Focused data-only checks; no runtime, model, or training imports."""
import json
import unittest
from collections import Counter
from pathlib import Path

import prepare_data as p


class CandidateDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = p.build()

    def test_reproduction_and_group_disjointness(self):
        for name, value in self.outputs.items():
            self.assertEqual(value, json.loads((p.ROOT / name).read_text()))
        groups = self.outputs['GROUPS.json']
        ids = [g for c in groups for g in c['group_ids']]
        self.assertEqual(len(ids), 3136)
        self.assertEqual(len(set(ids)), len(ids))
        self.assertEqual(len({c['context_sha256'] for c in groups}), len(groups))

    def test_schedule_is_label_independent_and_has_true_size_holdout(self):
        groups = self.outputs['GROUPS.json']
        train = [c for c in groups if c['split'] == 'training']
        self.assertEqual(Counter(c['size'] for c in train), {16:8, 32:8, 64:8})
        schedule = self.outputs['CANDIDATE_SCHEDULE.json']
        visits = Counter(t.split(':')[0] for r in schedule for t in r['tasks'])
        self.assertEqual(len(schedule), 16)
        self.assertTrue(all(len(r['tasks']) == 3 for r in schedule))
        self.assertEqual(set(visits.values()), {2})
        tasks = [t for r in schedule for t in r['tasks']]
        self.assertEqual(len(tasks), len(set(tasks)))
        self.assertEqual(Counter(t.split(':')[1] for t in tasks), {
            'human_being':12, 'numeric_value':12, 'entity':12, 'location':12})
        self.assertEqual({c['size'] for c in groups if c['split'] == 'transfer-size'}, {128,256})
        rows = [{'group_id':str(i), 'gold':'positive'} for i in range(12)]
        altered = [{**r, 'gold':'negative'} for r in rows[::-1]]
        self.assertEqual([r['group_id'] for r in p.order(rows,'test')],
                         [r['group_id'] for r in p.order(altered,'test')])

    def test_public_host_boundary_and_all_aggregate_gold(self):
        public, host = self.outputs['PUBLIC.json'], self.outputs['HOST_GOLD.json']
        contexts = {c['id']:c for c in public['contexts']}
        for c in contexts.values():
            self.assertEqual(set(c), {'id','text'})
        for task in public['tasks']:
            self.assertEqual(set(task), {'id','context_id','question'})
            h = host[task['id']]
            records = host[task['context_id']]['records']
            self.assertEqual(h['answer_integer'], sum(r['gold'] == h['target_label'] for r in records))
            text = contexts[task['context_id']]['text']
            self.assertEqual(text.count('\n'), len(records))
            for r in records:
                self.assertIn('Instance: ' + r['question'] + '\n', text)
        # Public task labels are requested categories, not hidden per-record labels.
        self.assertNotIn('records', public)


if __name__ == '__main__':
    unittest.main()
