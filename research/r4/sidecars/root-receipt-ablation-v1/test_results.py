import importlib
import unittest


class ResultsTests(unittest.TestCase):
    def test_missing_and_failed_episodes_stay_unknown_in_contrasts(self):
        self.assertIsNotNone(importlib.util.find_spec("results"), "triple summary missing")
        r = importlib.import_module("results")
        plan = [{"id":str(i),"arm":arm,"matched_id":"match", "context_sha256":"context", "task_name":"task", "seed":1}
            for i,arm in enumerate(("unchanged","indexed_raw","receipt"))]
        rows = [{"coordinate":plan[0],"derived":{"strict_reward":1,"execution_completed":True}},
                {"coordinate":plan[1],"derived":{"strict_reward":None,"execution_completed":False}}]
        value = r.summarize(rows,plan)
        self.assertEqual(value["unrun_coordinates"],["2"])
        self.assertEqual(value["contrasts"]["receipt_minus_indexed_raw"]["observable_matches"],0)
        self.assertEqual(value["contrasts"]["indexed_raw_minus_unchanged"]["observable_matches"],0)
        self.assertEqual(value["cells"][1]["execution_failures"],1)


if __name__=="__main__":
    unittest.main()
