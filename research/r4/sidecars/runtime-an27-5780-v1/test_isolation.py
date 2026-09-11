import unittest
from unittest.mock import patch
import isolation_short as owned

class IsolationTests(unittest.TestCase):
    def test_exact_owned_paths_cpu_home_and_runtime_contract(self):
        argv, env = owned.command(['run', '--workdir', '/app', 'image'], {'HOME': '/sentinel-home'})
        self.assertEqual(env['HOME'], '/sentinel-home')
        self.assertEqual(argv[argv.index('--root') + 1], str(owned.STORE / 'root'))
        self.assertEqual(argv[argv.index('--runroot') + 1], str(owned.STORE / 'runroot'))
        self.assertEqual(argv[argv.index('--cpuset-cpus') + 1], '14,15')
        self.assertNotIn('--signature-policy', argv)
        self.assertIn('type=tmpfs,destination=/app', argv)
        self.assertIn('no-new-privileges', argv)
        self.assertEqual(env['XDG_RUNTIME_DIR'], str(owned.STORE / 'runtime'))
    def test_wrong_uid_rejected(self):
        with patch.object(owned.os, 'getuid', return_value=-1), self.assertRaises(ValueError):
            owned.command(['ps'])
    def test_unavailable_cpu_rejected(self):
        with patch.object(owned.os, 'sched_getaffinity', return_value={0,1}), self.assertRaises(ValueError):
            owned.command(['ps'])
    def test_wrong_node_rejected(self):
        with patch.object(owned.socket, 'gethostname', return_value='other-node'), self.assertRaises(ValueError):
            owned.command(['ps'])

if __name__ == '__main__':
    unittest.main()
