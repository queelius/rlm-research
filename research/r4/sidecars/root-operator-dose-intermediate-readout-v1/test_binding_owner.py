import json
from pathlib import Path

import id_owner as owner
import id_study as s


EXPECTED = {
    "sft6": (6, "efe7efc1b7b1ed642d04a1bee0ea4a3d5a6c1ac5b9575f89ad22d3e3ac2518cb", "fa6c9a8b53cfc541b626779f08dcbbb4b7337eb96ad7e4aea4fbbcff949476bc"),
    "sft12": (12, "1f1a201eb5f3f9a2322a7159c7c7821d50a77ac7e422ad9238beabe752b0b1c9", "93352c753e4548e57ca7906cae552b69fe1988e280076228c56bd5f99124349e"),
    "sft18": (18, "bc3387d239d17af9e24dedd5592c81e6c5569994ba728d606394be246de13725", "a755108693d8ea0f8d67c19ffc2550b658781545fb5535d1eef1d56b67818e61"),
    "sft24": (24, "94022838a64a530e1abc8daf6cd43502d8aec7d549b6bfec10dd4928b0ca9006", "75b3138884cf526503bba311dae932158b7305a4958b478f73d286ad3a755171"),
}


def test_selected_checkpoints_are_exact_fixed_lineage_not_best_selection():
    for policy, (step, adapter, state) in EXPECTED.items():
        selected = s.selected(policy)
        assert (selected["step"], selected["adapter_sha256"], selected["state_sha256"]) == (step, adapter, state)
        assert selected["rule"] == "fixed checkpoint ordinal; no performance selection"
        binding = s.binding(policy, selected)
        assert binding["campaign_policy"]["step"] == step
        assert binding["campaign_policy"]["adapter_sha256"] == adapter
        assert binding["operator_dose_intermediate"]["policy"] == policy
        assert binding["operator_dose"]["final_rule"] == "fixed checkpoints 6/12/18/24; no performance selection"


def test_budget_reserves_four_750_second_phases_and_150_second_harvest():
    budget = owner.budget(1000.0)
    assert budget == {"started": 1000.0, "work": 4150.0, "owned": 4270.0, "outer": 4300.0,
                      "phase_ends": [1750.0, 2500.0, 3250.0, 4000.0], "harvest_seconds": 150}
    assert owner.stage_caps() == {"startup": 180, "probe": 60, "free": 480, "cleanup_reserve": 30}


def test_slot_taxonomy_distinguishes_attempted_failure_from_unstarted(tmp_path):
    untouched = tmp_path / "untouched"
    assert owner.classify_slot(untouched) == "unstarted"
    attempted = tmp_path / "attempted"; (attempted / "physical").mkdir(parents=True)
    (attempted / "physical/0001.json").write_text("{}")
    (attempted / "FAILURE.json").write_text("{}")
    assert owner.classify_slot(attempted) == "attempted_failure_no_result"
    unavailable = tmp_path / "unavailable"; unavailable.mkdir()
    (unavailable / "RESULT.json").write_text(json.dumps({"available": False}))
    assert owner.classify_slot(unavailable) == "attempted_no_native_final"
    available = tmp_path / "available"; available.mkdir()
    (available / "RESULT.json").write_text(json.dumps({"available": True}))
    assert owner.classify_slot(available) == "native_final"


def test_collector_argv_uses_rotated_16_row_plan_and_exact_destination(tmp_path):
    stage = tmp_path / "stage"; destination = tmp_path / "out"
    argv = owner.collector_argv("sft18", stage, destination, 1234.5)
    assert argv[-4:] == ["--output", str(destination), "--deadline", "1234.5"]
    assert argv[argv.index("--plan") + 1] == "FREE_PLAN_sft18.json"
    assert argv[argv.index("--stop") + 1] == "16"
