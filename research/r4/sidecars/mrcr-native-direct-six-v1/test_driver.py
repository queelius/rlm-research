import copy
import unittest

from driver import request_for_alias, validate_binding_identity, validate_token_evidence


class ContractTests(unittest.TestCase):
    def test_only_alias_changes_from_frozen_full_request(self):
        original = {"model": "old", "messages": [{"role": "user", "content": "ALL\n\nQUESTION"}], "temperature": 0, "max_tokens": 2048}
        before = copy.deepcopy(original)
        actual = request_for_alias(original, "new-original")
        self.assertEqual(actual, {**before, "model": "new-original"})
        self.assertEqual(original, before)
        self.assertNotIn("tools", actual)

    def test_wrong_adapter_identity_is_rejected(self):
        frozen = {"base_model": {"revision": "base", "manifest_sha256": "manifest"}, "adapter": {"model_sha256": "original", "config_sha256": "config"}}
        actual = copy.deepcopy(frozen)
        actual.update(host="127.0.0.1", port=1234, model_alias="new-alias", api_key_env="LOCAL_KEY")
        actual["adapter"]["model_sha256"] = "trained"
        with self.assertRaises(ValueError):
            validate_binding_identity(actual, frozen)

    def test_sampled_evidence_preserved_not_reconstructed(self):
        record = {"prompt_ids": [1, 2], "completion_ids": [7, 9], "completion_logprobs": [-0.25, -0.5]}
        self.assertEqual(validate_token_evidence(record), (2, 2))
        self.assertEqual(record["completion_logprobs"], [-0.25, -0.5])

    def test_missing_or_sentinel_logprobs_are_rejected(self):
        for values in ([-0.25], [-0.25, -9999.0]):
            with self.assertRaises(ValueError):
                validate_token_evidence({"prompt_ids": [1], "completion_ids": [7, 9], "completion_logprobs": values})


if __name__ == "__main__":
    unittest.main()
