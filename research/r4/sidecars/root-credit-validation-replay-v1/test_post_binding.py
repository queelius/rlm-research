import copy
import importlib.util

import pytest


def implementation():
    assert importlib.util.find_spec("post_replay") is not None, "post-update binding not implemented"
    return __import__("post_replay")


def fixture():
    return {
        "schema": "one-step-root-only-tis-result-v1", "optimizer_steps": 1,
        "child_loss_tokens": 0, "observation_loss_tokens": 0,
        "gradient_norm_before_clip": 0.1, "trainable_parameter_delta_l2": 0.2,
        "recipe_sha256": "recipe", "correction_diagnostics": {"guard_failures": []},
        "input_identity": {"input_binding": {"original_root_sha256": "root", "fixed_child_sha256": "child"},
                           "child_adapter_loaded_into_training_model": False},
    }


def test_post_binding_requires_real_root_only_one_step_result():
    post = implementation()
    valid = fixture()
    post.validate_result_contract(valid, original_root_sha="root", child_sha="child", recipe_sha="recipe")
    for key, value in [("optimizer_steps", 0), ("child_loss_tokens", 1), ("observation_loss_tokens", 1),
                       ("gradient_norm_before_clip", 0), ("trainable_parameter_delta_l2", float("nan"))]:
        bad = copy.deepcopy(valid)
        bad[key] = value
        with pytest.raises(ValueError):
            post.validate_result_contract(bad, original_root_sha="root", child_sha="child", recipe_sha="recipe")
    bad = copy.deepcopy(valid)
    bad["input_identity"]["input_binding"]["fixed_child_sha256"] = "wrong-child"
    with pytest.raises(ValueError):
        post.validate_result_contract(bad, original_root_sha="root", child_sha="child", recipe_sha="recipe")


def test_post_endpoint_must_name_actual_new_root_and_unchanged_base():
    post = implementation()
    source = {"source_endpoint_descriptor": {"base_model": {"path": "/base", "revision": "r"}}}
    binding = {"role_map": {"root": post.POST_ALIAS}, "models": {post.POST_ALIAS: {"path": "/trained", "adapter_sha256": "new", "config_sha256": "config"}}}
    endpoint = {"host": "127.0.0.1", "port": 18601, "model_alias": post.POST_ALIAS,
        "base_model": {"path": "/base", "revision": "r"}, "role_binding_sha256": "binding",
        "adapter": {"path": "/trained", "model_sha256": "new", "config_sha256": "config"}}
    post.validate_endpoint(source, endpoint, binding, "binding")
    endpoint["model_alias"] = "old-original"
    with pytest.raises(ValueError):
        post.validate_endpoint(source, endpoint, binding, "binding")
