import unittest
from pathlib import Path
import isolation_short as owned

class TestIsolation(unittest.TestCase):
    def test_private_paths_cpu_and_no_home_reassignment(self):
        argv,env=owned.command(['run','--workdir','/app','image'],{'HOME':'/sentinel-home'})
        self.assertEqual(env['HOME'],'/sentinel-home')
        self.assertIn('--root',argv)
        self.assertEqual(argv[argv.index('--root')+1],'/tmp/rlmc.0m4242/root')
        self.assertEqual(argv[argv.index('--runroot')+1],'/tmp/rlmc.0m4242/runroot')
        self.assertEqual(argv[argv.index('--cpuset-cpus')+1],'34,35')
        self.assertNotIn('--signature-policy',argv)
        self.assertEqual(env['XDG_RUNTIME_DIR'],'/tmp/rlmc.0m4242/runtime')
        self.assertIn('type=tmpfs,destination=/app',argv)
        self.assertTrue(Path(env['CONTAINERS_CONF']).is_relative_to(owned.ROOT))

if __name__=='__main__':unittest.main()
