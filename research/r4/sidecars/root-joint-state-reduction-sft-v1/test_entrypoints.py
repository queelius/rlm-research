import importlib
from pathlib import Path
import tempfile
import unittest
import os
import sys
import time
import runpy
import types
from unittest.mock import patch
import joint_study as s

class EntryTests(unittest.TestCase):
    def modules(self):
        self.assertTrue((Path(__file__).parent/'owner.py').exists(),'composed owner not implemented')
        self.assertTrue((Path(__file__).parent/'collect.py').exists(),'collector not implemented')
        return importlib.import_module('owner'),importlib.import_module('collect')
    def test_owner_cli_namespace_matches_real_collector(self):
        owner,collector=self.modules();stage=Path('/tmp/no-launch');destination=Path('/tmp/no-output')
        for mode,plan,stop in (('capture','TRAIN_PLAN.json',16),('controlled','DIAGNOSTIC_PLAN.json',4),('free','FREE_PLAN.json',16)):
            argv=owner.collector_argv(stage,destination,1234.,mode,plan,0,stop)
            parsed=collector.parse_args(argv[2:])
            self.assertEqual((parsed.mode,parsed.plan,parsed.stop),(mode,plan,stop))
            self.assertEqual(parsed.binding,stage/'BINDING.json');self.assertEqual(parsed.endpoint,stage/'service/endpoint-original.json')
            self.assertEqual(parsed.output,destination)
    def test_missing_slots_are_null_but_returned_malformed_final_is_zero(self):
        owner,collector=self.modules()
        rows=collector.planned_results([dict(id='a'),dict(id='b')],{'a':dict(coordinate=dict(id='a'),available=True,reward=0)})
        self.assertEqual(rows[0]['reward'],0);self.assertIsNone(rows[1]['reward'])
        actual=dict(status='returned',native_response=dict(finish_reason='stop',message=dict(content='maybe 2',tool_calls=[])))
        self.assertEqual(collector.metrics.score(dict(root_reply='maybe 2'),actual,2)['reward'],0)
        self.assertIsNone(collector.metrics.score(dict(root_reply='Answer: 2'),actual,2)['reward'])
    def test_wrong_output_stops_before_any_output_creation(self):
        owner,_=self.modules()
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'wrong'
            with self.assertRaises(ValueError):owner.check_output(path)
            self.assertFalse(path.exists())

    def test_real_owner_service_wrapper_config_descriptor_and_intercepted_popen(self):
        owner,_=self.modules();original_sha=s.sha;spec_loader=importlib.util.spec_from_file_location
        class InterceptedLaunch(Exception):pass
        spawned=[]
        def instrumented_spec(name,path,*args,**kwargs):
            spec=spec_loader(name,path,*args,**kwargs)
            if name=='dual_lora_owned_launcher':
                execute=spec.loader.exec_module
                def load_helper(module):
                    execute(module)
                    module._port_free=lambda port:True
                    module._wait_endpoint_model=lambda *a,**k:None
                    module._load_adapter=lambda descriptor:None
                    module._stop=lambda process:None
                spec.loader.exec_module=load_helper
            return spec
        with tempfile.TemporaryDirectory() as d,patch.dict(os.environ,{'CUDA_VISIBLE_DEVICES':'CPU_INTERCEPT_ONLY','STRICT_RLM_CALIBRATION_API_KEY':'cpu-fixture-not-a-credential'}),patch.object(s,'sha',side_effect=lambda path:'0'*64 if Path(path)==s.ROOT/'READY.json' else original_sha(path)):
            output=Path(d)/'attempt';stage=output/'teacher-service';suite=owner.dependencies();bound=owner.b.binding('unchanged',owner.b.selected('unchanged'))
            def intercepted_popen(argv,**kwargs):
                spawned.append(argv)
                if len(spawned)==1:
                    planned=s.read(output/'PLANNED_NULL_ENDPOINTS.json')
                    self.assertEqual(len(planned),84);self.assertTrue(all(r['reward'] is None for r in planned))
                    self.assertEqual(Path(argv[1]),s.RUNTIME/'service_wrapper_v2.py')
                    self.assertEqual(Path(argv[0]),s.NATIVE)
                    previous_path=list(sys.path)
                    try:
                        with patch.object(sys,'argv',argv[1:]),patch('importlib.util.spec_from_file_location',side_effect=instrumented_spec):runpy.run_path(argv[1],run_name='__main__')
                    finally:sys.path[:]=previous_path
                    raise InterceptedLaunch()
                self.assertEqual(Path(argv[0]).name,'inference')
                self.assertEqual(argv[1],'@')
                config=s.read(Path(argv[2]));self.assertEqual(config['vllm']['max_model_len'],8192);self.assertEqual(config['vllm']['max_loras'],2)
                self.assertNotIn('580.126.09',kwargs['env']['LD_LIBRARY_PATH'])
                return types.SimpleNamespace(pid=999999,returncode=0,poll=lambda:0)
            released=[]
            with patch.object(s,'ATTEMPT',output),patch.object(s,'verify',return_value={'identity':'cpu-fixture'}),patch.object(suite.life.v1,'ports_free',return_value=True),patch.object(suite.subprocess,'Popen',side_effect=intercepted_popen),patch.object(suite,'release_service',side_effect=lambda path:released.append(path)):
                result=owner.execute(output)
            self.assertEqual(result['error']['type'],'InterceptedLaunch')
            self.assertEqual(released,[stage]);self.assertIsNone(result['active_unreleased_service'])
            self.assertFalse(result['complete']);self.assertEqual(len(result['readout_inventory']),84)
            self.assertEqual(len(spawned),2)
            endpoint=s.read(stage/'service/endpoint-original.json')
            owner.b.validate(bound,endpoint,stage/'BINDING.json')
            self.assertEqual(endpoint['adapter']['model_sha256'],s.START_SHA)
            self.assertEqual(s.read(stage/'service/SERVER_START.json')['launcher_sha256'],original_sha(s.RUNTIME/'service_wrapper_v2.py'))
            self.assertEqual(s.read(stage/'SERVICE_REQUEST.json')['command'],spawned[0])

    def test_all84_rows_exist_as_planned_nulls_before_any_service(self):
        owner,_=self.modules();rows=owner.planned_inventory(Path('/tmp/no-launch'))
        self.assertEqual(len(rows),84)
        self.assertEqual(sum(r['mode']=='training_diagnostic' for r in rows),12)
        self.assertTrue(all(r['reward'] is None and not r['available'] for r in rows))

if __name__=='__main__':unittest.main()
