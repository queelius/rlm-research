import ast
import unittest
import recovery_wrapper as recovery

class RecoveryTests(unittest.TestCase):
    def test_counted_output_and_subprocess_only_diff(self):
        for name in recovery.COUNTS:
            with self.subTest(source=name):
                original = (recovery.SCIENCE/name).read_text()
                expected = original.replace(recovery.OLD_OUTPUT,recovery.NEW_OUTPUT)
                if name == 'launch.py':
                    for entry in ('capture','train','readout'):
                        expected = expected.replace("str(s.ROOT/'"+entry+".py')", "str(RECOVERY_WRAPPER),'"+entry+"'")
                actual = recovery.transformed(name)
                self.assertEqual(actual,expected)
                self.assertNotIn(recovery.OLD_OUTPUT,actual)
                ast.parse(actual)
                if name in ('capture.py','readout.py'):
                    self.assertEqual(actual,original)
    def test_all_three_child_argv_keep_interpreters_and_route_to_same_wrapper(self):
        tree = ast.parse(recovery.transformed('launch.py'))
        found = []
        for node in ast.walk(tree):
            if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='argv' for t in node.targets):
                found.append(node.value)
        self.assertEqual(len(found),3)
        for value, entry in zip(found, ('capture','train','readout')):
            self.assertIsInstance(value,ast.List)
            self.assertEqual(ast.unparse(value.elts[1]),'str(RECOVERY_WRAPPER)')
            self.assertEqual(value.elts[2].value,entry)
            self.assertEqual(ast.unparse(value.elts[0]),'str(s.TRAIN)' if entry=='train' else 'str(s.NATIVE)')

if __name__ == '__main__':
    unittest.main()
