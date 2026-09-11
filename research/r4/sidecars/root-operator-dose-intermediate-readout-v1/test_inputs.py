from collections import Counter
import json
import pytest

import id_prepare as p


def test_build_inputs_freezes_new_ids_and_four_way_pairing():
    values = p.build_inputs()
    free = values["FREE_PLAN.json"]
    assert len(free) == 16
    assert [row["seed"] for row in free] == list(range(981681101, 981681117))
    assert free[0]["id"] == "beff5d53d116283963c1f1b7c6c9b62d0d04eeb72e320739fb1e358a10069524"
    assert free[-1]["id"] == "0b3ab4346ebdda8efdfd597525494b42432f695012feb56d0e0ba2cb68a02237"
    assert all(row["namespace"] == "operator-dose-intermediate-readout-v1" for row in free)
    assert all("source_coordinate_id" in row for row in free)
    evaluation = values["EVALUATION_PLAN.json"]
    assert evaluation["policy_order"] == ["sft18", "sft24", "sft12", "sft6"]
    assert len(evaluation["full"]) == 64
    assert Counter(row["policy"] for row in evaluation["full"]) == {"sft6": 16, "sft12": 16, "sft18": 16, "sft24": 16}
    assert all(len({row["coordinate"]["seed"] for row in evaluation["full"] if row["coordinate"]["id"] == coordinate["id"]}) == 1 for coordinate in free)
    assert len(evaluation["first_action"]) == 48
    assert Counter(row["policy"] for row in evaluation["first_action"]) == {"sft6": 12, "sft12": 12, "sft18": 12, "sft24": 12}
    assert values["ANALYSIS_PLAN.json"]["primary_planned_coordinate_denominator"] == 16
    assert values["ANALYSIS_PLAN.json"]["descriptive_equal_context_denominator"] == 12


def test_prompt_and_public_receipts_are_exact_source_bytes_or_selected_prefixes():
    values = p.build_inputs()
    source = p.source_inputs()
    assert values["PUBLIC.json"] == source["PUBLIC.json"]
    assert values["HOST_GOLD.json"] == source["HOST_GOLD.json"]
    for row in values["FREE_PLAN.json"]:
        assert values["PROMPTS_ACCURATE.json"][row["id"]] == source["PROMPTS_ACCURATE.json"][row["source_coordinate_id"]]
    assert values["SELECTION_RECEIPT.json"]["model_outcome_fields_used"] == []
    assert values["SELECTION_RECEIPT.json"]["label_use"] == "gold_is_zero only; explicit 13 nonzero/3 zero design stratification"
    assert values["BASELINES.json"]["planned"] == 16
    assert values["BASELINES.json"]["source_strata"]["root_new"]["n"] == 8
    assert values["BASELINES.json"]["source_strata"]["exposed_repeatability"]["n"] == 8
    assert set(values["BASELINES.json"]["context_clusters"]) == {row["context_id"] for row in values["FREE_PLAN.json"]}
    assert values["PROVENANCE.json"]["authoritative_new_selection"] == "SELECTION_RECEIPT.json"
    assert values["SOURCE_PROVENANCE.json"] == source["PROVENANCE.json"]


def test_seed_collision_scan_matches_exact_integer_fields_not_float_substrings():
    candidates = {981681001, 981681101, 981681201}
    catalog = [{"seed": 9816811010}, {"loss": -2.981681101}, {"seed": 981681101}]
    assert p.seed_collisions(candidates, catalog) == [981681101]


def test_write_inputs_is_complete_and_refuses_overwrite(tmp_path):
    target = tmp_path / "inputs"
    receipt = p.write_inputs(target)
    assert receipt["files"] == len(p.build_inputs())
    assert json.loads((target / "EVALUATION_PLAN.json").read_text())["planned_full"] == 64
    with pytest.raises(FileExistsError):
        p.write_inputs(target)
