import importlib.util
import unittest


class CollectorTests(unittest.TestCase):
    def test_four_workers_flush_cancelled_attempts_at_shared_deadline(self):
        c = self.module()
        import asyncio
        import time
        started, flushed = [], []
        async def one(row):
            started.append(row)
            try: await asyncio.sleep(10)
            finally: flushed.append(row)
        complete = asyncio.run(c.dispatch(list(range(9)), one, time.time()+.05))
        self.assertFalse(complete)
        self.assertEqual(started, [0, 1, 2, 3])
        self.assertEqual(set(flushed), set(started))
    def test_nonjson_failed_response_retains_attempt_with_unknown_usage(self):
        c = self.module()
        self.assertTrue(hasattr(c, 'attempt_usage'), 'failure-safe usage accounting absent')
        value = c.attempt_usage([{'native_wire_response': {'body': 'upstream error'}}])
        self.assertEqual(value['calls'], 1)
        self.assertEqual(value['known']['output'], 0)
        self.assertEqual(value['unknown']['output'], 1)

    def test_actual_collector_preserves_failed_source_slots_and_executes_direct(self):
        c = self.module()
        import asyncio
        import contextlib
        import httpx
        import json
        import os
        from pathlib import Path
        import tempfile
        from types import SimpleNamespace
        from unittest.mock import patch
        import native as n
        import protocol as p
        import study as s
        import verifiers.v1.envs.single_agent as agent
        worlds = p.worlds(); plan = p.plan(worlds); acq = p.acquisition_plan(worlds)
        tools = next(s.read(path)['native_tools_ordered_json'] for path in (s.ROOT / 'qualification-004/role-audit').glob('*-result.json')
                     if s.read(path)['coordinate']['python'])
        inputs = {'WORLDS.json': worlds, 'PLAN.json': plan, 'ACQUISITION_PLAN.json': acq,
                  'HOST_GOLD.json': {w['id']: p.oracle(w['records'], w['query_products']) for w in worlds},
                  'NATIVE_TOOLS.json': {'ordered_json': tools}}
        tokenizer = s.tokenizer(); invoked = []; acquisition_count = []
        def transport(request):
            if request.method == 'GET':
                return httpx.Response(200, json={'data': [{'id': s.MODEL['alias'], 'root': s.MODEL['path'], 'parent': None}]})
            body = json.loads(request.content); row = next(r for r in acq if r['seed'] == body['seed'])
            acquisition_count.append(row['id'])
            raw = 'not-json' if row == acq[0] else p.serialize(row['records'])
            incoming = tokenizer.apply_chat_template(body['messages'], tokenize=True, add_generation_prompt=True, enable_thinking=False, return_dict=False)
            outgoing = tokenizer.encode(raw, add_special_tokens=False) + [151645]
            return httpx.Response(200, json={'model': s.MODEL['alias'], 'prompt_token_ids': incoming,
                'choices': [{'message': {'role': 'assistant', 'content': raw}, 'finish_reason': 'stop', 'token_ids': outgoing}],
                'usage': {'prompt_tokens': len(incoming), 'completion_tokens': len(outgoing)}})
        class Env:
            def __init__(self, config): pass
            @contextlib.asynccontextmanager
            async def serving(self): yield self
            async def run_slot(self, slot, context):
                invoked.append(context.client.headers[n.HEADER])
                raise RuntimeError('authored fixture stops before native process; native process separately qualified')
        original_read = s.read; original_client = httpx.AsyncClient
        class OfflineClient(original_client):
            def __init__(self, **kwargs): super().__init__(**kwargs, transport=httpx.MockTransport(transport))
        with tempfile.TemporaryDirectory(prefix='join-collector-test-') as directory:
            root = Path(directory); attempt = root / 'attempt-001'; endpoint = attempt / 'owned-service/service/endpoint-original.json'
            s.write(endpoint, {**s.service.descriptor(s.MODEL, endpoint.parent), 'port': 1})
            args = SimpleNamespace(endpoint=endpoint, output=attempt / 'rollout', deadline=__import__('time').time()+90)
            def read(path):
                path = Path(path)
                return inputs[path.name] if path.parent == s.ROOT and path.name in inputs else original_read(path)
            with patch.object(s, 'ATTEMPT', attempt), patch.object(s, 'verify', lambda: {'identity': 'cpu-fixture'}), \
                 patch.object(s, 'read', read), patch.object(agent, 'SingleAgentEnv', Env), \
                 patch.object(n, 'installed', lambda *a, **k: contextlib.nullcontext()), \
                 patch.object(httpx, 'AsyncClient', OfflineClient), \
                 patch.dict(os.environ, {'STRICT_RLM_CALIBRATION_API_KEY': 'cpu-fixture'}):
                status = asyncio.run(c.run(args))
            self.assertEqual(status['recorded'], 48)
            rows = [original_read(path) for path in (args.output / 'rows').glob('*.json')]
            self.assertEqual(sum(r['cause'] == 'source_extraction_gate' for r in rows), 4)
            self.assertEqual(len(invoked), 44)
            self.assertEqual(len(acquisition_count), 24)
            direct = {r['id'] for r in plan if r['representation'] == 'direct'}
            self.assertTrue(direct <= set(invoked))
            self.assertTrue(all(r['reward'] is None and r['operational_success'] == 0 for r in rows))
            ledger = original_read(args.output / 'COST_LEDGER.json')
            self.assertEqual(ledger['all_new_physical']['calls'], 24)
            self.assertEqual(ledger['new_physical_root_pipelines']['calls'], 0)
            self.assertEqual(ledger['planned_hypothetical_acquisition_charges'], 96)

    def test_authentic_unadvertised_tool_is_policy_failure_not_infrastructure(self):
        c = self.module()
        self.assertTrue(hasattr(c, 'policy_failure_metadata'), 'explicit policy failure metadata absent')
        record = {'request_id': 'actual', 'status': 'returned', 'depth': 0,
                  'native_request': {'messages': [], 'model': 'bound'}, 'native_wire_request': {'body': {'token_ids': [1]}},
                  'native_response': {'message': {'tool_calls': [{'name': 'ipython'}]}}}
        value = c.policy_failure_metadata({'python': False}, [record])
        self.assertTrue(value['observed_unadvertised_tool_attempt'])
        self.assertEqual(value['failure_class'], 'policy_failure')
        self.assertEqual(value['unadvertised_tool_request_ids'], ['actual'])
        self.assertFalse(c.policy_failure_metadata({'python': True}, [record])['observed_unadvertised_tool_attempt'])
        record['status'] = 'error'; record.pop('native_response')
        self.assertFalse(c.policy_failure_metadata({'python': False}, [record])['observed_unadvertised_tool_attempt'])

    def test_actual_native_unadvertised_fixture_preserves_null_and_policy_cause(self):
        c = self.module()
        import study as s
        records = [s.read(path) for path in (s.ROOT / 'qualification-005/role-audit').glob('*-result.json')]
        actual = [r for r in records if r['coordinate']['id'] == 'cpu-unadvertised']
        self.assertEqual(len(actual), 1)
        self.assertTrue(c.policy_failure_metadata({'python': False}, actual)['observed_unadvertised_tool_attempt'])
        trace = s.read(s.ROOT / 'qualification-005/cpu-unadvertised.json')['traces'][0]
        score = c.terminal_score(trace, actual[0], [], [])
        self.assertFalse(score['available']); self.assertIsNone(score['reward'])
        self.assertEqual(score['operational_success'], 0)

    def module(self):
        self.assertIsNotNone(importlib.util.find_spec('collect'), 'new collector absent')
        import collect
        return collect

    def test_terminal_requires_matching_authentic_native_final_not_printed_output(self):
        c = self.module()
        trace = {'root_reply': '["c1"]'}
        capture = {'status': 'returned', 'native_response': {'finish_reason': 'stop',
                    'message': {'content': '["c1"]', 'tool_calls': None}}}
        self.assertEqual(c.terminal_score(trace, capture, ['c1'], ['c1'])['reward'], 1)
        capture['native_response']['message']['tool_calls'] = [{'name': 'ipython'}]
        self.assertIsNone(c.terminal_score(trace, capture, ['c1'], ['c1'])['reward'])
        capture['native_response']['message']['tool_calls'] = None
        capture['native_response']['message']['content'] = 'print(["c1"])'
        self.assertIsNone(c.terminal_score(trace, capture, ['c1'], ['c1'])['reward'])

    def test_complete_malformed_length_is_wrong_but_unrun_is_null(self):
        c = self.module()
        capture = {'status': 'returned', 'native_response': {'finish_reason': 'length', 'message': {'content': '['}}}
        self.assertEqual(c.terminal_score({'root_reply': '['}, capture, [], ['c1'])['reward'], 0)
        self.assertIsNone(c.terminal_score({}, None, [], ['c1'])['reward'])


if __name__ == '__main__': unittest.main()
