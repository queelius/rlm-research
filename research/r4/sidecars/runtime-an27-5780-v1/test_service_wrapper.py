import unittest
import service_wrapper as service

class ServiceTests(unittest.TestCase):
    def test_driver_replaces_old_shadow_preserving_other_environment(self):
        source = dict(PATH='/old:/export/software/system/nvidia/580.126.09/bin:/bin',
            LD_LIBRARY_PATH='/project/alex_phd/.cache/nvidia-driver-580.126.09/runtime-lib-v1:/other',
            CUDA_VISIBLE_DEVICES='fixture-device', scientific='unchanged')
        result = service.adapt_environment(source)
        self.assertEqual(result['LD_LIBRARY_PATH'], service.DRIVER + ':/other')
        self.assertNotIn('580.126.09', result['PATH'])
        self.assertEqual(result['CUDA_VISIBLE_DEVICES'], source['CUDA_VISIBLE_DEVICES'])
        self.assertEqual(result['scientific'], source['scientific'])
        self.assertIn('580.126.09', source['LD_LIBRARY_PATH'])
    def test_pinned_source_has_one_environment_only_seam(self):
        text = service.source_text()
        self.assertEqual(text.count('environment = adapt_environment(environment)'), 1)
        compile(text, str(service.SOURCE), 'exec')

if __name__ == '__main__':
    unittest.main()
