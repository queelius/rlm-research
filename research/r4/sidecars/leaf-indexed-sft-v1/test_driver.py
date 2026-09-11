import importlib.util
import json
from pathlib import Path

import pytest
import torch

ROOT = Path(__file__).resolve().parent


def driver():
    assert (ROOT / "driver.py").exists(), (
        "indexed renderer/training integration not implemented"
    )
    spec = importlib.util.spec_from_file_location(
        "indexed_test_driver", ROOT / "driver.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_indexed_score_checks_exact_id_coverage_without_positional_repair():
    d = driver()
    row = {
        "representation": "indexed",
        "record_ids": ["q0001", "q0002"],
        "gold": ["entity", "location"],
    }
    good = d.score('{"q0002":"location","q0001":"entity"}', row)
    assert good["array_valid"] and good["correct"] == [True, True]
    wrong = d.score('{"q0001":"location","q0002":"entity"}', row)
    assert wrong["array_valid"] and wrong["correct"] == [False, False]
    for text in [
        '{"q0001":"entity"}',
        '{"q0001":"entity","q0002":"location","q0003":"entity"}',
        '{"q0001":"entity","q0001":"entity","q0002":"location"}',
        '["entity","location"]',
        '{"q0001":"ENTY","q0002":"location"}',
    ]:
        result = d.score(text, row)
        assert not result["array_valid"] and result["predictions"] == [None, None]
    row["representation"] = "anonymous"
    assert d.score('["entity","location"]', row)["correct"] == [True, True]
    assert not d.score('{"q0001":"entity","q0002":"location"}', row)["array_valid"]


def test_native_render_masks_prompt_retains_ids_terminator_and_no_array_instruction():
    d = driver()
    rows = [
        {"question": "Where is Paris?", "gold": "location", "group_id": "a"},
        {"question": "Who won?", "gold": "human being", "group_id": "b"},
    ]
    tokenizer = d.data.load_tokenizer()
    result = d.render(rows, tokenizer, "training", 1, 0, "indexed")
    assert json.loads(result["target"]) == {"q0001": "location", "q0002": "human being"}
    assert result["record_ids"] == ["q0001", "q0002"]
    assert result["input_ids"][: len(result["prompt_ids"])] == result["prompt_ids"]
    assert result["labels"][: len(result["prompt_ids"])] == [-100] * len(
        result["prompt_ids"]
    )
    assert tokenizer.eos_token_id in result["labels"][len(result["prompt_ids"]) :]
    assert "JSON object mapping every input ID" in result["messages"][1]["content"]
    assert "JSON array" not in result["messages"][1]["content"]
    with pytest.raises(ValueError, match="truncation"):
        d.data.causal_example([1], [1, 2, 3], max_length=2)


def test_group_order_and_allocation_are_exact_b_not_a_new_shuffle():
    d = driver()
    source = d.data.read_json(d.MIXED / "B/data.json")
    rows = d.data.load_partitions()["train"]
    batches = d.mixed.allocate(rows, (1, 5, 16, 64))
    assert [len(e) for e in batches] == [1621, 1620]
    for got, want in zip(batches, source["train"], strict=True):
        assert [r["group_id"] for b in got for r in b["records"]] == [
            g for b in want for g in b["group_ids"]
        ]
        assert [b["nominal_size"] for b in got] == [b["nominal_size"] for b in want]
        assert len({r["group_id"] for b in got for r in b["records"]}) == 5065


def tiny_model():
    from peft import LoraConfig, get_peft_model
    from transformers import Qwen3Config, Qwen3ForCausalLM

    torch.manual_seed(19)
    return get_peft_model(
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
        LoraConfig(
            r=2,
            target_modules=["q_proj", "v_proj"],
            task_type="CAUSAL_LM",
            lora_dropout=0,
        ),
    )


def test_actual_peft_step_mask_save_restore_preserves_adam_rng_and_frozen_base(
    tmp_path,
):
    d = driver()
    model = tiny_model()
    before = {n: p.detach().clone() for n, p in model.named_parameters()}
    opt = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad], lr=1e-4, weight_decay=0
    )
    rows = [
        {"input_ids": [1, 2, 3, 4], "labels": [-100, -100, 3, 4]},
        {"input_ids": [5, 6, 7], "labels": [-100, -100, 7]},
    ]
    metrics = d.mixed.supervised_step(model, opt, rows, 0)
    assert metrics["action_tokens"] == 3 and metrics["gradient_norm"] > 0
    assert all(
        torch.equal(before[n], p)
        for n, p in model.named_parameters()
        if not p.requires_grad
    )
    assert any(
        not torch.equal(before[n], p)
        for n, p in model.named_parameters()
        if p.requires_grad
    )
    state = {
        "identity": "tiny",
        "step": 1,
        "epoch": 1,
        "cursor": 0,
        "training_seconds": 0.1,
        "step_metrics": [],
    }
    checkpoint = d.mixed.old.save_checkpoint(model, opt, tmp_path, state)
    restored = d.mixed.old.checkpoint_state(checkpoint, "tiny", [16, 16])
    assert restored["step"] == 1
    from peft import PeftModel

    # Reload into an adapter-free base to avoid testing adapter stacking.
    fresh = tiny_model().unload()
    loaded = PeftModel.from_pretrained(fresh, checkpoint, is_trainable=True)
    left = {n: p for n, p in model.named_parameters() if p.requires_grad}
    right = {n: p for n, p in loaded.named_parameters() if p.requires_grad}
    assert left.keys() == right.keys()
    assert all(torch.equal(left[n], right[n]) for n in left)
    newopt = torch.optim.AdamW(right.values(), lr=1e-4, weight_decay=0)
    newopt.load_state_dict(torch.load(checkpoint / "optimizer.pt", weights_only=True))
    assert {int(v["step"]) for v in newopt.state.values()} == {1}
    rng = torch.load(checkpoint / "rng_state.pt", weights_only=True)
    torch.set_rng_state(rng["torch"])
    expected = torch.rand(3)
    torch.set_rng_state(rng["torch"])
    assert torch.equal(torch.rand(3), expected)
    d.mixed.supervised_step(loaded, newopt, rows, 0)
    assert {int(v["step"]) for v in newopt.state.values()} == {2}
    logits = torch.randn(1, 5, 8, requires_grad=True)
    loss, count = d.mixed.old.loss_sum(logits, torch.tensor([[-100, -100, -100, 2, 3]]))
    loss.backward()
    assert count == 2 and logits.grad[:, :2].abs().sum() == 0


def test_owned_evaluator_separates_contracts_and_binds_physical_inputs(tmp_path):
    from types import SimpleNamespace

    d = driver()

    class Model:
        device = "cpu"
        generation_config = SimpleNamespace(eos_token_id=1)

        def eval(self):
            pass

        def gradient_checkpointing_disable(self):
            pass

        def generate(self, **kwargs):
            assert kwargs["max_new_tokens"] == 3072 and kwargs["do_sample"] is False
            assert kwargs["input_ids"].tolist() == [[10, 11], [0, 12]]
            return torch.cat(
                [kwargs["input_ids"], torch.tensor([[2, 1], [3, 1]])], dim=1
            )

    class Tokenizer:
        pad_token_id = 0

        def decode(self, ids, **kwargs):
            return {2: '["entity"]', 3: '{"q0001":"entity"}'}[ids[0]]

    # The tiny file represents only the evaluator's identity boundary, not model weights.
    adapter = tmp_path / "adapter"
    adapter.mkdir()
    (adapter / "adapter_model.safetensors").write_bytes(b"evaluator-checkpoint-fixture")
    rows = [
        {
            "id": "anon",
            "representation": "anonymous",
            "record_ids": ["q0001"],
            "gold": ["entity"],
            "group_ids": ["g"],
            "prompt_ids": [10, 11],
        },
        {
            "id": "map",
            "representation": "indexed",
            "record_ids": ["q0001"],
            "gold": ["entity"],
            "group_ids": ["g"],
            "prompt_ids": [12],
        },
    ]
    result = d.evaluate_long(
        Model(), Tokenizer(), rows, tmp_path / "eval", "prepared-id", adapter
    )
    assert result["unique_groups"] == 1
    assert result["by_representation"]["anonymous"]["accuracy"] == 1
    assert result["by_representation"]["indexed"]["accuracy"] == 1
    saved = json.loads((tmp_path / "eval/map.json").read_text())
    assert saved["prompt_token_ids"] == [12] and saved["score"]["correct"] == [True]
    assert (
        d.evaluate_long(
            Model(), Tokenizer(), rows, tmp_path / "eval", "prepared-id", adapter
        )
        == result
    )
    with pytest.raises(ValueError, match="binding changed"):
        d.evaluate_rows(
            Model(),
            Tokenizer(),
            rows,
            tmp_path / "eval",
            "prepared-id",
            adapter,
            max_new_tokens=256,
        )
