import importlib.machinery as machinery
import importlib.util as util
import os,subprocess,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import owner,study as s
import service_wrapper

class OwnerTests(unittest.TestCase):
    def test_actual_owner_collector_composition(self):
        stage=s.ATTEMPT/'owned-service';argv=owner.collector_argv(stage,s.ATTEMPT,123.0);parsed=owner.validate_argv(argv)
        self.assertEqual(parsed['output'],s.ATTEMPT/'rollout');self.assertEqual(parsed['deadline'],123.0)
    def test_wrong_namespace_rejected(self):
        argv=[str(s.NATIVE),str(s.ROOT/'collect.py'),'run','--endpoint',str(s.ATTEMPT/'owned-service/service/endpoint-original.json'),'--output',str(Path('/tmp/wrong')),'--deadline','1']
        with self.assertRaises(ValueError):owner.validate_argv(argv)
    def test_inherited_service_wrapper_binds_pinned_mnli_study(self):
        wrapper=service_wrapper.qualified_wrapper();self.assertIs(wrapper.s,s.base)
    def test_full_service_entry_reaches_pinned_launcher_before_popen(self):
        observed={}
        class Loader:
            def create_module(self,spec):return None
            def exec_module(self,module):
                module.PRIME_ENV=Path('/fixture/prime');module._port_free=lambda port:True
                module._environment=lambda:{'PATH':'/usr/bin','LD_LIBRARY_PATH':''}
                module._server_environment=lambda environment,replica:dict(environment)
                module._wait_endpoint_model=lambda endpoint,process,alias,timeout:observed.update(alias=alias)
        original_spec=util.spec_from_file_location
        def spec(name,path):return machinery.ModuleSpec(name,Loader()) if name=='base_service_environment' else original_spec(name,path)
        def spawn(command,**kwargs):observed['command']=command;return type('Process',(),{'pid':424242})()
        with tempfile.TemporaryDirectory(prefix='mnli-exact-tag-service-') as directory:
            output=Path(directory)/'attempt-001';binding=owner.binding()
            def start(stage,actual,deadline):
                self.assertEqual(actual,binding);s.write(stage/'BINDING.json',actual)
                with patch.object(sys,'argv',[str(s.ROOT/'service_wrapper.py'),'--binding',str(stage/'BINDING.json'),'--run-dir',str(stage/'service')]):service_wrapper.main()
            def command(stage,name,argv,timeout,deadline):
                parsed=owner.validate_argv(argv);observed['collector_argv']=argv;s.write(parsed['output']/'STATUS.json',dict(planned=32,recorded=32))
            runner=SimpleNamespace(start_service=start,command=command,release_service=lambda stage:None)
            with patch.object(util,'spec_from_file_location',spec),patch.object(subprocess,'Popen',spawn),\
                 patch.dict(os.environ,{'CUDA_VISIBLE_DEVICES':'fixture-only','STRICT_RLM_CALIBRATION_API_KEY':'fixture-not-secret'}),\
                 patch.object(s,'ATTEMPT',output),patch.object(s,'verify',lambda:{'identity':'cpu'}),\
                 patch.object(owner,'credential',lambda:{}),patch.object(owner,'suite',lambda:runner):
                original_sha=s.sha
                with patch.object(s,'sha',lambda path:'cpu-ready' if Path(path)==s.READY_PATH else original_sha(path)):
                    result=owner.execute(output)
            self.assertTrue(result['complete']);self.assertEqual(observed['alias'],s.MODEL['alias'])
            self.assertEqual(observed['command'],['/fixture/prime/bin/inference','@',str(output/'owned-service/service/inference.json')])
            self.assertEqual(observed['collector_argv'][1],str(s.ROOT/'collect.py'))

if __name__=='__main__':unittest.main()
