import importlib.util
import unittest
from pathlib import Path


class OwnerTests(unittest.TestCase):
    def test_ready_identity_survives_sorted_json_storage(self):
        import json
        import study
        value = {'z': 1, 'a': {'y': 2, 'b': 3}}
        restored = json.loads(json.dumps(value, sort_keys=True))
        self.assertEqual(study.digest(value), study.digest(restored))

    def test_actual_owned_lifecycle_authenticates_new_wrapper(self):
        import owner
        import study
        suite = owner.suite()
        self.assertEqual(suite.SERVE, study.ROOT / 'service_wrapper.py')
        self.assertEqual(suite.life.__dict__['ALLOCATION_SERVICE'], suite.SERVE)

    def test_full_service_entry_pins_qualified_module_namespace_before_launch(self):
        self.assertIsNotNone(importlib.util.find_spec('service_wrapper'), 'new explicit service wrapper absent')
        import importlib.machinery as machinery
        import importlib.util as util
        import json
        import os
        import subprocess
        import sys
        import tempfile
        from unittest.mock import patch
        import service_wrapper
        import study
        import owner
        observed = {}
        class Loader:
            def create_module(self, spec): return None
            def exec_module(self, module):
                module.PRIME_ENV = Path('/fixture/prime')
                module._port_free = lambda port: True
                module._environment = lambda: {'PATH': '/usr/bin', 'LD_LIBRARY_PATH': ''}
                module._server_environment = lambda environment, replica: dict(environment)
                module._wait_endpoint_model = lambda endpoint, process, alias, timeout: observed.update(alias=alias)
        original_spec = util.spec_from_file_location
        def spec(name, path):
            return machinery.ModuleSpec(name, Loader()) if name == 'base_service_environment' else original_spec(name, path)
        def spawn(command, **kwargs):
            observed['command'] = command
            return type('Process', (), {'pid': 424242})()
        with tempfile.TemporaryDirectory(prefix='join-service-test-') as directory:
            root = Path(directory); binding = owner.binding(); study.write(root / 'BINDING.json', binding)
            with patch.object(util, 'spec_from_file_location', spec), patch.object(subprocess, 'Popen', spawn), \
                 patch.object(sys, 'argv', [str(study.ROOT / 'service_wrapper.py'), '--binding', str(root / 'BINDING.json'), '--run-dir', str(root / 'service')]), \
                 patch.dict(os.environ, {'CUDA_VISIBLE_DEVICES': 'fixture-only', 'STRICT_RLM_CALIBRATION_API_KEY': 'fixture-not-secret'}):
                service_wrapper.main()
            self.assertEqual(observed['alias'], study.MODEL['alias'])
            self.assertEqual(observed['command'], ['/fixture/prime/bin/inference', '@', str(root / 'service/inference.json')])
            self.assertEqual(study.read(root / 'service/BINDING.json'), binding)
            self.assertIsNone(study.read(root / 'service/endpoint-original.json')['adapter'])

    def test_actual_collector_cli_is_bound_to_new_attempt(self):
        self.assertIsNotNone(importlib.util.find_spec('owner'), 'new owner implementation absent')
        import owner
        import study
        argv = owner.collector_argv(study.ATTEMPT / 'owned-service', study.ATTEMPT, 12345.)
        value = owner.validate_argv(argv)
        self.assertEqual(value['output'], study.ATTEMPT / 'rollout')
        with self.assertRaises(ValueError):
            owner.validate_argv([x.replace('root-native-partition-join-v1', 'root-partition-final-interface-v1') for x in argv])


if __name__ == '__main__': unittest.main()
