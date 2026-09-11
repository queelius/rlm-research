import importlib.machinery as machinery
import importlib.util as util
import os,subprocess,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import owner,study as s,service_wrapper

class OwnerTests(unittest.TestCase):
    def test_exact_owner_to_collector_namespace(self):
        stage=s.ATTEMPT/'owned-service';argv=owner.collector_argv(stage,s.ATTEMPT,123.)
        parsed=owner.validate_argv(argv)
        self.assertEqual(parsed['output'],s.ATTEMPT/'rollout')
        self.assertEqual(argv[1],str(s.ROOT/'collect.py'))
        self.assertEqual(parsed['deadline'],123.)
    def test_qualified_service_wrapper_reaches_released_base(self):
        outer=service_wrapper.qualified_wrapper()
        inner=outer.qualified_wrapper()
        self.assertIs(outer.s,s)
        self.assertIs(inner.s,s.base)
    def test_full_service_entry_reaches_launcher_and_exact_collector(self):
        observed={}
        class Loader:
            def create_module(self,spec):return None
            def exec_module(self,module):
                module.PRIME_ENV=Path('/fixture/prime');module._port_free=lambda port:True
                module._environment=lambda:{'PATH':'/usr/bin','LD_LIBRARY_PATH':''}
                module._server_environment=lambda environment,replica:dict(environment)
                module._wait_endpoint_model=lambda endpoint,process,alias,timeout:observed.update(alias=alias)
        original=util.spec_from_file_location
        def spec(name,path):return machinery.ModuleSpec(name,Loader()) if name=='base_service_environment' else original(name,path)
        def spawn(command,**kwargs):observed['command']=command;return type('Process',(),{'pid':424242})()
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'attempt-001';stage=output/'owned-service';stage.mkdir(parents=True);s.write(stage/'BINDING.json',owner.binding())
            with patch.object(util,'spec_from_file_location',spec),patch.object(subprocess,'Popen',spawn),patch.dict(os.environ,{'CUDA_VISIBLE_DEVICES':'fixture','STRICT_RLM_CALIBRATION_API_KEY':'fixture'}),patch.object(sys,'argv',[str(s.ROOT/'service_wrapper.py'),'--binding',str(stage/'BINDING.json'),'--run-dir',str(stage/'service')]):
                service_wrapper.main()
            with patch.object(s,'ATTEMPT',output):
                observed['collector']=owner.collector_argv(stage,output,123.)
                parsed=owner.validate_argv(observed['collector'])
        self.assertEqual(observed['alias'],s.MODEL['alias'])
        self.assertEqual(parsed['output'],output/'rollout')
        self.assertEqual(observed['collector'][1],str(s.ROOT/'collect.py'))
        self.assertEqual(observed['command'][0:2],['/fixture/prime/bin/inference','@'])

if __name__=='__main__':unittest.main()
