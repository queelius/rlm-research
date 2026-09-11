import asyncio
import contextlib
import json
import os
from pathlib import Path
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch


class CollectorTests(unittest.TestCase):
    def test_actual_entry_retains_all32_failed_roots_without_any_acquisition(self):
        import httpx
        import collect as c
        import native as n
        import protocol as p
        import study as s
        import verifiers.v1.envs.single_agent as agent
        worlds=p.worlds(); plan=p.plan(worlds)
        tools=s.read(p.SOURCE/'NATIVE_TOOLS.json')
        inputs={'WORLDS.json':worlds,'PLAN.json':plan,'NATIVE_TOOLS.json':tools,
                'HOST_GOLD.json':{w['id']:p.oracle(w['records'],w['query_products']) for w in worlds}}
        invoked=[]; physical=[]
        def transport(request):
            physical.append(request.method)
            if request.method != 'GET': raise AssertionError('no acquisition POST authorized')
            return httpx.Response(200,json={'data':[{'id':s.MODEL['alias'],'root':s.MODEL['path'],'parent':None}]})
        class Env:
            def __init__(self,config): pass
            @contextlib.asynccontextmanager
            async def serving(self): yield self
            async def run_slot(self,slot,context):
                invoked.append(context.client.headers[n.HEADER])
                raise RuntimeError('authored pre-native failure')
        original_read=s.read; original_client=httpx.AsyncClient
        class OfflineClient(original_client):
            def __init__(self,**kwargs): super().__init__(**kwargs,transport=httpx.MockTransport(transport))
        with tempfile.TemporaryDirectory(prefix='record-externalization-collector-') as directory:
            attempt=Path(directory)/'attempt-001'; endpoint=attempt/'owned-service/service/endpoint-original.json'
            s.write(endpoint,{**s.service.descriptor(s.MODEL,endpoint.parent),'port':1})
            args=SimpleNamespace(endpoint=endpoint,output=attempt/'rollout',deadline=time.time()+90)
            def read(path):
                path=Path(path)
                return inputs[path.name] if path.parent==s.ROOT and path.name in inputs else original_read(path)
            with patch.object(s,'ATTEMPT',attempt),patch.object(s,'verify',lambda:{'identity':'cpu-only'}),\
                 patch.object(s,'read',read),patch.object(agent,'SingleAgentEnv',Env),\
                 patch.object(n,'installed',lambda *a,**k:contextlib.nullcontext()),\
                 patch.object(httpx,'AsyncClient',OfflineClient),\
                 patch.dict(os.environ,{'STRICT_RLM_CALIBRATION_API_KEY':'cpu-fixture'}):
                status=asyncio.run(c.run(args))
            self.assertEqual(status['recorded'],32)
            self.assertEqual(set(invoked),{r['id'] for r in plan})
            self.assertEqual(physical,['GET'])
            rows=[original_read(f) for f in (args.output/'rows').glob('*.json')]
            self.assertTrue(all(r['reward'] is None and not r['available'] for r in rows))
            self.assertEqual(len(original_read(args.output/'PLANNED_NULL_ENDPOINTS.json')),32)
            self.assertEqual(original_read(args.output/'COST_LEDGER.json')['all_new_physical']['calls'],0)

    def test_shared_deadline_flushes_physical_attempts(self):
        import collect as c
        started=[]; flushed=[]
        async def one(row):
            started.append(row)
            try: await asyncio.sleep(10)
            finally: flushed.append(row)
        self.assertFalse(asyncio.run(c.dispatch(list(range(9)),one,time.time()+.05)))
        self.assertEqual(started,[0,1,2,3]); self.assertEqual(set(flushed),set(started))


if __name__=='__main__': unittest.main()
