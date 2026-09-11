from collections import Counter

import warm_prepare as prepare
import warm_study as study


def test_exact_sft24_is_fresh_rl_step_zero():
    start = study.fixed_start()
    assert start["rl_step"] == 0 and start["source_sft_step"] == 24
    assert start["adapter_sha256"] == "94022838a64a530e1abc8daf6cd43502d8aec7d549b6bfec10dd4928b0ca9006"
    assert start["optimizer"] == "fresh AdamW; no SFT optimizer state loaded"


def test_frozen_eight_windows_and_paired_composition_readout():
    values = prepare.build_inputs()
    plans = values["PLANS.json"]
    training = [row for window in plans["training"].values() for row in window]
    assert len(plans["training"]) == 8 and len(training) == 192
    assert set(row["context_id"] for row in training) == {f"training-{i:02d}" for i in range(8)}
    assert len({row["id"] for row in training}) == 192
    assert [row["seed"] for row in training] == list(range(981731101, 981731293))
    groups = {(row["context_id"], row["family"]) for row in training}
    assert len(groups) == 24
    assert Counter((row["operator"], row["scope"]) for row in training) == {
        ("count", "all"): 32, ("count", "single"): 32,
        ("distinct", "single"): 32, ("distinct", "union"): 32,
        ("weight", "all"): 32, ("weight", "union"): 32,
    }
    truths = {values["HOST_GOLD.json"][context]["answers"][family]
              for context, family in groups}
    zero_groups = sum(values["HOST_GOLD.json"][context]["answers"][family] == 0
                      for context, family in groups)
    assert truths and zero_groups == 3
    assert len(plans["readout"]) == 48
    assert len(plans["evaluation"]) == 96
    assert Counter(row["policy"] for row in plans["evaluation"]) == {"unchanged": 48, "trained": 48}
    for coordinate in plans["readout"]:
        pair = [row for row in plans["evaluation"] if row["coordinate"]["id"] == coordinate["id"]]
        assert len(pair) == 2 and len({row["coordinate"]["seed"] for row in pair}) == 1


def test_current_training_questions_and_composition_bytes_are_authoritative():
    values = prepare.build_inputs()
    assert all("all records, regardless of which user owns them" in task["question"]
               for name, task in values["TASKS.json"].items()
               if name.startswith("training-") and task["scope"] == "all")
    source = prepare.composition_inputs()
    for row in values["PLANS.json"]["readout"]:
        assert row["source_coordinate_id"] in {item["id"] for item in source["FREE_PLAN.json"]}
        assert values["PROMPTS_ACCURATE.json"][row["id"]] == source["PROMPTS_ACCURATE.json"][row["source_coordinate_id"]]
    assert values["PROVENANCE.json"]["composition_outcomes_used"] is False


def test_seed_scan_is_integer_exact():
    assert prepare.seed_collisions({981731101}, [{"seed": 9817311010}, {"loss": .981731101},
                                                  {"seed": 981731101}]) == [981731101]
