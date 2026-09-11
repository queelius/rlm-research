import unittest

import protocol as p
import study as s


class InputTests(unittest.TestCase):
    def test_frozen_requests_hold_within_block_text_tags_seed_and_output_schema(self):
        requests = s.read(s.ROOT / "REQUESTS.json")
        rows = p.plan()
        for context_index in range(8):
            block = [row for row in rows if row["context_index"] == context_index]
            bodies = [requests[row["id"]] for row in block]
            self.assertEqual({body["seed"] for body in bodies}, {981626101 + context_index})
            self.assertEqual(len({s.digest(body["structured_outputs"]) for body in bodies}), 1)
            context = p.contexts()[context_index]
            for row, body in zip(block, bodies, strict=True):
                records = p.visible_records(context, row["arm"])
                self.assertTrue(all(record["premise"] == source["premise"] and
                    record["hypothesis"] == source["hypothesis"]
                    for record, source in zip(records, context["records"], strict=True)))
                self.assertEqual([record["requested_tag"] for record in records],
                    p.requested_tags(context))

    def test_natural_prompt_wordings_and_lengths_are_receipted_without_padding(self):
        receipt = s.read(s.ROOT / "CPU_NATIVE.json")
        self.assertFalse(receipt["artificial_prompt_padding"])
        self.assertEqual(receipt["legacy_instruction"], p.LEGACY)
        self.assertEqual(receipt["explicit_instruction"], p.EXPLICIT)
        self.assertEqual(len(receipt["prompt_tokens"]), 40)
        self.assertTrue(receipt["all_fit8192"])

    def test_inventory_and_alias_collision_receipts_cover_current_named_scan(self):
        selection = s.read(s.ROOT / "SELECTION_AUDIT.json")
        collision = s.read(s.ROOT / "COLLISION_AUDIT.json")
        self.assertEqual(selection["selected_contexts"], 8)
        self.assertEqual(selection["selected_premise_groups"], 128)
        self.assertEqual(selection["prior_selected_overlap"], [])
        self.assertTrue(selection["label_mutation_invariant"])
        self.assertEqual(collision["alien_ids"], 384)
        self.assertEqual(collision["alien_visible_collisions"], [])
        self.assertEqual(collision["alien_manifest_text_collisions"], [])
        self.assertEqual(collision["seed_collisions"], [])


if __name__ == "__main__":
    unittest.main()
