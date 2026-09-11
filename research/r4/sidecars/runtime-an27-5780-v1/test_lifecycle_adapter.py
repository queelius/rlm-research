import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import lifecycle_adapter as adapter

class LifecycleTests(unittest.TestCase):
    def simulate(self, launcher, digest):
        service = Path('/nonexistent-an27-fixture/service')
        python = Path('/python/bin/python')
        start = dict(command=[str(python.with_name('inference')), '@', str(service/'inference.json')],
            gpu='fixture', launcher_sha256=digest, pid=-1)
        request = dict(command=[str(python),str(launcher),'--binding',str(service.parent/'BINDING.json'),'--run-dir',str(service)], gpu='fixture')
        def read(path):
            if path.name == 'SERVER_START.json': return start
            if path.name == 'SERVICE_REQUEST.json': return request
            return {'same':'binding'}
        scope = dict(ALLOCATION_SERVICE=adapter.SERVICE, verify_amendment=lambda: {},
            c=SimpleNamespace(NATIVE_PYTHON=python, read=read, file_hash=lambda _: 'actual-wrapper'), observe=lambda _: None)
        exec(compile(adapter.claim_source(), str(adapter.SOURCE), 'exec'), scope)
        with patch.object(Path, 'exists', lambda self: self.name == 'SERVER_START.json'):
            return scope['claim_service'](service)
    def test_actual_wrapper_path_and_hash_pass_identity_gate(self):
        self.assertIsNone(self.simulate(adapter.SERVICE, 'actual-wrapper'))
    def test_original_launcher_path_is_rejected(self):
        with self.assertRaises(ValueError):
            self.simulate(adapter.runtime.ROOT.parent/'leaf-role-routing-v1/source/serve.py','actual-wrapper')
    def test_wrong_wrapper_hash_is_rejected(self):
        with self.assertRaises(ValueError):
            self.simulate(adapter.SERVICE, 'original-scientific-hash')

if __name__ == '__main__':
    unittest.main()
