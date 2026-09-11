import asyncio
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time
import unittest

ROOT=Path(__file__).parent
class RuntimeTests(unittest.TestCase):
    def test_fixed_contexts_expand_into_32_complete_global_scalar_slots(self):
        import study as s
        contexts,gold,tasks=s.inputs();plan=s.plan_for(contexts)
        self.assertEqual([len(c['records']) for c in contexts],[32,32,128,128])
        self.assertEqual(len(plan),32);self.assertEqual(len(tasks),8)
        for c in contexts:
            for family in ('count','checksum'):
                prompt=tasks['bridge-'+c['id']+'-'+family]['prompt']
                self.assertIn(f'list of {len(c["records"])} records',prompt)
                self.assertIn('entire file',prompt)
                self.assertIsInstance(gold[c['id']]['answers'][family],int)
    def test_actual_entrypoints_import_and_all_32_pairs_dispatch(self):
        self.assertTrue((ROOT/'collect.py').exists(),'32-slot collector not implemented')
        for file in ('collect.py','driver.py'):
            result=subprocess.run([sys.executable,str(ROOT/file),'--help'],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
        import collect
        rows=[{'id':i,'pair_id':i//2,'pair_order':i%2} for i in range(32)];seen=[]
        async def run():
            async def one(row):seen.append(row['id']);await asyncio.sleep(.001)
            self.assertIsNone(await collect.dispatch(rows,one,time.time()+5))
        asyncio.run(run());self.assertEqual(sorted(seen),list(range(32)))
        for i in range(0,32,2):self.assertLess(seen.index(i),seen.index(i+1))
    def test_cancellation_settles_inflight_row_finalizers(self):
        self.assertTrue((ROOT/'collect.py').exists(),'settled collector not implemented')
        import collect
        done=[]
        async def run():
            async def one(row):
                try:await asyncio.sleep(1)
                finally:await asyncio.sleep(.01);done.append(row['id'])
            rows=[{'id':i,'pair_id':i//2,'pair_order':i%2} for i in range(32)]
            self.assertEqual(await collect.dispatch(rows,one,time.time()+.03),'collection_wall_cap')
        asyncio.run(run());self.assertEqual(len(done),4)
    def test_native_decision_has_root_boundary_and_one_grammar_per_invocation(self):
        import bridge,contract
        records=[{'id':'q0009','text':'Where?'}];catalog={'records':records}
        d=contract.Decisions();meta={'invocation':'root','depth':0,'kind':'ordinary'}
        messages=[{'role':'user','content':bridge.child_prompt(records,'array')}]
        self.assertFalse(d.choose('c','array',meta,messages,catalog)['apply'])
        meta={'invocation':'child','depth':1,'kind':'ordinary'}
        result=d.choose('c','array',meta,messages,catalog)
        self.assertTrue(result['apply']);self.assertEqual(result['schema']['maxItems'],1)
        self.assertEqual(d.choose('c','array',meta,messages+[{'role':'assistant','content':'other'}],catalog),result)
        self.assertFalse(d.choose('d','map',meta,messages,catalog)['apply'])
        self.assertFalse(d.choose('e','array',{**meta,'depth':2},messages,catalog)['apply'])
    def test_actual_owned_run_clips_collection_and_records_32(self):
        import driver
        from tempfile import TemporaryDirectory
        from unittest.mock import patch
        from types import SimpleNamespace
        calls=[]
        suite=SimpleNamespace(life=SimpleNamespace(install=lambda:None),
            start_service=lambda *a:calls.append(('start',a)),command=lambda *a:calls.append(('collect',a)),
            release_service=lambda *a:calls.append(('release',a)))
        with TemporaryDirectory() as d,patch.object(driver,'dependencies',return_value=suite),patch.object(driver.s,'verify',return_value={'binding':{}}),patch.object(driver.s,'sha',return_value='fixture'),patch.dict('os.environ',{'CUDA_VISIBLE_DEVICES':'fixture-not-a-device'}):
            result=driver.run(Path(d)/'out');run=json.loads((Path(d)/'out/RUN.json').read_text())
        self.assertTrue(result['complete']);self.assertEqual(result['planned'],32)
        self.assertEqual([v[0] for v in calls],['start','collect','release'])
        argv=calls[1][1][2]
        self.assertEqual(Path(argv[1]),ROOT/'collect.py')
        self.assertLessEqual(float(argv[-1]),run['work_deadline_epoch'])
        self.assertEqual(calls[1][1][3],1530)

if __name__=='__main__':unittest.main()
