import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch


class DriverTests(unittest.TestCase):
    def test_collection_failure_releases_only_owned_service_and_no_analysis(self):
        import driver as d
        events=[]
        def start(directory,policy,deadline):
            directory.mkdir(parents=True)
            events.append(("start",directory,deadline))
            return directory/"BINDING.json",directory/"endpoint.json"
        def command(argv,log,cap):
            events.append(("collect",argv,cap))
            raise RuntimeError("retained fixture failure")
        coordinator=types.SimpleNamespace(start_service=start,owned_command=command)
        lifecycle=types.SimpleNamespace(install=lambda:None,stop_service=lambda path:events.append(("stop",path)))
        spec={"policy":{"step":8}}
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/"run"
            with patch.object(d,"verify_ready",return_value=spec), patch.object(d.c,"file_hash",return_value="fixture"), \
                    patch.object(d.inherited,"coordinator",coordinator), patch.object(d.inherited,"lifecycle",lifecycle), \
                    patch.object(d.e,"phase_spec",return_value={}), patch.dict(d.os.environ,{"CUDA_VISIBLE_DEVICES":"fixture-device","STRICT_RLM_CALIBRATION_API_KEY":"fixture"}):
                terminal=d.run(output)
            self.assertFalse(terminal["complete"])
            self.assertEqual(terminal["error"]["message"],"retained fixture failure")
            self.assertEqual([v[0] for v in events],["start","collect","stop"])
            self.assertEqual(events[-1][1],output/"services/step8/service")
            self.assertLessEqual(events[1][2],2130)
            self.assertFalse((output/"ANALYSIS.json").exists())


if __name__=="__main__":
    unittest.main()
