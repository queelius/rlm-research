import copy
import unittest

import study as s


class StudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tasks = s.make_tasks()

    def test_prompt_only_adds_literal_suffix_and_keeps_gold_context_config(self):
        for task in self.tasks.values():
            original = s.native.capture.role.with_prompt(task, "sft_child")
            left, right = [s.with_prompt(task, arm) for arm in s.ARMS]
            self.assertEqual(left.data.model_dump(), original.data.model_dump())
            self.assertEqual(left.config, right.config)
            self.assertEqual(right.data.prompt, left.data.prompt + s.SUFFIX)
            expected = left.data.model_dump()
            expected["prompt"] += s.SUFFIX
            self.assertEqual(right.data.model_dump(), expected)
            self.assertNotEqual(left.hash, right.hash)

    def test_plan_has_96_paired_fresh_balanced_coordinates(self):
        plan = s.build_plan(self.tasks)
        self.assertEqual(len(plan), 96)
        self.assertEqual(len({r["id"] for r in plan}), 96)
        self.assertEqual(len({r["matched_id"] for r in plan}), 24)
        self.assertEqual(len({r["context_sha256"] for r in plan}), 6)
        self.assertFalse({r["seed"] for r in plan} & s.prior_seeds())
        by_match = {}
        for row in plan:
            by_match.setdefault(row["matched_id"], []).append(row)
        for rows in by_match.values():
            self.assertEqual(len(rows), 4)
            self.assertEqual(len({r["seed"] for r in rows}), 1)
            self.assertEqual({(r["weight"], r["arm"]) for r in rows},
                {(w, a) for w in s.WEIGHTS for a in s.ARMS})
        for weight in s.WEIGHTS:
            rows = [r for r in plan if r["weight"] == weight]
            self.assertEqual(sum(r["arm"] == "contract" for r in rows[::2]), 12)
            for i in range(0, 48, 2):
                self.assertEqual(rows[i]["pair_id"], rows[i+1]["pair_id"])
                self.assertEqual(rows[i]["seed"], rows[i+1]["seed"])
                self.assertNotEqual(rows[i]["arm"], rows[i+1]["arm"])

    def test_binding_rejects_wrong_root_or_child(self):
        policies = s.policies()
        for weight, policy in policies.items():
            bound = s.binding_for(policy)
            self.assertEqual(s.validate_binding(bound), weight)
            wrong = copy.deepcopy(bound)
            wrong["models"][wrong["fixed_child"]]["adapter_sha256"] = "0" * 64
            with self.assertRaises(ValueError):
                s.validate_binding(wrong)
        wrong = copy.deepcopy(policies["step8"])
        wrong["adapter_sha256"] = policies["original"]["adapter_sha256"]
        with self.assertRaises(ValueError):
            s.binding_for(wrong)

    def test_native_context_changes_no_sampler_or_renderer(self):
        endpoint = s.planned_endpoint(s.binding_for(s.policies()["original"]))
        row = s.build_plan(self.tasks)[0]
        ctx = s.native.capture.make_context(endpoint, row)
        self.assertEqual(ctx.client.type, "train")
        self.assertEqual(ctx.client.renderer.model_dump(exclude_none=True),
                         {"name": "qwen3", "enable_thinking": True})
        metadata = s.native.capture.native.request_metadata(endpoint, row)
        for key, expected in {"temperature": .5, "top_p": 1.0, "top_k": -1,
                "min_p": 0.0, "max_tokens": 2048, "seed": row["seed"]}.items():
            self.assertEqual(metadata[key], expected)

    def test_missing_pair_outcome_and_diagnostics_remain_null(self):
        import analysis
        plan = s.build_plan(self.tasks)
        row = plan[0]
        metrics = {"strict_reward": 1, "execution_completed": True}
        report = analysis.summarize([{"coordinate": row, "derived": metrics}], plan)
        self.assertEqual(len(report["contexts"]), 6)
        self.assertEqual(len(report["matched"]), 24)
        self.assertEqual(report["recorded"], 1)
        self.assertTrue(all(p["interaction"] is None for p in report["matched"]))
        self.assertIsNone(analysis.code_markers({})["direct_answer_extend"])

    def test_static_code_marker_does_not_execute_generated_code(self):
        import analysis
        code = "raise RuntimeError('must never run')\nxs.extend(child.answer)\ny = json.loads(other.answer)"
        markers = analysis.static_markers(code)
        self.assertEqual(markers["direct_answer_extend"], 1)
        self.assertEqual(markers["json_loads"], 1)

    def test_private_capture_adapter_restores_shared_functions(self):
        driver = s.c.load("return_contract_driver_test", s.ROOT / "driver.py")
        capture = s.native.capture
        old = (capture.q.make_context, capture.base.with_prompt, capture.base.crossover_metrics)
        with driver.collector_adapters():
            self.assertIs(capture.base.with_prompt, s.with_prompt)
            self.assertIs(capture.q.make_context, capture.make_context)
        self.assertEqual(old, (capture.q.make_context, capture.base.with_prompt, capture.base.crossover_metrics))

    def test_partial_phase_summary_has_null_other_root_not_key_error(self):
        import analysis
        plan = [r for r in s.build_plan(self.tasks) if r["weight"] == "original"]
        record = {"coordinate": plan[0], "derived": {"strict_reward": 1, "execution_completed": True}}
        report = analysis.summarize([record], plan)
        self.assertEqual(report["planned"], 48)
        self.assertTrue(all(r["unchanged_step8_minus_original"] is None for r in report["matched"]))


if __name__ == "__main__":
    unittest.main()
