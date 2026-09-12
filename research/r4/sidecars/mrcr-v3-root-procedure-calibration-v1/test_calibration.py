"""Focused CPU contracts for the calibration-only MRCR owner."""

import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent


def test_frozen_rows_prompt_and_plan_have_no_host_answer_leakage():
    import study

    rows = study.selected_rows()
    assert len(rows) == 8
    assert len({row["context_sha256"] for row in rows}) == 1
    assert {row["quartile"] for row in rows} == {0, 1, 2, 3}
    assert {row["requested_ordinal"] for row in rows} == {0, 1}
    for row in rows:
        prompt = study.root_prompt(row["question"])
        assert row["question"] in prompt
        assert row["answer"] not in prompt
        assert "host" not in prompt.lower()
        assert "parser" not in prompt.lower()
        assert "/context.txt" in prompt
    plan = study.plan()
    assert len(plan) == 32
    assert {row["seed"] for row in plan} == set(study.SEEDS)
    assert all(sum(item["row_id"] == row["row_id"] for item in plan) == 4 for row in rows)


def test_official_metric_and_diagnostics_preserve_rfind_behavior():
    import study

    target = "abcdefghijklThe exact body."
    strict = study.score_terminal(target, target, "completed")
    late = study.score_terminal("preamble abcdefghijklThe exact body.", target, "completed")
    absent = study.score_terminal("The exact body.", target, "completed")
    partial = study.score_terminal("abcdefghijklThe wrong body.", target, "completed")
    assert strict["official_score"] == 1.0 and strict["strict_prefix"] is True
    assert late["official_score"] == 1.0 and late["strict_prefix"] is False
    assert absent["official_score"] == 0.0 and absent["hash_present"] is False
    assert 0.0 < partial["content_similarity"] < 1.0
    assert study.score_terminal(target, target, "deadline_censored")["official_score"] is None


def test_actual_taskset_and_model_context_preserve_runtime_contract(tmp_path):
    import collect
    import study

    prepared = study.prepare_inputs(tmp_path)
    environment = collect.environment(tmp_path)
    tasks = list(environment.taskset)
    assert len(tasks) == 32
    assert {task.data.name for task in tasks} == {row["id"] for row in study.plan()}
    config = prepared["environment"]
    assert config["agent"]["max_turns"] == 6
    assert config["agent"]["harness"]["max_depth"] == 1
    endpoint = {
        "host": "127.0.0.1", "port": 1, "model_alias": study.MODEL_ALIAS,
        "api_key_env": "CPU_ONLY_KEY", "base_model": {"path": str(study.MODEL)},
        "adapter": None,
    }
    context = collect.model_context(endpoint, study.plan()[0])
    assert context.model == study.MODEL_ALIAS
    sampling = context.sampling.model_dump(mode="json")
    assert sampling["temperature"] == 0.5
    assert sampling["top_p"] == 1.0
    assert sampling["max_tokens"] == 2048
    assert sampling["extra_body"]["top_k"] == -1
    assert sampling["extra_body"]["min_p"] == 0.0


def test_native_response_checkpoint_rejects_incomplete_token_evidence(tmp_path):
    import collect

    payload = {
        "model": "base", "finish_reason": "stop",
        "tokens": {"prompt_ids": [1, 2], "completion_ids": [3, 4],
                   "completion_logprobs": [-0.2, -0.3]},
    }
    normalized = collect.validate_native_response(payload)
    assert normalized["prompt_tokens"] == 2
    assert normalized["action_tokens"] == 2
    broken = json.loads(json.dumps(payload))
    broken["tokens"]["completion_logprobs"] = [-0.2]
    with pytest.raises(ValueError, match="logprob"):
        collect.validate_native_response(broken)


def test_no_adapter_binding_and_exact_owner_budget():
    import owner
    import study

    binding = study.binding()
    assert binding["adapter"] is None
    assert binding["checkpoint"]["alias"] == study.MODEL_ALIAS
    assert Path(binding["checkpoint"]["path"]).resolve() == study.MODEL.resolve()
    assert owner.OWNER_SECONDS == 900
    assert owner.SCIENCE_SECONDS < owner.OWNER_SECONDS

