"""Regression for the real scorer namespace and vector-valued diagnostic fields."""

import copy
import importlib.util
from pathlib import Path

import torch
from transformers import Qwen3Config, Qwen3ForCausalLM


def load_study(path):
    spec = importlib.util.spec_from_file_location("vector_credit_v2_test_study", path)
    study = importlib.util.module_from_spec(spec); spec.loader.exec_module(study)
    return study


def test_actual_scorer_all_logprobs_and_diagnostics():
    study = load_study(Path(__file__).resolve().parents[1] / "b05-vector-credit-local-v2/study.py")
    trainer = study.load("vector_credit_v2_test_trainer", study.SHARED / "trainer.py")
    core, _credit = trainer.dependencies(study)
    model = Qwen3ForCausalLM(Qwen3Config(vocab_size=32, hidden_size=16, intermediate_size=32,
        num_hidden_layers=1, num_attention_heads=2, num_key_value_heads=1, head_dim=8,
        attention_dropout=0.0))
    turn = {"prompt_ids": [1, 2, 3], "action_ids": [4, 5], "input_ids": [1, 2, 3, 4, 5],
        "labels": [-100, -100, -100, 4, 5], "loss_mask": [0, 0, 0, 1, 1],
        "old_logprobs": [-1.0, -1.0]}
    rows = [{"episode_id": f"tiny-{index}", "group_id": "tiny", "root_turns": [copy.deepcopy(turn)],
             "reward": [1, 0], "advantage": [0.5, -0.5]} for index in range(4)]
    baseline = core.scorer._all_logprobs(model, rows)
    for row, values in zip(rows, baseline, strict=True): row["root_turns"][0]["old_logprobs"] = values[0]
    weights, diagnostics = core.scorer._build_token_diagnostics(rows, baseline)
    assert len(weights) == 4 and diagnostics["episodes"] == 4
    assert diagnostics["episodes_detail"][0]["reward"] == [1, 0]
    assert diagnostics["episodes_detail"][0]["advantage"] == [0.5, -0.5]
    assert diagnostics["cap"] == 2.0 and diagnostics["capped_tokens"] == 0


def test_study_exports_entire_scorer_contract():
    study = load_study(Path(__file__).resolve().parents[1] / "b05-vector-credit-local-v2/study.py")
    names = {"BASE", "BRANCHES", "CAP_SECONDS", "DENOMINATOR", "INPUTS", "NP_SEED", "OUTPUT",
             "SEED", "TEMPERATURE", "TOKEN_TIS_CAP", "load_sealed_inputs", "positions_and_targets",
             "sha", "write_x"}
    assert not (names - set(vars(study)))
    assert study.TEMPERATURE == 0.5
