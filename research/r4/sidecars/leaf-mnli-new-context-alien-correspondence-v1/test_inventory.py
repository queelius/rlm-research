import unittest

import collect
import protocol as p


class InventoryTests(unittest.TestCase):
    def test_summary_accepts_all_48_planned_rows(self):
        rows = [{"coordinate": row, "score": {"available": False, "strict_correct": None,
            "contract_valid": None, "shape_valid": None, "shape_positional_correct": None,
            "tag_position_matches": None, "whole_batch_correct": None},
            "physical_attempt": False, "usage_observed": None} for row in p.plan()]
        summary = collect.summarize(rows)
        self.assertEqual(set(summary["arms"]), set(p.ARMS))
        self.assertEqual(sum(cell["planned"] for cell in summary["arms"].values()), 48)


if __name__ == "__main__":
    unittest.main()
