import unittest

import protocol_v2 as p


class ProtocolV2Tests(unittest.TestCase):
    def test_plan_is_full_three_by_two_grid_on_unchanged_eight_contexts(self):
        rows = p.plan()
        self.assertEqual(len(rows), 48)
        self.assertEqual({row["context_index"] for row in rows}, set(range(8)))
        for context_index in range(8):
            selected = [row for row in rows if row["context_index"] == context_index]
            self.assertEqual({row["arm"] for row in selected}, set(p.ARMS))
            self.assertEqual({row["seed"] for row in selected}, {981626101 + context_index})
        first = [row["arm"] for row in rows if row["pair_position"] == 0]
        self.assertEqual(sorted(first.count(arm) for arm in p.ARMS), [1, 1, 1, 1, 2, 2])

    def test_wording_pairs_change_no_record_or_output_contract(self):
        context = p.contexts()[0]
        for relation in p.RELATIONS:
            legacy = f"{relation}_legacy"
            explicit = f"{relation}_explicit_slot"
            self.assertEqual(p.visible_records(context, legacy), p.visible_records(context, explicit))
            self.assertEqual(p.schema(context, legacy), p.schema(context, explicit))
            legacy_body = p.request(context, {"arm": legacy, "seed": 981626101})
            explicit_body = p.request(context, {"arm": explicit, "seed": 981626101})
            for key in legacy_body:
                if key != "messages":
                    self.assertEqual(legacy_body[key], explicit_body[key])
            self.assertNotEqual(legacy_body["messages"][1]["content"],
                explicit_body["messages"][1]["content"])

    def test_requested_tags_and_relation_identifiers_are_writing_invariant(self):
        context = p.contexts()[0]
        ids = [row["id"] for row in context["records"]]
        requested = ids[17:] + ids[:17]
        self.assertEqual(p.requested_tags(context), requested)
        for wording in ("legacy", "explicit_slot"):
            self.assertEqual(p.visible_ids(context, f"wrong_{wording}"), ids)
            self.assertEqual(p.visible_ids(context, f"aligned_{wording}"), requested)
            self.assertEqual(p.visible_ids(context, f"alien_{wording}"),
                p.visible_ids(context, "alien_legacy"))


if __name__ == "__main__":
    unittest.main()
