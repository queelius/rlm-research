import importlib.util
import json
import unittest
from collections import Counter


class ExternalizationTests(unittest.TestCase):
    def test_only_raw_inline_block_differs_and_file_preserves_all_facts(self):
        self.assertIsNotNone(importlib.util.find_spec('protocol'), 'isolated protocol is absent')
        import protocol as p
        self.assertEqual(p.REPRESENTATIONS, ('I','E'))
        for world in p.worlds():
            inline, external = [p.evidence(world,a,[]) for a in ('I','E')]
            self.assertEqual(inline['files'],external['files'])
            self.assertEqual(external['text'],'')
            self.assertEqual(inline['text'],inline['files']['evidence.dat'])
            triples=[[r['record_id'],r['customer_id'],r['product']] for r in json.loads(inline['text'])]
            self.assertEqual(triples,world['records']);self.assertEqual(len(triples),48)
            self.assertEqual(p.prompt(world,inline).replace(inline['text'],''),p.prompt(world,external))
            self.assertTrue(all(r[0] not in p.prompt(world,external) for r in world['records']))

    def test_16_planned_slots_have_balanced_orders_fresh_paired_seeds(self):
        self.assertIsNotNone(importlib.util.find_spec('protocol'), 'isolated protocol is absent')
        import protocol as p
        rows=p.plan(p.worlds());self.assertEqual(len(rows),16);self.assertEqual(len({r['id'] for r in rows}),16)
        orders=[]
        for block in range(8):
            pair=[r for r in rows if r['block']==block]
            self.assertEqual({r['representation'] for r in pair},{'I','E'})
            self.assertEqual({r['seed'] for r in pair},{981492101+block})
            self.assertEqual(len({r['world_id'] for r in pair}),1)
            orders.append(tuple(r['representation'] for r in pair))
        self.assertEqual(Counter(orders),{('I','E'):4,('E','I'):4})


if __name__=='__main__':unittest.main()
