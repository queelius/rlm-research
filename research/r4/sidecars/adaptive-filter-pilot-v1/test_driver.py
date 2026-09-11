import importlib.util
import unittest
from pathlib import Path


class DriverTests(unittest.TestCase):
    def test_remaining_time_never_resets_or_exceeds_collection_cap(self):
        self.assertTrue(Path(__file__).with_name('driver.py').exists(),'owned driver missing')
        import driver
        self.assertEqual(driver.collection_deadline(0,180),2460)
        self.assertEqual(driver.collection_deadline(0,300),2460)
        self.assertEqual(driver.collection_deadline(0,0),2280)
        self.assertLessEqual(driver.collection_deadline(0,2500)-2500,0)

    def test_actual_wrapper_dispatches_one_service_and_preserves_absolute_cap(self):
        import driver as d
        import tempfile
        import os
        from unittest.mock import patch
        starts,stops,commands=[],[],[]
        clock=[0.]
        spec={'policy':{'name':'historical8'},'binding':{},'source_file_sha256':{}}
        def start(path,policy,deadline):
            starts.append((policy,deadline));clock[0]+=100
            return path/'BINDING.json',path/'endpoint.json'
        def read(path):
            if str(path).endswith('endpoint.json'):return {'host':'127.0.0.1','port':1234,'api_key_env':'TEST'}
            return {'recorded':40,'stop_reason':None}
        def command(argv,log,timeout):commands.append((argv,timeout));clock[0]+=1000
        with tempfile.TemporaryDirectory(prefix='adaptive-driver-test-') as directory, \
             patch.object(d,'verify_ready',return_value=spec),patch.object(d.upstream,'install_observer'), \
             patch.object(d.life,'install'),patch.object(d.life,'stop_service',side_effect=lambda p:stops.append(str(p))), \
             patch.object(d.coordinator,'start_service',side_effect=start),patch.object(d.coordinator,'owned_command',side_effect=command), \
             patch.object(d.c,'read',side_effect=read),patch.object(d.c,'file_hash',return_value='fixture'), \
             patch.object(d.e.old,'planned_endpoint',return_value={}),patch.object(d.e.capture.recursive,'serving_evidence',return_value={}), \
             patch.object(d.time,'time',side_effect=lambda:clock[0]),patch.object(d.e.native,'binding_for'), \
             patch.dict(os.environ,{'CUDA_VISIBLE_DEVICES':'CPU_FIXTURE','STRICT_RLM_CALIBRATION_API_KEY':'fixture'}):
            result=d.run(Path(directory)/'run')
        self.assertTrue(result['complete']);self.assertEqual(starts,[({'name':'historical8'},180.)])
        self.assertEqual(len(stops),1);self.assertEqual(len(commands),1)
        self.assertEqual(result['deadline_epoch'],2700.)
        self.assertEqual(result['work_deadline_epoch'],2580.)
        self.assertLessEqual(commands[0][1],2280+30)


if __name__=='__main__':unittest.main()
