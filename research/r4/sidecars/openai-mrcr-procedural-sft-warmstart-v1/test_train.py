import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load_training():
    spec = importlib.util.spec_from_file_location("procedural_sft_training_tested", ROOT / "training.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_corpus_contract_and_fixed_recipe_are_exact():
    training = load_training()
    corpus = json.loads((ROOT / "TEACHER_CORPUS_V2.json").read_text())
    summary = training.validate_corpus(corpus)
    assert summary == {
        "episodes": 32,
        "root_action_target_tokens": 6696,
        "terminal_target_tokens": 11365,
        "maximum_sequence_tokens": 2298,
    }
    assert len(
        {
            turn["id"]
            for episode in corpus["episodes"]
            for turn in episode["turns"]
        }
    ) == 64
    recipe = training.recipe()
    assert recipe["updates"] == 4
    assert recipe["terminal_weight"] == 0.1
    assert recipe["seed"] == 2026091401 < 2**32
    assert recipe["selection"] == "fixed checkpoint-0004; no evaluation selection"


def test_actual_reused_loss_has_action_mass_one_terminal_mass_point_one():
    training = load_training()
    import torch
    from peft import LoraConfig, get_peft_model
    from transformers import GPT2Config, GPT2LMHeadModel

    torch.manual_seed(7)
    model = get_peft_model(
        GPT2LMHeadModel(
            GPT2Config(
                vocab_size=32,
                n_positions=32,
                n_embd=16,
                n_layer=1,
                n_head=2,
                resid_pdrop=0.0,
                embd_pdrop=0.0,
                attn_pdrop=0.0,
            )
        ),
        LoraConfig(
            r=2,
            lora_alpha=4,
            target_modules=["c_attn"],
            lora_dropout=0.0,
            task_type="CAUSAL_LM",
        ),
    )
    episodes = []
    for episode in range(2):
        turns = []
        for kind, ids, prompt in [
            ("root_action", [1, 2, 3, 4], 2),
            ("terminal", [1, 2, 5, 6, 7], 2),
        ]:
            turns.append(
                {
                    "kind": kind,
                    "id": f"{episode}-{kind}",
                    "input_ids": ids,
                    "prompt_length": prompt,
                    "labels": [-100] * prompt + ids[prompt:],
                    "loss_mask": [0] * prompt + [1] * (len(ids) - prompt),
                }
            )
        episodes.append({"episode_id": str(episode), "turns": turns})
    optimizer = torch.optim.AdamW(
        [parameter for parameter in model.parameters() if parameter.requires_grad],
        lr=1e-4,
        weight_decay=0.0,
    )
    metric = training.learning().update(
        model, optimizer, episodes, "cpu", terminal_weight=0.1
    )
    assert metric["episodes"] == 2
    assert metric["root_turns"] == 4
    assert abs(metric["mass_sum"] - 1.1) < 1e-6
    assert metric["action_target_tokens"] == 4
    assert metric["terminal_target_tokens"] == 6
    assert {int(state["step"]) for state in optimizer.state.values()} == {1}


def test_checkpoint_contract_accepts_only_completed_fixed_step_four(tmp_path):
    training = load_training()
    for step in range(1, 5):
        checkpoint = tmp_path / f"checkpoint-{step:04d}"
        checkpoint.mkdir()
        for name in [
            "adapter_model.safetensors",
            "adapter_config.json",
            "optimizer.pt",
            "rng.pt",
            "EVAL_BINDING.json",
        ]:
            (checkpoint / name).write_bytes(f"{step}-{name}".encode())
        state = {
            "schema": "openai-mrcr-procedural-sft-state-v1",
            "step": step,
            "optimizer_steps": step,
            "selection": "fixed checkpoint-0004; no evaluation selection",
        }
        (checkpoint / "state.json").write_text(json.dumps(state))
        training.commit_checkpoint(checkpoint, state)
    result = training.result_for(tmp_path)
    assert result["status"] == "COMPLETED_FOUR_UPDATES"
    assert result["primary_checkpoint"] == str(tmp_path / "checkpoint-0004")
    assert result["evaluation_binding"] == str(
        tmp_path / "checkpoint-0004/EVAL_BINDING.json"
    )
    (tmp_path / "checkpoint-0004/STEP_COMMIT.json").unlink()
    try:
        training.result_for(tmp_path)
    except ValueError as error:
        assert "checkpoint-0004" in str(error)
    else:
        raise AssertionError("missing final commit was accepted")
