import os,subprocess,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import owner,study as s,service_wrapper

class OwnerTests(unittest.TestCase):
    def test_qualified_service_wrapper_is_executable(self):
        wrapper=service_wrapper.qualified_wrapper();self.assertIsNotNone(wrapper);self.assertIs(wrapper.s,s.base)
    def test_exact_owner_to_collector_entry(self):
        stage=s.ATTEMPT/'owned-service';argv=owner.collector_argv(stage,s.ATTEMPT,123.)
        parsed=owner.validate_argv(argv);self.assertEqual(parsed['output'],s.ATTEMPT/'rollout');self.assertEqual(parsed['deadline'],123.)
        self.assertIn('alien-tag48',owner.COLLECT_LABEL)
    def test_actual_owner_runs_exact_48_slot_collector_command(self):
        observed=[]
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'attempt-001'
            runner=SimpleNamespace(start_service=lambda *a:None,release_service=lambda *a:None,
                command=lambda stage,label,argv,timeout,deadline:(observed.append((label,argv)),s.write(out/'rollout/STATUS.json',{'planned':48,'recorded':48})))
            with patch.object(s,'ATTEMPT',out),patch.object(s,'verify',lambda:{'identity':'cpu'}),patch.object(owner.module,'credential',lambda:{}),patch.object(owner.module,'suite',lambda:runner),patch.dict(os.environ,{'CUDA_VISIBLE_DEVICES':'MIG-cpu'}):
                result=owner.execute(out)
        self.assertTrue(result['complete']);self.assertEqual(result['planned'],48);self.assertEqual(observed[0][1][1],str(s.ROOT/'collect.py'))
if __name__=='__main__':unittest.main()
