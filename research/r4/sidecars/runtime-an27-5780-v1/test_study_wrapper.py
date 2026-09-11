import unittest
from unittest.mock import patch
from types import SimpleNamespace
from pathlib import Path
import study_wrapper as wrapper

class WrapperTests(unittest.TestCase):
    def test_only_capture_readout_argv_are_routed(self):
        for name in ('capture', 'readout'):
            source = ['/python', str(wrapper.SCIENTIFIC / (name + '.py')), '--output', '/out']
            self.assertEqual(wrapper.rewrite(source), ['/python', str(wrapper.ROOT / 'study_wrapper.py'), name, '--output', '/out'])
        train = ['/training-python', str(wrapper.SCIENTIFIC / 'train.py'), '--arm', 'action_only']
        self.assertEqual(wrapper.rewrite(train), train)
    def test_local_callbacks_use_new_store_and_exact_image(self):
        local = SimpleNamespace(LOCAL=Path('/old'), STORE=Path('/missing'))
        st = SimpleNamespace(local=local)
        self.assertIs(wrapper.adapt_stack(st), st)
        self.assertEqual(local.LOCAL, wrapper.ROOT)
        self.assertEqual(local.STORE, wrapper.owned.STORE)
        local.validate_store()
        with self.assertRaises(ValueError):
            local.validate_store('/missing')
        with patch.object(wrapper, 'sha', return_value='ready-hash-fixture'):
            delta = local.delta(Path('/example'))
        self.assertEqual(delta['image_id'], wrapper.IMAGE)
        self.assertTrue(Path(delta['verifiers_cache']).is_relative_to(wrapper.owned.STORE))

if __name__ == '__main__':
    unittest.main()
