import json
from pathlib import Path

import pytest

import checkpoint
import collect
import study


def test_held_schedule_is_one_paired_rollout_per_disjoint_record():
    rows = study.schedule("held")
    assert len(rows) == 16
    assert len({row["record_id"] for row in rows}) == 16
    assert {row["repeat"] for row in rows} == {0}
    assert {row["seed"] for row in rows} == set(range(202609132100, 202609132116))
    assert all(row["temperature"] == 0.5 and "arm" not in row for row in rows)
    training_ids = {
        row["group_id"] for row in study.read(study.TRAINING / "TRAIN_INPUTS.json")["episodes"]
    }
    assert not (training_ids & {row["record_id"] for row in rows})


def test_checkpoint_header_requires_exact_updated_checkpoint(tmp_path):
    output = tmp_path / "attempt"
    checkpoint_dir = output / "checkpoint-0001"
    result = {
        "status": "UPDATED",
        "optimizer_steps": 1,
        "checkpoint": str(checkpoint_dir),
        "state_sha256": "a",
        "step_commit_sha256": "b",
    }
    checkpoint.validate_result_header(result, output)
    result["optimizer_steps"] = 0
    with pytest.raises(ValueError, match="one-update"):
        checkpoint.validate_result_header(result, output)


def test_zero_adapter_is_exact_and_binding_changes_only_root(tmp_path, monkeypatch):
    import torch
    from safetensors.torch import save_file

    source = tmp_path / "checkpoint"
    zero = tmp_path / "zero"
    source.mkdir()
    (source / "adapter_config.json").write_text(
        json.dumps({"bias": "none", "lora_dropout": 0.0, "r": 8, "lora_alpha": 16})
    )
    save_file(
        {
            "base_model.a.lora_A.weight": torch.ones(2, 3),
            "base_model.a.lora_B.weight": torch.ones(4, 2),
        },
        source / "adapter_model.safetensors",
    )
    receipt = checkpoint.materialize_zero_adapter(source, zero)
    checkpoint.validate_zero_adapter(zero, receipt)
    assert receipt["all_tensors_zero"] and receipt["tensors"] == 2

    fake = {
        "zero_adapter": {**receipt, "path": str(zero)},
        "training": {
            "checkpoint": str(source),
            "adapter_model_sha256": study.sha(source / "adapter_model.safetensors"),
            "adapter_config_sha256": study.sha(source / "adapter_config.json"),
        },
    }
    fake_receipt = tmp_path / "CHECKPOINT_READY.json"
    fake_receipt.write_text("{}")
    monkeypatch.setattr(checkpoint, "RECEIPT", fake_receipt)
    monkeypatch.setattr(checkpoint, "verify_checkpoint", lambda: fake)
    base = checkpoint.binding("base")
    updated = checkpoint.binding("updated")
    assert base["role_map"]["children"] == updated["role_map"]["children"]
    assert base["fixed_child"] == updated["fixed_child"] == study.BASE_ALIAS
    assert base["role_map"]["root"] == study.BASE_ALIAS
    assert updated["role_map"]["root"] == study.UPDATED_ALIAS


def test_result_summary_keeps_raw_exact_official_and_shaped_separate():
    rows = []
    for score, exact, available in ((0.91, False, True), (1.0, True, True), (0.2, False, True), (0.0, False, False)):
        rows.append(
            {
                "derived": {
                    "scientifically_available": available,
                    "raw_exact": exact,
                    "reward": score,
                }
            }
        )
    result = collect.shaped_summary(rows)
    assert result == {
        "raw_exact": 1,
        "raw_similarity_at_least_0_90": 2,
        "shaped_reward_sum": 1.5,
        "scientifically_available": 3,
        "infrastructure_unavailable": 1,
        "newline_or_output_repair": None,
    }
