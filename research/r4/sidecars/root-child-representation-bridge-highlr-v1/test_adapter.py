"""Actual thin-entrypoint and trusted role routing, no model or service startup."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest
ROOT=Path(__file__).parent
class AdapterTests(unittest.TestCase):
    def test_only_root_checkpoint_binding_changes_and_coordinates_are_exact(self):
        self.assertTrue((ROOT/'study.py').exists(),'checkpoint-only adapter missing')
        import study as s
        a=s.old.binding();b=s.binding();alias=a['role_map']['root']
        self.assertEqual({k:v for k,v in a.items() if k!='models'},{k:v for k,v in b.items() if k!='models'})
        self.assertEqual({k:v for k,v in a['models'].items() if k!=alias},{k:v for k,v in b['models'].items() if k!=alias})
        self.assertEqual(b['models'][alias]['adapter_sha256'],'0ba42364183a311a8f5b67e4bac4e9294924c1dfb73f152a209811df09b78773')
        self.assertEqual(s.old.plan_for(s.old.inputs()[0]),s.read(s.OLD/'SPEC.json')['plan'])
    def test_actual_executable_imports_and_native_root_child_route(self):
        self.assertTrue((ROOT/'study.py').exists(),'entrypoint adapter missing')
        import study as s
        for filename in ('driver.py','collect.py'):
            result=subprocess.run([sys.executable,str(ROOT/filename),'--help'],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
        role=s.load('highlr_actual_native_route',s.SIDE/'leaf-role-routing-v1/source/routing.py','8575081694a6ceea8d5f4058d4f625eb81d34f617a680f94bc06968e3a3ca78f')
        binding=s.binding();headers={'x-rlm-role-invocation':'cpu-native-invocation','x-rlm-role-request-id':'a'*32,'x-rlm-role-kind':'ordinary'}
        for depth in (0,1):
            body={'model':binding['role_map']['root'],'messages':[{'role':'user','content':'same source-bound public request'}]}
            result=role.route(body,{**headers,'x-rlm-role-depth':str(depth)},binding['fixed_child'],binding['role_map'])
            alias=binding['role_map']['root'] if depth==0 else binding['fixed_child']
            self.assertEqual(result['actual_alias'],alias)
            self.assertEqual(binding['models'][alias]['adapter_sha256'],s.NEW_SHA if depth==0 else s.old.CHILD_SHA)
            self.assertEqual(body['messages'],[{'role':'user','content':'same source-bound public request'}])

if __name__=='__main__':unittest.main()
