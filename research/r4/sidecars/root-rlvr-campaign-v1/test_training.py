from pathlib import Path

import pytest
import torch

import campaign_common as c
import campaign_train as trainer


def tiny():
    from peft import LoraConfig, get_peft_model
    from transformers import Qwen3Config, Qwen3ForCausalLM
    torch.manual_seed(981260800)
    model = get_peft_model(Qwen3ForCausalLM(Qwen3Config(vocab_size=16, hidden_size=16,
        intermediate_size=32, num_hidden_layers=1, num_attention_heads=2, num_key_value_heads=2, head_dim=8)),
        LoraConfig(r=2, target_modules=["q_proj", "v_proj"], task_type="CAUSAL_LM", lora_dropout=0))
    return model


def fresh_rows(model, weight_sha):
    model.eval()
    rows = []
    for index, tokens in enumerate(([1, 2, 3, 4], [5, 6, 7, 8])):
        with torch.no_grad():
            logits = model(input_ids=torch.tensor([tokens])).logits
            old = torch.log_softmax(logits[0, 2].float() / 0.5, -1)[tokens[3:]].tolist()
        turn = {"input_ids": tokens, "prompt_length": 3, "labels": [-100] * 3 + tokens[3:],
            "loss_mask": [0, 0, 0, 1], "old_logprobs": old, "role_depth": 0, "credited": True,
            "call_model": "root", "source_trace_id": "synthetic-cpu-only", "source_node_index": 2,
            "source_call_index": 0, "usage_input_tokens": 3, "usage_completion_tokens": 1,
            "sampling": {"temperature": .5, "top_p": 1, "top_k": -1, "min_p": 0, "max_tokens": 2048},
            "role_audit": {"depth": 0, "actual_alias": "root", "model_sha256": weight_sha}}
        rows.append({"episode_id": str(index), "advantage": [-1., 1.][index], "turns": [turn]})
    return rows


def test_two_fresh_generations_persist_adam_and_recover_without_double_step(tmp_path, monkeypatch):
    torch.set_num_threads(1)
    model, child = tiny(), tiny()
    for value in child.parameters():
        value.requires_grad_(False)
    child_before = {n: p.detach().clone() for n, p in child.named_parameters()}
    base_before = {n: p.detach().clone() for n, p in model.named_parameters() if not p.requires_grad}
    original = tmp_path / "original"
    model.save_pretrained(original, safe_serialization=True)
    policy = {"step": 0, "path": str(original), "adapter_sha256": c.file_hash(original / "adapter_model.safetensors"),
        "config_sha256": c.file_hash(original / "adapter_config.json"), "optimizer_sha256": None,
        "rng_sha256": None, "state_sha256": None}
    recipe = c.read(c.ROOT / "RECIPE.json")
    first = c.generation_identity("cpu-synthetic-not-research", 1, policy, "fresh-one")
    optimizer = trainer.make_optimizer(model, recipe)
    original_write = c.write_once
    def crash_after_checkpoint(path, value):
        if path.name == "RESULT.json":
            raise RuntimeError("simulated crash after checkpoint commit")
        return original_write(path, value)
    with monkeypatch.context() as local:
        local.setattr(c, "write_once", crash_after_checkpoint)
        with pytest.raises(RuntimeError, match="simulated crash"):
            trainer.update_generation(model, optimizer, fresh_rows(model, policy["adapter_sha256"]),
                tmp_path / "one", recipe, first, {"fixture": True})
    assert trainer.optimizer_step(optimizer) == 1
    # Simulated coordinator crash after checkpoint: discover state, not RESULT/cursor.
    recovered = c.checkpoint_policy(tmp_path / "one", first)
    assert recovered["step"] == 1
    assert not (tmp_path / "one/RESULT.json").exists()
    before_recovery = {n: p.detach().clone() for n, p in model.named_parameters()}
    again = trainer.update_generation(model, optimizer, [], tmp_path / "one", recipe, first, {"fixture": True})
    assert again["recovered_checkpoint"] is True
    assert trainer.optimizer_step(optimizer) == 1
    assert all(torch.equal(before_recovery[n], p) for n, p in model.named_parameters())
    with pytest.raises(ValueError, match="input binding"):
        trainer.update_generation(model, optimizer, [], tmp_path / "one", recipe, first, {"fixture": "different-group"})
    original_hash = c.file_hash
    with monkeypatch.context() as local:
        local.setattr(c, "file_hash", lambda path: "corrupt" if Path(path).name == "correction-capture.json" else original_hash(path))
        with pytest.raises(ValueError, match="authenticated file"):
            c.checkpoint_policy(tmp_path / "one", first)
    second = c.generation_identity("cpu-synthetic-not-research", 2, recovered, "fresh-two")
    from peft import PeftModel
    model = PeftModel.from_pretrained(tiny().unload(), recovered["path"], is_trainable=True,
                                      autocast_adapter_dtype=True)
    converter = c.load("cpu_resume_tensor_audit", c.pilot_math().CONVERTER_PATH)
    audit = converter.audit_loaded_adapter(model, Path(recovered["path"]))
    assert audit["missing_adapter_keys"] == 0
    new_optimizer = trainer.make_optimizer(model, recipe)
    trainer.restore_optimizer(new_optimizer, recovered, [n for n, p in model.named_parameters() if p.requires_grad])
    assert trainer.optimizer_step(new_optimizer) == 1
    with pytest.raises(ValueError, match="optimizer"):
        trainer.update_generation(model, trainer.make_optimizer(model, recipe), fresh_rows(model, recovered["adapter_sha256"]),
            tmp_path / "wrong", recipe, second, {})
    result2 = trainer.update_generation(model, new_optimizer, fresh_rows(model, recovered["adapter_sha256"]),
        tmp_path / "two", recipe, second, {"fixture": True})
    assert trainer.optimizer_step(new_optimizer) == 2
    assert result2["policy"]["step"] == 2
    assert all(p.grad is None and torch.equal(child_before[n], p) for n, p in child.named_parameters())
    assert all(torch.equal(base_before[n], p) for n, p in model.named_parameters() if not p.requires_grad)
    with pytest.raises(ValueError, match="stale|optimizer"):
        trainer.update_generation(model, new_optimizer, fresh_rows(model, recovered["adapter_sha256"]),
            tmp_path / "stale", recipe, first, {})


def test_child_turn_and_unmasked_observation_rejected_before_step(tmp_path):
    model = tiny()
    recipe = c.read(c.ROOT / "RECIPE.json")
    policy = {"step": 0, "path": "/synthetic", "adapter_sha256": "fixture", "config_sha256": "fixture",
              "optimizer_sha256": None, "rng_sha256": None, "state_sha256": None}
    generation = c.generation_identity("cpu-fixture", 1, policy, "plan")
    rows = fresh_rows(model, "fixture")
    rows[0]["turns"][0]["role_depth"] = 1
    with pytest.raises(ValueError, match="root"):
        trainer.update_generation(model, trainer.make_optimizer(model, recipe), rows, tmp_path / "child", recipe, generation, {})
    rows = fresh_rows(model, "fixture")
    rows[0]["turns"][0]["labels"][0] = 1
    with pytest.raises(ValueError, match="masked"):
        trainer.update_generation(model, trainer.make_optimizer(model, recipe), rows, tmp_path / "observation", recipe, generation, {})
