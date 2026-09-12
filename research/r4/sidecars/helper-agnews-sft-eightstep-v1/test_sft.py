"""Actual tokenizer/data and one-step optimizer contracts for the AG SFT comparator."""

import importlib
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent


def modules():
    sys.path.insert(0, str(ROOT))
    try:
        for name in ("owner", "train_sft", "sft_study"):
            sys.modules.pop(name, None)
        return tuple(importlib.import_module(name) for name in ("sft_study", "train_sft", "owner"))
    finally:
        sys.path.remove(str(ROOT))


def test_actual_tokenizer_builds_exact_frozen_teacher_schedule():
    study, train, _ = modules()
    steps = study.teacher_schedule()
    assert len(steps) == 8 and all(len(rows) == 32 for rows in steps)
    assert sum(len(row["requested_ids"]) for rows in steps for row in rows) == 1024
    assert sum(row["supervised_tokens"] for rows in steps for row in rows) == 20591
    assert [sum(row["supervised_tokens"] for row in rows) for rows in steps] == [
        2583, 2579, 2589, 2553, 2584, 2571, 2579, 2553
    ]
    for rows in steps:
        assert len({row["context_id"] for row in rows}) == 32
        for row in rows:
            assert row["input_ids"][: row["prompt_tokens"]] == row["prompt_ids"]
            assert all(value == -100 for value in row["labels"][: row["prompt_tokens"]])
            assert row["labels"][row["prompt_tokens"] :] == row["input_ids"][row["prompt_tokens"] :]
            assert set(row["gold_map"].values()) <= {"World", "Sports", "Business", "Sci/Tech"}
            assert "AG News definitions" in row["request_text"]
            assert "TREC" not in row["request_text"]
    batch = train.collate(steps[0][:2], study.tokenizer().pad_token_id)
    assert batch["input_ids"].shape == batch["labels"].shape == batch["attention_mask"].shape


def test_optimizer_is_fresh_lr_and_rejects_wrong_step():
    torch = pytest.importorskip("torch")
    _, train, _ = modules()
    model = torch.nn.Module()
    model.lora_test = torch.nn.Parameter(torch.ones(2, dtype=torch.float32))
    optimizer = train.make_optimizer(model)
    assert optimizer.param_groups[0]["lr"] == 1e-5
    assert optimizer.param_groups[0]["weight_decay"] == 0
    train.validate_optimizer(model, optimizer, 0)
    model.lora_test.grad = torch.ones_like(model.lora_test)
    optimizer.step()
    train.validate_optimizer(model, optimizer, 1)
    with pytest.raises(ValueError, match="counter"):
        train.validate_optimizer(model, optimizer, 2)


def test_owner_and_training_import_same_local_study():
    study, train, owner = modules()
    assert train.study is study and owner.study is study
    assert callable(train.main) and callable(owner.execute)
    assert study.ATTEMPT == ROOT / "outputs/attempt-001"
    assert study.CAP == 900 and study.OUTER_CAP == 1000
