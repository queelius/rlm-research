"""Focused contract tests: no permissive parsing, prompt drift, or invented coverage."""
import asyncio
import importlib
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path


class ReceiptTests(unittest.TestCase):
    def api(self):
        self.assertIsNotNone(importlib.util.find_spec("receipt_api"), "receipt implementation missing")
        return importlib.import_module("receipt_api")

    def test_valid_target_only_and_reordered_ids(self):
        api = self.api()
        raw = '{"q0002":"no","q0001":"yes"}'
        value = api.parse_receipt(raw, ["q0001", "q0002"], ["yes", "no"])
        self.assertTrue(value["valid"])
        self.assertEqual(value["labels_by_id"], {"q0001": "yes", "q0002": "no"})
        self.assertEqual(value["raw_answer"], raw)
        self.assertEqual(value["requested_id_coverage"], 1)
        self.assertEqual(value["returned_order"], ["q0002", "q0001"])

    def test_invalid_outputs_never_expose_mapping_or_repair_raw(self):
        api = self.api()
        for raw in ('{}', '{"q0001":"yes","q0001":"no"}',
                    '{"q9999":"yes"}', '{"q0001":"YES"}',
                    '[{"id":"q0001","label":"yes"}]',
                    '```json\n{"q0001":"yes"}\n```',
                    '{"q0001":"yes"} trailing', '{"q0001":NaN}',
                    '{"q0001":true}', '{"q0001":{"label":"yes"}}'):
            with self.subTest(raw=raw):
                value = api.parse_receipt(raw, ["q0001"], ["yes", "no"])
                self.assertFalse(value["valid"])
                self.assertIsNone(value["labels_by_id"])
                self.assertEqual(value["raw_answer"], raw)

    def test_identical_prompt_one_call_and_exception_propagation(self):
        api = self.api()
        native = types.SimpleNamespace(answer='{"q0001":"yes"}',
            session_dir=None, usage=types.SimpleNamespace(prompt_tokens=10, completion_tokens=3), turns=1)
        calls = []
        async def fake(prompt):
            calls.append(prompt)
            return native
        old = sys.modules.get("rlm.api")
        sys.modules["rlm.api"] = types.SimpleNamespace(run=fake)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            api.ROOT = root
            catalog = {"context_sha256": "context-sha", "records": [{"id":"q0001", "text":"Record one", "group_id":"group-one", "text_sha256":"row-sha"}]}
            (root / "receipt_catalog.json").write_text(json.dumps(catalog))
            try:
                answers = []
                for arm in ("indexed_raw", "receipt"):
                    (root / "receipt_config.json").write_text(json.dumps({"arm":arm}))
                    result = asyncio.run(api.rlm_records(["q0001"], "Is it human?", ["yes", "no"]))
                    answers.append(result.answer)
                    self.assertIs(result.native_result, native)
                    self.assertEqual(hasattr(result, "receipt"), arm == "receipt")
                    if arm == "receipt":
                        self.assertTrue(result.receipt()["valid"])
                self.assertEqual(answers, [native.answer, native.answer])
                self.assertEqual(len(calls), 2)
                self.assertEqual(calls[0], calls[1])
                self.assertIn('"id":"q0001","text":"Record one"', calls[0])
                for selected in ([], ["q0001", "q0001"], ["unknown"]):
                    with self.assertRaises(ValueError):
                        asyncio.run(api.rlm_records(selected, "query", ["yes", "no"]))
                self.assertEqual(len(calls), 2)
                async def broken(prompt):
                    raise RuntimeError("transport failed")
                sys.modules["rlm.api"] = types.SimpleNamespace(run=broken)
                with self.assertRaisesRegex(RuntimeError, "transport failed"):
                    asyncio.run(api.rlm_records(["q0001"], "query", ["yes", "no"]))
            finally:
                if old is None:
                    sys.modules.pop("rlm.api", None)
                else:
                    sys.modules["rlm.api"] = old


if __name__ == "__main__":
    unittest.main()
