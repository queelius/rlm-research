import unittest,json
from collections import Counter
import protocol as p
class FreshTests(unittest.TestCase):
    def test_deterministic_fresh_eight_worlds_and_reversal(self):
        worlds=p.worlds();self.assertEqual(worlds,p.worlds());self.assertEqual(len(worlds),8)
        old=p.inventory();old_ids={v for w in old for r in w['records'] for v in r[:2]}
        all_ids=[]
        for w in worlds:
            self.assertEqual(len(w['records']),48);self.assertEqual(len(w['customers']),12)
            self.assertEqual(len(set(r[0] for r in w['records'])),48)
            self.assertTrue(set(w['customers']).isdisjoint(old_ids))
            self.assertTrue({r[0] for r in w['records']}.isdisjoint(old_ids))
            a,b=p.ordered_world(w,'random'),p.ordered_world(w,'reverse')
            self.assertEqual(b['records'],list(reversed(a['records'])))
            self.assertEqual(Counter(map(tuple,a['records'])),Counter(map(tuple,w['records'])))
            self.assertEqual(p.oracle(a['records'],w['query_products']),p.oracle(b['records'],w['query_products']))
            all_ids.extend(r[0] for r in w['records'])
        self.assertEqual(len(set(all_ids)),384)
    def test_balanced_32cells_one_seed_per_world(self):
        plan=p.plan(p.worlds());self.assertEqual(len(plan),32)
        self.assertEqual(len({r['id'] for r in plan}),32)
        positions={cell:Counter() for cell in [('I','random'),('E','random'),('I','reverse'),('E','reverse')]}
        for wi in range(8):
            group=[r for r in plan if r['world_index']==wi]
            self.assertEqual(len({r['seed'] for r in group}),1)
            self.assertEqual({(r['representation'],r['record_order']) for r in group},set(positions))
            for r in group:positions[(r['representation'],r['record_order'])][r['pair_position']]+=1
        self.assertTrue(all(c==Counter({0:2,1:2,2:2,3:2}) for c in positions.values()))
    def test_representation_pair_same_canonical_file_and_primary(self):
        for world in p.worlds():
            for order in p.ORDERS:
                w=p.ordered_world(world,order);i,e=[p.evidence(w,a,[]) for a in p.REPRESENTATIONS]
                self.assertEqual(i['files'],e['files']);self.assertEqual(e['text'],'')
                self.assertEqual(i['text'],i['files']['evidence.dat'])
                self.assertEqual(p.prompt(w,i).replace(i['text'],''),p.prompt(w,e))
                gold=p.oracle(w['records'],w['query_products'])
                self.assertEqual(p.score(json.dumps(gold),gold,w['customers'])['reward'],1)
                self.assertEqual(p.score('Answer: '+json.dumps(gold),gold,w['customers'])['reward'],0)
if __name__=='__main__':unittest.main()
