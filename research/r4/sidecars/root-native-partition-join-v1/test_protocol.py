import importlib.util
import unittest
from collections import Counter


class ProtocolTests(unittest.TestCase):
    def module(self):
        self.assertIsNotNone(importlib.util.find_spec('protocol'), 'new protocol implementation is absent')
        import protocol
        return protocol

    def test_conserved_balanced_partitions_and_independent_join(self):
        p = self.module()
        worlds = p.worlds()
        self.assertEqual(len(worlds), 4)
        for index, world in enumerate(worlds):
            records = world['records']; a, b = world['query_products']
            truth = sorted({c for _, c, t in records if t == a} & {c for _, c, t in records if t == b})
            self.assertEqual(len(truth), 3 + 2 * index)
            self.assertEqual(p.oracle(records, [a, b]), truth)
            self.assertEqual(len({r[0] for r in records}), 48)
            for partition, chunks in world['partitions'].items():
                self.assertEqual([len(c) for c in chunks], [16, 16, 16])
                self.assertEqual(Counter(tuple(r) for c in chunks for r in c), Counter(map(tuple, records)))
                local = set()
                for chunk in chunks:
                    local |= {c for _, c, t in chunk if t == a} & {c for _, c, t in chunk if t == b}
                self.assertEqual(local, set() if partition == 'cross' else set(truth))

    def test_two_seed_six_cell_blocks_do_not_duplicate_direct(self):
        p = self.module(); rows = p.plan(p.worlds())
        self.assertEqual(len(rows), 48)
        self.assertEqual(len({r['id'] for r in rows}), 48)
        self.assertEqual(sum(r['representation'] == 'direct' for r in rows), 16)
        for block in range(8):
            group = [r for r in rows if r['block'] == block]
            self.assertEqual(len(group), 6)
            self.assertEqual(len({r['seed'] for r in group}), 1)
            self.assertEqual({(r['representation'], r['python']) for r in group},
                             {(r, t) for r in ('direct', 'colocated', 'cross') for t in (False, True)})

    def test_no_final_repair_and_null_is_not_observed_malformed(self):
        p = self.module()
        for raw in ('["c2","c1"]', '["c1","c1"]', 'Answer: ["c1"]', '```json\n["c1"]\n```', '["other"]'):
            self.assertEqual(p.score(raw, ['c1'], ['c1', 'c2'])['reward'], 0)
        self.assertEqual(p.score('["c1"]', ['c1'], ['c1', 'c2'])['reward'], 1)
        self.assertIsNone(p.score(None, ['c1'], ['c1', 'c2'], available=False)['reward'])
        self.assertEqual(p.score('', ['c1'], ['c1', 'c2'])['reward'], 0)

    def test_extraction_does_not_repair_incomplete_or_wrong_fields(self):
        p = self.module(); chunk = [['r1', 'c1', 'A'], ['r2', 'c1', 'B']]
        for raw in ('[["r1","c1","A"]]', '[["r1","c1","A"],["r2","c2","B"]]', 'not-json'):
            result = p.extraction(raw, chunk)
            self.assertFalse(result['available'])
            self.assertNotEqual(result['rows'], chunk)
        self.assertTrue(p.extraction('[["r2","c1","B"],["r1","c1","A"]]', chunk)['available'])


if __name__ == '__main__':
    unittest.main()
