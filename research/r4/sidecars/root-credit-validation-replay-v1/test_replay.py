import copy
import importlib.util
import json
from pathlib import Path

import pytest

PHASE1 = Path(__file__).resolve().parents[1] / "root-only-credit-v1"


def implementation():
    assert importlib.util.find_spec("replay") is not None, "validation replay implementation absent"
    return __import__("replay")


def test_exact_validation_coordinates_and_prompts_only():
    replay = implementation()
    original = json.loads((PHASE1 / "SPEC.json").read_text())
    plan, tasks = replay.validation_subset(original)
    assert plan == [row for row in original["plan"] if row["split"] == "validation"]
    assert len(plan) == 8 and len(tasks) == 4
    assert len({row["context_window_id"] for row in plan}) == 2
    assert {row["task_name"] for row in plan} == {task["name"] for task in tasks}
    assert all(task in original["tasks"] for task in tasks)
    assert all(row["client_path"] == "train" and row["temperature"] == 0.5 for row in plan)


def test_original_replay_rejects_changed_root_child_or_endpoint_alias():
    replay = implementation()
    original = json.loads((PHASE1 / "SPEC.json").read_text())
    endpoint = original["source_endpoint_descriptor"]
    binding = copy.deepcopy(original["role_binding"])
    binding.pop("fixed_child")
    replay.validate_original_identity(original, endpoint, binding)
    bad = copy.deepcopy(endpoint)
    bad["model_alias"] = "different-root"
    with pytest.raises(ValueError):
        replay.validate_original_identity(original, bad, binding)
    for alias in binding["models"]:
        bad = copy.deepcopy(binding)
        bad["models"][alias]["adapter_sha256"] = "0" * 64
        with pytest.raises(ValueError):
            replay.validate_original_identity(original, endpoint, bad)


def test_native_role_and_sampler_contract_matches_original_coordinates():
    replay = implementation()
    original = json.loads((PHASE1 / "SPEC.json").read_text())
    plan, _ = replay.validation_subset(original)
    for row in plan:
        context = replay.phase1.make_context(original["endpoint"], row)
        assert context.model == original["role_binding"]["role_map"]["root"]
        assert context.client.type == "train"
        assert context.client.renderer.enable_thinking is True
        assert context.sampling.temperature == 0.5 and context.sampling.seed == row["seed"]
        assert context.sampling.max_tokens == 2048
