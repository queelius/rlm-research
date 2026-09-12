import importlib.util
import json
from pathlib import Path

import pytest
import torch
from safetensors.torch import save_file


ROOT = Path(__file__).resolve().parent


def load(name):
    path = ROOT / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"token_tis_eval_test_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_schedule_is_exact_existing_held16_and_not_training_groups():
    study = load("study")
    rows = study.schedule("held")
    assert len(rows) == 16
    assert [row["seed"] for row in rows] == list(range(202609132100, 202609132116))
    assert len({row["record_id"] for row in rows}) == 16
    training = study.read(study.TRAIN_INPUTS)["episodes"]
    assert not ({row["record_id"] for row in rows} & {row["group_id"] for row in training})


def test_training_header_requires_both_independent_step1_branches(tmp_path):
    checkpoint = load("checkpoint")
    output = tmp_path / "attempt"
    branches = {
        name: {
            "status": "UPDATED",
            "optimizer_steps": 1,
            "checkpoint": str(output / "branches" / name / "checkpoint-0001"),
        }
        for name in ("lr1e-5", "lr1e-4")
    }
    checkpoint.validate_result_header(
        {"status": "UPDATED_TWO_INDEPENDENT_BRANCHES", "branches": branches}, output
    )
    branches["lr1e-4"]["optimizer_steps"] = 2
    with pytest.raises(ValueError, match="independent step1"):
        checkpoint.validate_result_header(
            {"status": "UPDATED_TWO_INDEPENDENT_BRANCHES", "branches": branches}, output
        )


def test_zero_adapter_and_three_bindings_change_only_root(tmp_path, monkeypatch):
    checkpoint = load("checkpoint")
    study = checkpoint.study
    source = tmp_path / "checkpoint"
    zero = tmp_path / "zero"
    source.mkdir()
    (source / "adapter_config.json").write_text(
        json.dumps({"bias": "none", "lora_dropout": 0.0, "r": 8, "lora_alpha": 16})
    )
    save_file(
        {
            "base.a.lora_A.weight": torch.ones(2, 3),
            "base.a.lora_B.weight": torch.ones(4, 2),
        },
        source / "adapter_model.safetensors",
    )
    receipt = checkpoint.materialize_zero_adapter(source, zero)
    checkpoint.validate_zero_adapter(zero, receipt)
    fake = {
        "zero_adapter": {**receipt, "path": str(zero)},
        "branches": {
            name: {
                "checkpoint": str(source),
                "adapter_model_sha256": study.sha(source / "adapter_model.safetensors"),
                "adapter_config_sha256": study.sha(source / "adapter_config.json"),
            }
            for name in ("lr1e-5", "lr1e-4")
        },
    }
    monkeypatch.setattr(checkpoint, "verify_checkpoint", lambda: fake)
    receipt_path = tmp_path / "CHECKPOINT_READY.json"
    receipt_path.write_text("{}")
    monkeypatch.setattr(checkpoint, "RECEIPT", receipt_path)
    bindings = {arm: checkpoint.binding(arm) for arm in ("base", "lr1e-5", "lr1e-4")}
    assert len({tuple(value["role_map"]["children"]) for value in bindings.values()}) == 1
    assert len({value["fixed_child"] for value in bindings.values()}) == 1
    assert len({value["role_map"]["root"] for value in bindings.values()}) == 3


def test_owner_plan_has_three_fixed_held_arms_and_no_training():
    owner = load("owner")
    plan = owner.plan()
    assert list(plan["stage_argv"]) == ["base", "lr1e-5", "lr1e-4"]
    assert all(value[-1] == "650" for value in plan["stage_argv"].values())
    assert plan["episodes_per_arm"] == 16
    assert plan["optimizer_steps"] == 0
    assert plan["selection"] is False
