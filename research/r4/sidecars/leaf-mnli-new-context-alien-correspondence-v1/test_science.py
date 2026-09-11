import unittest

import protocol as p


class ScienceTests(unittest.TestCase):
    def test_exact_48_plan_and_rotated_dispatch(self):
        rows = p.plan()
        self.assertEqual(len(rows), 48)
        self.assertEqual({row["context_index"] for row in rows}, set(range(16)))
        for context_index in range(16):
            selected = [row for row in rows if row["context_index"] == context_index]
            self.assertEqual({row["arm"] for row in selected}, set(p.ARMS))
            self.assertEqual({row["seed"] for row in selected}, {981622101 + context_index})
        first = [row["arm"] for row in rows if row["pair_position"] == 0]
        self.assertEqual(sorted(first.count(arm) for arm in p.ARMS), [5, 5, 6])

    def test_alien_ids_are_global_unique_and_length_matched(self):
        contexts = p.contexts()
        visible = {item["id"] for context in contexts for item in context["records"]}
        aliens = [tag for context in contexts for tag in p.expected_tags(context, "alien")]
        self.assertEqual(len(aliens), 768)
        self.assertEqual(len(set(aliens)), 768)
        self.assertFalse(set(aliens) & visible)
        tokenizer = p.s.tokenizer()
        for context in contexts:
            shifted = p.expected_tags(context, "shift17")
            alien = p.expected_tags(context, "alien")
            self.assertTrue(all(len(tokenizer.encode(a, add_special_tokens=False)) ==
                len(tokenizer.encode(b, add_special_tokens=False))
                for a, b in zip(alien, shifted, strict=True)))

    def test_selected_contexts_are_label_blind_and_disjoint_receipted(self):
        receipt = p.s.read(p.s.ROOT / "SELECTION_AUDIT.json")
        self.assertTrue(receipt["label_mutation_invariant"])
        self.assertEqual(receipt["selected_premise_groups"], 256)
        self.assertEqual(receipt["prior_selected_overlap"], [])


if __name__ == "__main__":
    unittest.main()
