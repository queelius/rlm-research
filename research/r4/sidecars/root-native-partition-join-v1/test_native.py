import ast
import asyncio
import importlib.util
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch


class NativeTests(unittest.TestCase):
    def module(self):
        self.assertIsNotNone(importlib.util.find_spec('native'), 'new native implementation absent')
        import native
        return native

    def test_present_absent_evidence_files_and_prompt_are_identical(self):
        n = self.module()
        import protocol as p
        world = p.worlds()[0]; package = p.evidence(world, 'direct', [])
        class MemoryRuntime:
            name = 'authored-memory-fixture'
            def __init__(self): self.files = {}
            async def write(self, name, payload): self.files[name] = payload
            async def read(self, name, **kwargs): return self.files[name]
        outputs = []
        for enabled in (False, True):
            row = dict(id='test-' + str(enabled), python=enabled, seed=1)
            task = n.task(world, package, row); runtime = MemoryRuntime()
            asyncio.run(task.setup(SimpleNamespace(info={}), runtime))
            outputs.append((task.data.prompt, runtime.files, task.runtime_env()))
        self.assertEqual(outputs[0][:2], outputs[1][:2])
        self.assertNotEqual(outputs[0][2]['JOIN_TOOL_PRESENT'], outputs[1][2]['JOIN_TOOL_PRESENT'])
        self.assertFalse(any('gold' in name or 'batch_contract' in name for name in outputs[0][1]))

    def test_disabled_attempt_raises_before_any_tool_execution(self):
        n = self.module()
        source = n.patched_engine()
        tree = ast.parse(source)
        engine = next(x for x in tree.body if isinstance(x, ast.ClassDef) and any(getattr(v, 'name', '') == '_run_loop' for v in x.body))
        fn = next(x for x in engine.body if getattr(x, 'name', '') == '_run_loop')
        logs = []
        class Message:
            content = None
            tool_calls = [SimpleNamespace(id='tool1', function=SimpleNamespace(name='ipython', arguments='{"code":"print(2)"}'))]
            def model_dump(self, **kwargs): return {'role': 'assistant', 'tool_calls': [{'function': {'name': 'ipython'}}]}
        response = SimpleNamespace(choices=[SimpleNamespace(message=Message())])
        async def complete(*args): return response, None
        state = SimpleNamespace(_messages=[], _turn=0, _last_call_id='request', _branch_start_turn=0,
            _metrics=SimpleNamespace(), _join_python=False, _complete=complete,
            session=SimpleNamespace(log_assistant=lambda *a: logs.append('assistant'), write_meta=lambda **kw: logs.append(kw)))
        import itertools
        namespace = dict(RLMResult=object, itertools=itertools, CompactionFailed=type('CompactionFailed', (Exception,), {}),
                         _parse_tool_call_args=lambda x: ({'code': 'print(2)'}, None),
                         get_builtin_tool=lambda *a: self.fail('disabled tool executed'))
        exec(compile(ast.Module(body=[fn], type_ignores=[]), '<audited-native-function>', 'exec'), namespace)
        with self.assertRaisesRegex(RuntimeError, 'JOIN_DISABLED_TOOL_ATTEMPT'):
            asyncio.run(namespace['_run_loop'](state))
        self.assertEqual(logs[0], 'assistant')
        self.assertEqual(logs[1]['join_disabled_tool_attempt']['request_id'], 'request')

    def test_extraction_request_has_final_role_no_tools_and_not_gold(self):
        n = self.module()
        import protocol as p
        world = p.worlds()[0]; row = p.acquisition_plan([world])[0]
        body = n.acquisition_request(world, row)
        self.assertNotIn('tools', body)
        self.assertNotIn('structured_outputs', body)
        self.assertIn('extraction assistant', body['messages'][0]['content'])
        self.assertNotIn(p.serialize(p.oracle(world['records'], world['query_products'])), p.serialize(body))


if __name__ == '__main__': unittest.main()
