import importlib.util
import os
from pathlib import Path
import runpy
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
import transfer_study as s
import owner

class LifecycleTests(unittest.TestCase):
    def test_main_termination_releases_then_stops_without_next_policy(self):
        import signal
        started=[];released=[]
        def command(*args):signal.getsignal(signal.SIGTERM)(signal.SIGTERM,None)
        suite=types.SimpleNamespace(start_service=lambda p,*a:started.append(p),release_service=lambda p:released.append(p),command=command)
        real_sha=s.sha
        with tempfile.TemporaryDirectory(prefix='transfer-stop-cpu-') as directory,patch.dict(os.environ,{'CUDA_VISIBLE_DEVICES':'CPU_FIXTURE'}):
            output=Path(directory)/'attempt'
            with patch.object(s,'ATTEMPT',output),patch.object(s,'runtime',return_value=None),patch.object(s,'verify',return_value={'identity':'cpu'}),patch.object(s,'sha',side_effect=lambda p:'0'*64 if p==s.ROOT/'READY.json' else real_sha(p)),patch.object(owner,'dependencies',return_value=suite),patch.object(owner.b,'selected',return_value={}),patch.object(owner.b,'binding',return_value={}):
                result=owner.execute(output)
            self.assertFalse(result['complete']);self.assertEqual(len(started),1);self.assertEqual(started,released)
            self.assertIsNotNone(result['error'])

    def test_real_owner_service_wrapper_config_descriptor_before_intercepted_launch(self):
        class InterceptedLaunch(BaseException):pass
        spawned=[];real_sha=s.sha;spec_loader=importlib.util.spec_from_file_location
        def instrumented_spec(name,path,*args,**kwargs):
            spec=spec_loader(name,path,*args,**kwargs)
            if name=='dual_lora_owned_launcher':
                execute=spec.loader.exec_module
                def load_helper(module):
                    execute(module);module._port_free=lambda port:True;module._wait_endpoint_model=lambda *a,**k:None;module._load_adapter=lambda d:None;module._stop=lambda p:None
                spec.loader.exec_module=load_helper
            return spec
        with tempfile.TemporaryDirectory(prefix='transfer-owner-cpu-') as directory,patch.dict(os.environ,{'CUDA_VISIBLE_DEVICES':'CPU_INTERCEPT_ONLY','STRICT_RLM_CALIBRATION_API_KEY':'cpu-fixture-not-a-credential'}),patch.object(s,'sha',side_effect=lambda p:'0'*64 if Path(p)==s.ROOT/'READY.json' else real_sha(p)):
            output=Path(directory)/'attempt';arm=s.phases()[0];stage=output/('service-'+arm);suite=owner.dependencies()
            def popen(argv,**kwargs):
                spawned.append(argv)
                if len(spawned)==1:
                    rows=s.read(output/'PLANNED_NULL_ENDPOINTS.json');self.assertEqual(len(rows),48);self.assertTrue(all(x['reward'] is None for x in rows))
                    self.assertEqual(Path(argv[1]),s.RUNTIME/'service_wrapper_v2.py');previous=list(sys.path)
                    try:
                        with patch.object(sys,'argv',argv[1:]),patch('importlib.util.spec_from_file_location',side_effect=instrumented_spec):runpy.run_path(argv[1],run_name='__main__')
                    finally:sys.path[:]=previous
                    raise InterceptedLaunch()
                self.assertEqual(Path(argv[0]).name,'inference');self.assertEqual(argv[1],'@')
                config=s.read(argv[2]);self.assertEqual(config['vllm']['max_model_len'],8192);self.assertEqual(config['vllm']['max_loras'],2)
                self.assertNotIn('580.126.09',kwargs['env']['LD_LIBRARY_PATH'])
                return types.SimpleNamespace(pid=999999,returncode=0,poll=lambda:0)
            releases=[]
            with patch.object(s,'ATTEMPT',output),patch.object(s,'verify',return_value={'identity':'cpu-fixture'}),patch.object(suite.life.v1,'ports_free',return_value=True),patch.object(suite.subprocess,'Popen',side_effect=popen),patch.object(suite,'release_service',side_effect=lambda p:releases.append(p)):
                result=owner.execute(output)
            self.assertFalse(result['complete']);self.assertEqual(result['error']['type'],'InterceptedLaunch');self.assertEqual(releases,[stage]);self.assertIsNone(result['active_unreleased_service']);self.assertEqual(len(spawned),2)
            binding=s.read(stage/'BINDING.json');endpoint=s.read(stage/'service/endpoint-original.json')
            owner.b.validate(binding,endpoint,stage/'BINDING.json')
            self.assertEqual(endpoint['adapter']['model_sha256'],owner.b.EXPECTED[arm])
            self.assertEqual(s.read(stage/'service/SERVER_START.json')['launcher_sha256'],real_sha(s.RUNTIME/'service_wrapper_v2.py'))
            self.assertEqual(result['planned'],48);self.assertEqual(s.read(output/'COST_LEDGER.json')['physical_request_attempts'],0)

if __name__=='__main__':unittest.main()
