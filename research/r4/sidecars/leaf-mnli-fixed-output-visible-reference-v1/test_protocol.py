"""Catch accidental prompt/tag/grammar changes and wrong visible-name oracle."""
import importlib.util,json,unittest
from pathlib import Path
class ProtocolTests(unittest.TestCase):
    def test_all_three_arms_fixed_tags_and_only_display_ids_change(self):
        import study as s,protocol as p
        contexts=s.read(s.ANCESTOR/'DATA.json')['contexts']
        for ci,c in enumerate(contexts):
            rows=[dict(context_index=ci,arm=arm,seed=981624101+ci) for arm in p.ARMS]
            bodies=[p.request(c,r) for r in rows]
            fixed=[r['id'] for r in c['records']][17:]+[r['id'] for r in c['records']][:17]
            self.assertEqual([p.expected_tags(c,arm) for arm in p.ARMS],[fixed]*3)
            self.assertEqual(bodies[0]['structured_outputs'],bodies[1]['structured_outputs']);self.assertEqual(bodies[1]['structured_outputs'],bodies[2]['structured_outputs'])
            visible=[json.loads(b['messages'][1]['content'].split('Input records (id, premise, hypothesis, requested_tag):\n')[1]) for b in bodies]
            self.assertEqual([v['id'] for v in visible[0]],fixed)
            self.assertEqual([v['id'] for v in visible[1]],[r['id'] for r in c['records']])
            for arm in visible:
                self.assertEqual([{k:v for k,v in r.items() if k!='id'} for r in arm],[dict(premise=r['premise'],hypothesis=r['hypothesis'],requested_tag=t) for r,t in zip(c['records'],fixed)])
    def test_plan_has16_paired_clusters(self):
        import protocol as p
        rows=p.plan();self.assertEqual(len(rows),48)
        for ci in range(16):
            group=[r for r in rows if r['context_index']==ci]
            self.assertEqual(len(group),3);self.assertEqual({r['seed'] for r in group},{981624101+ci})
    def test_active_closure_preserves_three_superseded_receipts(self):
        import prepare,study as s
        source,historical,manifests=prepare.source_closure()
        self.assertEqual(len(historical),3)
        for path,pin in source.items():self.assertEqual(s.sha(path),pin)
        for path,pin in historical.items():self.assertEqual(source[path],pin)
if __name__=='__main__':unittest.main()
