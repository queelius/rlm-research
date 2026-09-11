"""Single semantic binding and inclusive envelope boundaries; no service launch."""
import importlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent


def module():
    assert (ROOT / "owned.py").exists(), "owned single-adapter wrapper absent"
    return importlib.import_module("owned")


def test_binding_contains_only_old_adapter_and_exact_frozen_alias():
    owned = module()
    import driver
    binding = owned.service_binding(driver.weights(), ROOT / "WEIGHTS.json", "fixed-weight-file-sha")
    assert list(binding["models"]) == ["strict-rlm-qwen3-4b-role-sft-selected-v1"]
    assert binding["role_map"] == {"root": "strict-rlm-qwen3-4b-role-sft-selected-v1",
                                  "children": ["strict-rlm-qwen3-4b-role-sft-selected-v1"]}
    assert next(iter(binding["models"].values()))["adapter_sha256"] == "c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3"
    assert binding["selection_sha256"] == "fixed-weight-file-sha"


def test_owned_work_reserves_cleanup_inside_1800_seconds():
    owned = module()
    assert owned.work_deadline(100) == 1780
    assert owned.collection_command_cap(100, 110) == 930
    assert owned.collection_command_cap(100, 1700) == 80
    with pytest.raises(TimeoutError):
        owned.collection_command_cap(100, 1780)
