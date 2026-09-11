import unittest

import protocol_v2 as p
import scoring_v2 as scoring


class ScoringV2Tests(unittest.TestCase):
    def test_valid_wrong_arm_scores_displayed_and_named_labels_separately(self):
        context = p.contexts()[0]
        tags = p.requested_tags(context)
        displayed = [record["gold_label"] for record in context["records"]]
        message = {"content": p.s.serialize([{"tag": tag, "label": label}
            for tag, label in zip(tags, displayed, strict=True)]), "tool_calls": []}
        score = scoring.score(message, context, "wrong_explicit_slot")
        self.assertTrue(score["contract_valid"])
        self.assertEqual(score["strict_correct"], 48)
        by_id = {record["id"]: record["gold_label"] for record in context["records"]}
        disagree = [(shown, by_id[tag]) for shown, tag in zip(displayed, tags, strict=True)
            if shown != by_id[tag]]
        self.assertEqual(score["named_disagree_items"], len(disagree))
        self.assertEqual(score["named_correct_disagree"], 0)
        self.assertEqual(score["third_correct_disagree"], 0)

    def test_wrong_tag_is_observed_contract_failure_not_null(self):
        context = p.contexts()[0]
        tags = p.requested_tags(context)
        values = [{"tag": tag, "label": "neutral"} for tag in tags]
        values[0]["tag"] = tags[1]
        score = scoring.score({"content": p.s.serialize(values), "tool_calls": []},
            context, "aligned_legacy")
        self.assertTrue(score["available"])
        self.assertFalse(score["contract_valid"])
        self.assertEqual(score["strict_correct"], 0)
        self.assertEqual(score["strict_bounds"], [0, 0])


if __name__ == "__main__":
    unittest.main()
