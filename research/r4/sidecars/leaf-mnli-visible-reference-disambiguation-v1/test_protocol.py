import unittest

import protocol as p


class ProtocolTests(unittest.TestCase):
    def test_plan_has_five_paired_arms_for_each_of_eight_contexts(self):
        rows = p.plan()
        self.assertEqual(len(rows), 40)
        self.assertEqual({row["context_index"] for row in rows}, set(range(8)))
        for context_index in range(8):
            selected = [row for row in rows if row["context_index"] == context_index]
            self.assertEqual({row["arm"] for row in selected}, set(p.ARMS))
            self.assertEqual({row["seed"] for row in selected}, {981626101 + context_index})

    def test_wrong_alien_and_aligned_identifiers_have_declared_semantics(self):
        context = p.contexts()[0]
        ids = [row["id"] for row in context["records"]]
        requested = ids[17:] + ids[:17]
        self.assertEqual(p.requested_tags(context), requested)
        self.assertEqual(p.visible_ids(context, "wrong_legacy"), ids)
        self.assertEqual(p.visible_ids(context, "wrong_explicit_slot"), ids)
        self.assertEqual(p.visible_ids(context, "aligned_explicit_slot"), requested)
        alien = p.visible_ids(context, "alien_legacy")
        self.assertEqual(alien, p.visible_ids(context, "alien_explicit_slot"))
        self.assertFalse(set(alien) & set(ids))
        self.assertEqual(len(set(alien)), 48)

    def test_output_schema_is_identical_across_arms(self):
        context = p.contexts()[0]
        schemas = [p.schema(context, arm) for arm in p.ARMS]
        self.assertTrue(all(value == schemas[0] for value in schemas[1:]))


if __name__ == "__main__":
    unittest.main()
