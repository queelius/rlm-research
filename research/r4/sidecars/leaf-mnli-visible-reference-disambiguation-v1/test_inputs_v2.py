import unittest

import protocol_v2 as p
import study as s


class InputsV2Tests(unittest.TestCase):
    def test_additive_manifest_keeps_selected_contexts_and_has_exact_48_requests(self):
        amendment = s.read(s.ROOT / "ALLOCATION_AMENDMENT_V2.json")
        self.assertEqual(amendment["draft_data_sha256"],
            "e4ee78099d12d22b2e4e38fc2aa641a027712a34bf604124f753cf741ee829e8")
        self.assertEqual(amendment["draft_selection_audit_sha256"],
            "202997ba0aa612e772fb0857209926fb56c568c3f42ae98661cf5b46938265e3")
        rows = s.read(s.ROOT / "PLAN_v2.json")
        requests = s.read(s.ROOT / "REQUESTS_v2.json")
        self.assertEqual(rows, p.plan())
        self.assertEqual(set(requests), {row["id"] for row in rows})
        self.assertEqual(len(rows), 48)

    def test_native_receipt_freezes_natural_wordings_prefixes_and_fixed_contracts(self):
        receipt = s.read(s.ROOT / "CPU_NATIVE_v2.json")
        self.assertFalse(receipt["artificial_prompt_padding"])
        self.assertEqual(receipt["legacy_instruction"], p.LEGACY)
        self.assertEqual(receipt["explicit_instruction"], p.EXPLICIT)
        self.assertEqual(len(receipt["prompt_tokens"]), 48)
        self.assertEqual(len(receipt["request_wire_sha256"]), 48)
        self.assertTrue(receipt["all_fit8192"])
        self.assertEqual(receipt["schemas_compiled"], 48)
        self.assertTrue(receipt["all_output_schemas_equal_within_block"])

    def test_collision_receipt_covers_aliases_seeds_and_named_inventory(self):
        receipt = s.read(s.ROOT / "COLLISION_AUDIT_v2.json")
        self.assertEqual(receipt["alien_ids"], 384)
        self.assertEqual(receipt["alien_visible_collisions"], [])
        self.assertEqual(receipt["alien_manifest_text_collisions"], [])
        self.assertEqual(receipt["seed_collisions"], [])
        self.assertEqual(receipt["scope"], "named inventory only")


if __name__ == "__main__":
    unittest.main()
