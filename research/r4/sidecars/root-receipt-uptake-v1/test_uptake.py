import ast
import asyncio
import collections
import importlib
import unittest
from pathlib import Path
from unittest.mock import patch


class UptakeTests(unittest.TestCase):
    def study(self):
        self.assertIsNotNone(importlib.util.find_spec('experiment'), 'uptake implementation absent')
        return importlib.import_module('experiment')

    def test_paragraph_only_intervention_and_public_setup(self):
        e = self.study()
        for task in e.make_tasks().values():
            d, r, v = [e.with_prompt(task, arm) for arm in e.ARMS[1:]]
            self.assertEqual(r.data.prompt.replace(e.procedure(task)+'\n\n','',1),d.data.prompt)
            self.assertEqual(r.data.prompt.count(e.procedure(task)),1)
            self.assertEqual(e.example_code(d.data.prompt),e.example_code(r.data.prompt))
            self.assertIn('labels_by_id = receipt["labels_by_id"]',e.example_code(v.data.prompt))
            self.assertNotIn('.receipt()',e.example_code(r.data.prompt))
            normalized=v.data.prompt.replace('This arm also exposes child.receipt(), an optional structural validation report.',
                'This arm exposes child.answer and native metadata; child.receipt() is not available.')
            normalized=normalized.replace('receipt = child.receipt()\nprint(receipt)\nlabels_by_id = receipt["labels_by_id"]',
                'labels_by_id = json.loads(child.answer)')
            self.assertEqual(normalized,r.data.prompt)
            for variant in (d,r,v):
                compile(e.example_code(variant.data.prompt),'snippet','exec',flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
                self.assertEqual(variant.data.context,task.data.context)
                self.assertEqual(variant.data.answer,task.data.answer)
            self.assertEqual(e.with_prompt(task,'unchanged').data.prompt,e.old.with_prompt(task,'unchanged').data.prompt)
        class Runtime:
            def __init__(self): self.files={}
            async def write(self,path,data): self.files[path]=data
        runtime=Runtime()
        asyncio.run(e.with_prompt(task,'restored_receipt').setup(None,runtime))
        self.assertEqual(set(runtime.files),{'context.txt','receipt_api.py','receipt_catalog.json','receipt_config.json'})
        self.assertNotIn(b'"answer_category"',runtime.files['receipt_catalog.json'])
        self.assertNotIn(b'"label"',runtime.files['receipt_catalog.json'])

    def test_complete_balanced_quadruplets_and_root_order(self):
        e=self.study()
        plan=e.build_plan(e.make_tasks())
        self.assertEqual(len(plan),96)
        self.assertEqual(sorted({r['seed'] for r in plan}),list(range(981274301,981274313)))
        self.assertEqual(collections.Counter(r['phase'] for r in plan),{'originalA':24,'step8':48,'originalB':24})
        for i in range(0,96,4):
            chunk=plan[i:i+4]
            self.assertEqual({r['arm'] for r in chunk},set(e.ARMS))
            self.assertEqual(len({r['pair_id'] for r in chunk}),1)
        for weight in ('original','step8'):
            rows=[r for r in plan if r['weight']==weight]
            positions=collections.Counter((r['arm'],r['pair_order']) for r in rows)
            self.assertEqual(set(positions.values()),{3})
        for seed in range(981274301,981274313):
            self.assertEqual(len([r for r in plan if r['seed']==seed]),8)

    def test_actual_collector_queue_dispatches_four_not_two_or_three(self):
        e=self.study()
        tree=ast.parse(e.collector_source())
        run=next(n for n in tree.body if isinstance(n,ast.AsyncFunctionDef) and n.name=='run')
        loop=next(n for n in run.body if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='offset')
        code=compile(ast.fix_missing_locations(ast.Module(body=[loop],type_ignores=[])),'actual-queue','exec')
        for phase in e.PHASES:
            plan=[r for r in e.build_plan(e.make_tasks()) if r['phase']==phase]
            queue=asyncio.Queue()
            exec(code,{'plan':plan,'queue':queue})
            chunks=[]
            while not queue.empty(): chunks.append(queue.get_nowait())
            self.assertTrue(all(len(c)==4 and len({r['pair_id'] for r in c})==1 for c in chunks))
            self.assertEqual([r for c in chunks for r in c],plan)

    def test_shared_deadline_and_spent_collection_cannot_reset(self):
        self.assertIsNotNone(importlib.util.find_spec('driver'),'bounded driver absent')
        d=importlib.import_module('driver')
        self.assertEqual(d.collection_cap(600,1000,1200,3480,100),600)
        self.assertEqual(d.collection_cap(600,2300,0,3480,100),100)
        self.assertLessEqual(d.collection_cap(1200,0,0,3480,3450),0)
        self.assertLessEqual(d.collection_cap(600,2400,0,3480,100),0)

    def test_absence_observer_preserves_permission_errors(self):
        self.assertIsNotNone(importlib.util.find_spec('driver'),'lifecycle adapter absent')
        d=importlib.import_module('driver')
        class Coordinator:
            @staticmethod
            def process_identity(pid): raise ProcessLookupError(pid)
        fake=Coordinator()
        d.install_observer(fake)
        self.assertIsNone(fake.process_identity(1))
        class Denied:
            @staticmethod
            def process_identity(pid): raise PermissionError(pid)
        denied=Denied()
        d.install_observer(denied)
        with self.assertRaises(PermissionError): denied.process_identity(1)

    def test_unrun_outcomes_remain_unknown_in_summaries(self):
        self.assertIsNotNone(importlib.util.find_spec('results'),'uptake outcomes absent')
        results=importlib.import_module('results')
        e=self.study()
        plan=e.build_plan(e.make_tasks())
        report=results.summarize([],plan)
        self.assertEqual(report['planned'],96)
        self.assertEqual(report['recorded'],0)
        self.assertEqual(len(report['unrun_coordinates']),96)
        self.assertTrue(all(c['strict_successes']==0 and c['observable']==0 for c in report['cells']))

    def test_native_request_identity_is_field_not_filename(self):
        import tempfile
        import json
        import results
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'role-audit'
            path.mkdir()
            (path/'storage-id-result.json').write_text(json.dumps({'request_id':'actual-acp-id','depth':1}))
            self.assertTrue(hasattr(results,'role_audits'),'native field-index adapter missing')
            self.assertEqual(results.role_audits(Path(directory))['actual-acp-id']['depth'],1)

    def test_run_dispatches_three_phases_under_one_clock_and_releases_each(self):
        import tempfile
        import os
        import driver as d
        class Clock:
            now=0
            def time(self): return self.now
        clock=Clock()
        starts,stops,commands=[],[],[]
        spec={'policies':{'original':{'name':'original'},'step8':{'name':'step8'}}}
        def start(path,policy,deadline):
            starts.append((path.name,policy['name'],deadline))
            clock.now+=10
            path.mkdir(parents=True)
            return path/'BINDING.json',path/'endpoint.json'
        def phase(name,binding,endpoint,destination,cap):
            self.assertLessEqual(cap,{'originalA':600,'step8':1200,'originalB':600}[name])
            return {'plan':list(range(48 if name=='step8' else 24))}
        def command(argv,log,timeout):
            index=len(commands)
            commands.append((argv,timeout))
            clock.now += [500,1000,500][index]
            output=Path(argv[argv.index('--output')+1])
            d.c.write_once(output/'STATUS.json',{'recorded':[24,48,24][index],'stop_reason':None})
        def stop(path):
            stops.append(path.parent.name)
            clock.now+=5
        with tempfile.TemporaryDirectory() as directory, patch.object(d,'verify_ready',return_value=spec), \
                patch.object(d,'install_observer'),patch.object(d.inherited.lifecycle,'install'), \
                patch.object(d.inherited.lifecycle,'stop_service',side_effect=stop), \
                patch.object(d.inherited.coordinator,'start_service',side_effect=start), \
                patch.object(d.inherited.coordinator,'owned_command',side_effect=command), \
                patch.object(d.e,'phase_spec',side_effect=phase),patch.object(d.time,'time',side_effect=clock.time), \
                patch.object(d.c,'file_hash',return_value='cpu-fixture-hash'),patch.object(d.e.native,'binding_for'), \
                patch.dict(os.environ,{'CUDA_VISIBLE_DEVICES':'CPU_TEST_ONLY','STRICT_RLM_CALIBRATION_API_KEY':'cpu-fixture'}):
            result=d.run(Path(directory)/'run')
            self.assertTrue(result['complete'])
            self.assertEqual(result['collection_elapsed_seconds'],2000)
            self.assertEqual(starts,[('originalA','original',3480),('step8','step8',3480),('originalB','original',3480)])
            self.assertEqual(stops,['originalA','step8','originalB'])
            self.assertEqual(result['deadline_epoch'],3600)


if __name__=='__main__': unittest.main()
