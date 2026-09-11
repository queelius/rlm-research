import importlib.util
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parent
def load():
    p=ROOT/'windows.py'
    if not p.exists():raise AssertionError('window implementation missing')
    sp=importlib.util.spec_from_file_location('window_test_impl',p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

class WindowsTests(unittest.TestCase):
    def test_refill_until_two_mixed_or_four_complete_groups(self):
        w=load()
        self.assertTrue(w.needs_group([False,False]));self.assertTrue(w.needs_group([True,False,False]))
        self.assertFalse(w.needs_group([True,True]));self.assertFalse(w.needs_group([False,False,True,False]))
        with self.assertRaises(ValueError):w.validate_prefix([True,False])
        self.assertEqual(w.validate_prefix([False,False,True,False]),'update')
        self.assertEqual(w.validate_prefix([False]*4),'noop')

    def test_noop_keeps_exact_policy_and_optimizer_cursor(self):
        w=load();policy={'step':0,'adapter_sha256':'a','optimizer_sha256':None}
        result=w.transition(0,policy,1,[False]*4,None)
        self.assertEqual(result['next_window'],2);self.assertEqual(result['policy'],policy)
        self.assertEqual(result['optimizer_steps'],0)

    def test_update_advances_once_and_rejects_stale_or_fabricated_steps(self):
        w=load();old={'step':1,'adapter_sha256':'a'};new={'step':2,'adapter_sha256':'b'}
        result=w.transition(1,old,2,[True,True],new);self.assertEqual(result['optimizer_steps'],2)
        for window,policy in [(1,new),(3,new),(2,old)]:
            with self.assertRaises(ValueError):w.transition(1,old,window,[True,True],policy)
        with self.assertRaises(ValueError):w.transition(1,old,2,[False]*4,new)

if __name__=='__main__':unittest.main()
