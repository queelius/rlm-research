import asyncio
import contextlib
import os
from pathlib import Path
import tempfile
import time
import types
import unittest
from unittest.mock import patch
import httpx
import transfer_study as s
import collect

class CollectorTests(unittest.TestCase):
    def test_real_collector_continues_all16_failed_native_slots_without_retry(self):
        from verifiers.v1.envs.single_agent import SingleAgentEnvConfig
        binding={'fixed_child':'child','role_map':{'root':'root'},'models':{'child':{'path':'/fixture/child'},'root':{'path':'/fixture/root'}}}
        def response(request):
            self.assertEqual((request.method,request.url.path),('GET','/v1/models'))
            return httpx.Response(200,json={'data':[dict(id='child',root='/fixture/child'),dict(id='root',root='/fixture/root')]})
        base=httpx.AsyncClient
        class Client(base):
            def __init__(self,*a,**k):super().__init__(*a,**k,transport=httpx.MockTransport(response))
        class Environment:
            def __init__(self,config):pass
            @contextlib.asynccontextmanager
            async def serving(self):yield self
        calls=[]
        async def failed(row,context,binding,descriptor,target,deadline,mode,shared=None,installed=None):
            self.assertEqual(mode,'free');self.assertIsNone(shared);calls.append(row['id']);target.mkdir();s.write(target/'FAILURE.json',dict(type='AuthoredNativeBoundaryFailure'));raise ValueError('authored native boundary failure')
        interface=types.SimpleNamespace(installed=lambda *a,**k:contextlib.nullcontext(),e=types.SimpleNamespace(environment_config=lambda:{}))
        with tempfile.TemporaryDirectory(prefix='transfer-collector-cpu-') as directory,patch.dict(os.environ,{'CPU_FIXTURE_KEY':'not-secret'}):
            root=Path(directory);s.write(root/'binding.json',binding);s.write(root/'endpoint.json',dict(host='127.0.0.1',port=1,api_key_env='CPU_FIXTURE_KEY'))
            args=collect.parse_args(['--mode','free','--plan','FREE_PLAN.json','--stop','16','--binding',str(root/'binding.json'),'--endpoint',str(root/'endpoint.json'),'--output',str(root/'results'),'--deadline',str(time.time()+30)])
            with patch.object(s,'verify',return_value={}),patch.object(s,'runtime',return_value=None),patch.object(s,'interface',return_value=interface),patch.object(collect.b,'validate',return_value=None),patch.object(httpx,'AsyncClient',Client),patch.object(collect.original,'episode',failed),patch('verifiers.v1.envs.single_agent.SingleAgentEnv',Environment),patch.object(SingleAgentEnvConfig,'model_validate',return_value=None):asyncio.run(collect.run(args))
            terminal=s.read(root/'results/TERMINAL.json');self.assertEqual((terminal['planned'],terminal['recorded'],terminal['available']),(16,16,0));self.assertEqual(len(calls),16);self.assertEqual(len(set(calls)),16);self.assertTrue(all(r['reward'] is None for r in terminal['results']))
            self.assertEqual(s.read(root/'results/ATTEMPT_COST_LEDGER.json')['physical_request_attempts'],0)

if __name__=='__main__':unittest.main()
