import asyncio

import pytest

import warm_common as common
import warm_collect as collect
import warm_native as native
import warm_prepare as prepare
import warm_study as study


def test_fresh_rl_cursor_is_distinct_from_source_sft_step(monkeypatch):
    policy = study.fixed_start()
    plans = prepare.build_inputs()["PLANS.json"]["training"]
    monkeypatch.setattr(study, "candidate_plan", lambda window: plans[str(window)]
                        if 1 <= window <= 8 else (_ for _ in ()).throw(ValueError("fixed8")))
    generation = common.generation(1, policy)
    assert generation["round"] == 1 and generation["candidate_window"] == 1
    assert generation["previous_policy"]["step"] == 0
    assert generation["previous_policy"]["source_sft_step"] == 24
    no_op = common.transition(0, policy, 1, None)
    assert no_op["optimizer_steps"] == 0 and no_op["next_window"] == 2
    with pytest.raises(ValueError):
        common.generation(9, policy)


def test_current_clarified_native_prefix_is_gold_independent():
    values = prepare.build_inputs()
    row = values["PLANS.json"]["training"]["1"][0]
    context = next(item for item in values["PUBLIC.json"] if item["id"] == row["context_id"])
    question = values["TASKS.json"][row["task_name"]]["question"]
    first = native.make_task(context, question, 0, row["task_name"])
    changed = native.make_task(context, question, 999999, row["task_name"])
    assert native.first_prefix(first) == native.first_prefix(changed)
    assert native.first_prefix(first) == values["TASKS.json"][row["task_name"]]["first_prompt_token_ids"]
    assert first.data.prompt == changed.data.prompt
    assert "all records, regardless" in question if row["scope"] == "all" else True


def test_composition_readout_prefix_is_exact_source_bytes():
    values = prepare.build_inputs()
    row = values["PLANS.json"]["readout"][0]
    context = next(item for item in values["PUBLIC.json"] if item["id"] == row["context_id"])
    task = native.make_task(context, row["question"], 0, row["task_name"])
    assert native.first_prefix(task) == values["PROMPTS_ACCURATE.json"][row["id"]]["token_ids"]


def test_actual_start_binding_uses_exact_sft24_and_fresh_rl_cursor():
    binding = collect.binding_for(study.fixed_start())
    assert binding["campaign_policy"] == study.fixed_start()
    assert binding["starting_binding"]["kind"] == "exact_operator_sft24"
    assert binding["starting_binding"]["policy0"]["source_sft_step"] == 24
