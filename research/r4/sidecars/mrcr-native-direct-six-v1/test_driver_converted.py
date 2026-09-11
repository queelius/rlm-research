import copy
import unittest

import torch

import driver
import driver_converted as amended


class ConvertedBindingTests(unittest.TestCase):
    def setUp(self):
        self.frozen = driver.read(driver.ROOT / "SPEC.json")["original_identity"]
        self.endpoint = driver.read(amended.ENDPOINT)

    def test_exact_converted_binding_passes_without_changing_original_identity(self):
        before = copy.deepcopy(self.frozen)
        amended.validate_converted_binding(self.endpoint, self.frozen)
        self.assertEqual(self.frozen, before)
        with self.assertRaises(ValueError):
            driver.validate_binding_identity(self.endpoint, self.frozen)

    def test_other_weights_path_alias_or_role_binding_fail(self):
        for section, key, wrong in (
            ("adapter", "model_sha256", "0" * 64),
            ("adapter", "config_sha256", "0" * 64),
            ("adapter", "path", "/tmp/unrelated-adapter"),
            (None, "model_alias", "strict-rlm-qwen3-4b-role-sft-selected-v1"),
            (None, "role_binding_sha256", "0" * 64),
        ):
            endpoint = copy.deepcopy(self.endpoint)
            (endpoint if section is None else endpoint[section])[key] = wrong
            with self.assertRaises(ValueError):
                amended.validate_converted_binding(endpoint, self.frozen)

    def test_tensor_byte_proof_rejects_value_dtype_shape_and_missing_key(self):
        key = "model.layers.0.mlp.down_proj.lora_A.weight"
        original = {key: torch.arange(8, dtype=torch.float32).reshape(2, 4)}
        target = "base_model.model." + key
        converted = {target: original[key].clone()}
        evidence = amended.prove_tensor_mapping(original, converted)
        self.assertEqual(len(evidence), 1)
        self.assertEqual(evidence[key]["dtype"], "torch.float32")
        variants = [
            {target: original[key] + 1},
            {target: original[key].to(torch.float16)},
            {target: original[key].reshape(4, 2)},
            {},
        ]
        for bad in variants:
            with self.assertRaises(ValueError):
                amended.prove_tensor_mapping(original, bad)


if __name__ == "__main__":
    unittest.main()
