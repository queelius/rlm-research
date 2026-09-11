import ast
import asyncio
import unittest


class StudyTests(unittest.TestCase):
    def test_actual_queue_groups_exact_five_job_blocks(self):
        import experiment as e
        self.assertTrue(hasattr(e,'collector_source'),'five-job collector missing')
        tree=ast.parse(e.collector_source())
        run=next(n for n in tree.body if isinstance(n,ast.AsyncFunctionDef) and n.name=='run')
        loop=next(n for n in run.body if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='offset')
        queue=asyncio.Queue();plan=e.c.read(e.ROOT/'inputs/PLAN.json')
        exec(compile(ast.Module(body=[loop],type_ignores=[]),'actual-five-job-dispatch','exec'),{'plan':plan,'queue':queue})
        chunks=[]
        while not queue.empty():chunks.append(queue.get_nowait())
        self.assertEqual([r for chunk in chunks for r in chunk],plan)
        self.assertTrue(all(len(chunk)==5 and len({r['block'] for r in chunk})==1 for chunk in chunks))

    def test_public_setup_cannot_copy_gold_and_real_timeouts_are_bound(self):
        import experiment as e
        self.assertTrue(hasattr(e,'make_tasks'),'pilot task construction missing')
        task=next(iter(e.make_tasks().values()))
        class Runtime:
            def __init__(self): self.files={}
            async def write(self,path,data):self.files[path]=data
        runtime=Runtime();asyncio.run(task.setup(None,runtime))
        self.assertEqual(set(runtime.files),{'context.txt','records.json','query.txt','batch_contract.py'})
        import json
        self.assertTrue(all(set(r)=={'id','user','text'} for r in json.loads(runtime.files['records.json'])))
        self.assertEqual(e.environment_config()['agent']['timeout'],{'setup':45.,'rollout':300.,'finalize':15.,'scoring':15.})
        operator=Runtime();asyncio.run(e.with_prompt(task,'user_filter').setup(None,operator))
        self.assertEqual(set(operator.files)-set(runtime.files),{'operator_program.py','operator_config.json'})
        for key in runtime.files:self.assertEqual(operator.files[key],runtime.files[key])

    def test_unanswered_is_null_even_when_inherited_raw_score_is_zero(self):
        from pathlib import Path
        self.assertTrue(Path(__file__).with_name('results.py').exists(),'null-aware projection missing')
        import results
        raw={'traces':[{'is_completed':True,'root_reply':'','rewards':{'correctness':{'score':0}},'calls':[],'info':{}}]}
        self.assertIsNone(results.episode_metrics(raw,1)['strict_reward'])
        raw['traces'][0]['root_reply']='wrong shape'
        self.assertEqual(results.episode_metrics(raw,1)['strict_reward'],0)


if __name__=='__main__':unittest.main()
