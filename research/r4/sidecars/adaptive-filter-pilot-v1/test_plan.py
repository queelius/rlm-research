import importlib.util
import unittest
from pathlib import Path


class PlanTests(unittest.TestCase):
    def test_global_shared_rows_execute_once_and_user_methods_stay_distinct(self):
        path=Path(__file__).with_name('prepare.py')
        self.assertTrue(path.exists(),'exact40/48 planner missing')
        spec=importlib.util.spec_from_file_location('adaptive_test_prepare',path)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        plan,logical=module.plan_for([{'index':i,'sha256':str(i)} for i in range(4)])
        self.assertEqual(len(plan),40);self.assertEqual(len(logical),48)
        self.assertEqual(len({r['id'] for r in plan}),40)
        self.assertEqual(sorted({r['seed'] for r in plan}),[981281401,981281402])
        for block in range(8):
            physical=[r for r in plan if r['block']==block]
            refs=[r for r in logical if r['block']==block]
            self.assertEqual(len(physical),5);self.assertEqual(len(refs),6)
            global_fixed=[r['execution_id'] for r in refs if r['family']=='global' and r['method']!='free']
            self.assertEqual(global_fixed[0],global_fixed[1])
            self.assertEqual(len({r['execution_id'] for r in refs if r['family']=='user'}),3)
        first=[r['job'] for r in plan[:5]]
        self.assertEqual(first,['user_all','user_filter','user_free','global_shared','global_free'])


if __name__=='__main__':unittest.main()
