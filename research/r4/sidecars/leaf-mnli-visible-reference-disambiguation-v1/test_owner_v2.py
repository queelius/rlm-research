import importlib.machinery as machinery
import importlib.util as util
import os,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch

import owner_v2 as owner
import service_wrapper_v2 as service_wrapper
import study as s


class OwnerV2Tests(unittest.TestCase):
    def test_owner_observably_uses_1440_allocation_and_exact_48_collector(self):
        observed = {}
        class Runner:
            def start_service(self, stage, binding, deadline):observed["startup"] = deadline
            def command(self, stage, name, argv, timeout, deadline):
                observed.update(name=name, argv=argv, timeout=timeout, deadline=deadline)
                (stage.parent / "rollout").mkdir()
                s.write(stage.parent / "rollout/STATUS.json", {"planned": 48, "recorded": 48})
            def release_service(self, stage):observed["released"] = True
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "attempt-001"
            with (patch.object(s, "ATTEMPT", output), patch.object(owner.module, "credential",
                return_value={"credential_source": "fixture"}), patch.object(owner.module, "suite",
                return_value=Runner()), patch.object(s, "verify", return_value={"identity": "fixture"}),
                patch.dict(os.environ, {"CUDA_VISIBLE_DEVICES": "fixture"})):
                result = owner.execute(output)
            run = s.read(output / "OWNER_RUN.json")
        self.assertTrue(result["complete"])
        self.assertTrue(observed["released"])
        self.assertEqual(result["planned"], 48)
        self.assertEqual(run["outer_seconds"], 1440)
        self.assertAlmostEqual(run["work_deadline_epoch"] - run["started_epoch"], 1320)
        self.assertAlmostEqual(run["owned_deadline_epoch"] - run["started_epoch"], 1410)
        self.assertEqual(observed["argv"][1], str(s.ROOT / "collect_v2.py"))

    def test_full_service_entry_reaches_qualified_launcher(self):
        observed = {}
        class Loader:
            def create_module(self, spec):return None
            def exec_module(self, module):
                module.PRIME_ENV=Path('/fixture/prime');module._port_free=lambda port:True
                module._environment=lambda:{'PATH':'/usr/bin','LD_LIBRARY_PATH':''}
                module._server_environment=lambda environment,replica:dict(environment)
                module._wait_endpoint_model=lambda endpoint,process,alias,timeout:observed.update(alias=alias)
        original=util.spec_from_file_location
        def spec(name,path):return machinery.ModuleSpec(name,Loader()) if name=='base_service_environment' else original(name,path)
        def spawn(command,**kwargs):observed['command']=command;return type('Process',(),{'pid':424242})()
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'attempt-001';stage=output/'owned-service';stage.mkdir(parents=True);s.write(stage/'BINDING.json',owner.binding())
            with patch.object(util,'spec_from_file_location',spec),patch.object(subprocess,'Popen',spawn),patch.dict(os.environ,{'CUDA_VISIBLE_DEVICES':'fixture','STRICT_RLM_CALIBRATION_API_KEY':'fixture'}),patch.object(sys,'argv',[str(s.ROOT/'service_wrapper_v2.py'),'--binding',str(stage/'BINDING.json'),'--run-dir',str(stage/'service')]):
                service_wrapper.main()
        self.assertEqual(observed['alias'],s.MODEL['alias'])
        self.assertEqual(observed['command'][0:2],['/fixture/prime/bin/inference','@'])


if __name__ == "__main__":
    unittest.main()
