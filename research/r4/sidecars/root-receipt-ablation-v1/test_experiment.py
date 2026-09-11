import asyncio
import collections
import importlib
import itertools
import unittest


class ExperimentTests(unittest.TestCase):
    def exp(self):
        self.assertIsNotNone(importlib.util.find_spec("experiment"), "triple study missing")
        return importlib.import_module("experiment")

    def test_balanced_triples_and_unchanged_task_and_public_only_files(self):
        e = self.exp()
        tasks = e.make_tasks()
        plan = e.build_plan(tasks)
        self.assertEqual(len(plan), 72)
        self.assertEqual(len({r["seed"] for r in plan}), 24)
        orders = collections.Counter(tuple(r["arm"] for r in plan[i:i+3]) for i in range(0,72,3))
        self.assertEqual(set(orders), set(itertools.permutations(e.ARMS)))
        self.assertEqual(set(orders.values()), {4})
        for i in range(0,72,3):
            self.assertEqual(len({r["matched_id"] for r in plan[i:i+3]}), 1)
            self.assertEqual(len({r["seed"] for r in plan[i:i+3]}), 1)
        class Runtime:
            def __init__(self):
                self.files = {}
            async def write(self, path, value):
                self.files[path] = value
        task = next(iter(tasks.values()))
        for arm in e.ARMS:
            wrapped = e.with_prompt(task, arm)
            self.assertEqual(wrapped.data.answer, task.data.answer)
            self.assertEqual(wrapped.data.context, task.data.context)
            runtime = Runtime()
            asyncio.run(wrapped.setup(None, runtime))
            if arm == "unchanged":
                self.assertEqual(wrapped.data.prompt, e.old.with_prompt(task, "unchanged").data.prompt)
                self.assertEqual(set(runtime.files), {"context.txt"})
            else:
                self.assertEqual(set(runtime.files), {"context.txt", "receipt_api.py", "receipt_catalog.json", "receipt_config.json"})
                self.assertNotIn(b'"answer"', runtime.files["receipt_catalog.json"])
                self.assertNotIn(b'"label"', runtime.files["receipt_catalog.json"])

    def test_collector_actual_queue_builder_dispatches_triples(self):
        e = self.exp()
        # Execute the adapted collector's actual queue-building AST, not a mirrored helper.
        import ast
        tree = ast.parse(e.collector_source())
        run = next(n for n in tree.body if isinstance(n, ast.AsyncFunctionDef) and n.name == "run")
        loop = next(n for n in run.body if isinstance(n, ast.For) and isinstance(n.target, ast.Name) and n.target.id == "offset")
        code = compile(ast.fix_missing_locations(ast.Module(body=[loop], type_ignores=[])), "queue-test", "exec")
        plan = e.build_plan(e.make_tasks())
        queue = asyncio.Queue()
        exec(code, {"plan":plan, "queue":queue})
        chunks = []
        while not queue.empty():
            chunks.append(queue.get_nowait())
        self.assertEqual(len(chunks), 24)
        self.assertTrue(all(len(chunk) == 3 and len({r["matched_id"] for r in chunk}) == 1 for chunk in chunks))
        self.assertEqual([row for chunk in chunks for row in chunk], plan)


if __name__ == "__main__":
    unittest.main()
