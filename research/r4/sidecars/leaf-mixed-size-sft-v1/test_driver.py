import importlib.util
from pathlib import Path

import pytest
import torch

ROOT = Path(__file__).resolve().parent


def driver():
    assert (ROOT / "driver.py").exists(), "mixed curriculum driver missing"
    spec = importlib.util.spec_from_file_location("mixed_test_driver", ROOT / "driver.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize("sizes", [(1, 5, 16, 32), (1, 5, 16, 64)])
def test_every_group_once_each_epoch_with_balanced_record_quotas(sizes):
    mod = driver()
    rows = [{"group_id": f"{i:06d}"} for i in range(5065)]
    epochs = mod.allocate(rows, sizes)
    assert epochs == mod.allocate(list(reversed(rows)), sizes)
    for epoch in epochs:
        ids = [r["group_id"] for batch in epoch for r in batch["records"]]
        assert len(ids) == len(set(ids)) == 5065
        counts = [
            sum(len(b["records"]) for b in epoch if b["nominal_size"] == size) for size in sizes
        ]
        assert sorted(counts) == [1266, 1266, 1266, 1267]
        assert all(1 <= len(b["records"]) <= b["nominal_size"] for b in epoch)
    assert epochs[0] != epochs[1]


def test_curricula_share_group_bucket_assignments_and_final_epoch_selection():
    mod = driver()
    rows = [{"group_id": str(i)} for i in range(101)]
    left, right = mod.allocate(rows, (1, 5, 16, 32)), mod.allocate(rows, (1, 5, 16, 64))
    for a, b in zip(left, right, strict=True):
        for bucket in range(4):
            assert {r["group_id"] for x in a if x["bucket"] == bucket for r in x["records"]} == {
                r["group_id"] for x in b if x["bucket"] == bucket for r in x["records"]
            }
    selected = mod.final_selection(
        [{"epoch": 1, "validation": {"accuracy": 1}}, {"epoch": 2, "validation": {"accuracy": 0}}]
    )
    assert selected["epoch"] == 2


def test_supervised_loss_masks_context_and_normalizes_all_target_tokens():
    mod = driver()
    logits = torch.randn(2, 5, 9, requires_grad=True)
    labels = torch.tensor([[-100, -100, 2, 3, 4], [-100, -100, -100, 5, -100]])
    loss, count = mod.old.loss_sum(logits, labels)
    assert count == 4
    (loss / count).backward()
    assert torch.equal(logits.grad[:, 0], torch.zeros_like(logits.grad[:, 0]))
    assert logits.grad.abs().sum() > 0


def test_actual_tiny_peft_mixed_length_step_and_native64_position_metrics():
    from peft import LoraConfig, get_peft_model
    from transformers import Qwen3Config, Qwen3ForCausalLM

    mod = driver()
    torch.manual_seed(19)
    model = get_peft_model(
        Qwen3ForCausalLM(
            Qwen3Config(
                vocab_size=16,
                hidden_size=16,
                intermediate_size=32,
                num_hidden_layers=1,
                num_attention_heads=2,
                num_key_value_heads=2,
                head_dim=8,
            )
        ),
        LoraConfig(r=2, target_modules=["q_proj", "v_proj"], task_type="CAUSAL_LM", lora_dropout=0),
    )
    before = {n: p.detach().clone() for n, p in model.named_parameters()}
    optimizer = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad], lr=1e-4, weight_decay=0
    )
    rows = [
        {"input_ids": [1, 2, 3, 4], "labels": [-100, -100, 3, 4]},
        {"input_ids": [5, 6, 7], "labels": [-100, -100, 7]},
    ]
    metrics = mod.supervised_step(model, optimizer, rows, 0)
    assert metrics["action_tokens"] == 3 and metrics["gradient_norm"] > 0
    assert any(
        not torch.equal(before[n], p) for n, p in model.named_parameters() if p.requires_grad
    )
    assert all(
        torch.equal(before[n], p) for n, p in model.named_parameters() if not p.requires_grad
    )
    assert {int(v["step"]) for v in optimizer.state.values()} == {1}
    scores = mod.position_metrics(
        [
            {
                "gold": ["entity"] * 64,
                "score": {
                    "array_valid": True,
                    "predictions": ["entity"] * 16 + ["location"] * 48,
                    "correct": [True] * 16 + [False] * 48,
                },
            }
        ]
    )
    assert [r["correct"] for r in scores] == [16, 0, 0, 0]
