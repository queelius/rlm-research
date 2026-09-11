import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent


class ContractTests(unittest.TestCase):
    def api(self):
        self.assertTrue((ROOT/'batch_contract.py').exists(), 'public strict contract not implemented')
        spec = importlib.util.spec_from_file_location('tested_contract', ROOT/'batch_contract.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_reordered_map_reduces_by_id_and_excludes_user_metadata(self):
        api = self.api()
        self.assertEqual(api.strict_map('{"q0002":"entity","q0001":"numeric value"}', ['q0001','q0002']), {'q0002':'entity','q0001':'numeric value'})
        rows = [{'id':'q0001','user':'u00','text':'How many?'}]
        changed = [{**rows[0], 'user':'u15'}]
        self.assertEqual(api.request_for(rows), api.request_for(changed))
        self.assertIn('Records: [{"id":"q0001","text":"How many?"}]',api.request_for(rows))

    def test_strict_structural_failures_never_repair(self):
        api = self.api()
        for raw in ['[]','{"q0001":"entity","q0001":"entity"}','{}','{"q9999":"entity"}',
                    '{"q0001":"wrong"}','{"q0001":NaN}','{"q0001":"entity"} trailing']:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                api.strict_map(raw,['q0001'])


if __name__ == '__main__': unittest.main()
