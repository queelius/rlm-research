import importlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def test_frozen_selection_and_three_policy_inventory():
    study = importlib.import_module("study")
    provenance = study.read(ROOT / "inputs/PROVENANCE.json")
    plan = study.read(ROOT / "inputs/FREE_PLAN.json")
    groups = study.read(ROOT / "inputs/GROUPS.json")
    assert (provenance["base_pool"], provenance["excluded"], provenance["eligible"]) == (2000, 1819, 181)
    assert provenance["selection_before_gold"] is True
    assert len(provenance["selected_group_sequence"]) == 128
    assert len(groups) == 8 and all(len(group["group_ids"]) == 16 for group in groups)
    assert len(plan) == 72
    assert {row["family"] for row in plan} == {"T1", "T2", "M1", "M2", "J1", "J2", "P1", "P2", "P3"}
    assert all(set(row["users"]) <= {"u4", "u5", "u6", "u7"} for row in plan)
    assert {row["threshold"] for row in plan if row["threshold"] is not None} == {13, 25}
    original_path = str(study.ORIGINAL / "inputs/GROUPS.json")
    original_receipt = next(row for row in provenance["manifest_rows"]
                            if row["path"] == original_path)
    original_groups = {group_id for group in study.read(original_path)
                       for group_id in group["group_ids"]}
    assert original_receipt["positive_group_count"] == 320
    assert not set(provenance["selected_group_sequence"]) & original_groups


def test_exact_three_nonempty_bindings_and_fixed_child():
    study = importlib.import_module("study")
    expected = {"fixed24": "94022838a64a530e1abc8daf6cd43502d8aec7d549b6bfec10dd4928b0ca9006",
                "original_sft6": "4d8287537a9ff3d8e33bc0314f64315dee06e71b801257b389dab8b667e27aca",
                "new_corpus_sft6": "0fdd2c31a067405dabf61391d2b18c84c1206d4fbf88257f354733b0480f4f37"}
    for arm, sha in expected.items():
        binding = study.binding(arm)
        root = binding["models"][binding["role_map"]["root"]]
        child = binding["models"][binding["fixed_child"]]
        assert root["adapter_sha256"] == sha
        assert child["adapter_sha256"] == study.CHILD_SHA
        assert binding["fresh_input"]["arm"] == arm


def test_all_policy_tasks_have_identical_public_interface_and_seeds():
    study = importlib.import_module("study")
    rows = study.read(ROOT / "inputs/FREE_PLAN.json")
    public = {row["id"]: row for row in study.read(ROOT / "inputs/PUBLIC.json")}
    prompts = study.read(ROOT / "inputs/PROMPTS_ACCURATE.json")
    assert len(prompts) == 72
    for row in rows:
        context = public[row["context_id"]]
        assert prompts[row["id"]]["plain_query"] == row["question"]
        assert context["size"] == 16
        assert all(8 <= record["weight"] <= 15 for record in context["records"])
    evaluation = study.read(ROOT / "inputs/EVALUATION_PLAN.json")
    assert evaluation["planned"] == 216
    assert evaluation["policy_order"] == ["new_corpus_sft6", "original_sft6", "fixed24"]


def test_actual_nonempty_fake_transport_receipt_covers_all_bindings():
    value = json.loads((ROOT / "QUALIFICATION.json").read_text())
    assert value["gpu_calls"] == value["service_calls"] == 0
    assert value["provider_calls"] == 3
    assert value["arms"] == ["fixed24", "original_sft6", "new_corpus_sft6"]
    assert all(value["nonempty_binding_models"][arm] == 2 for arm in value["arms"])
    assert all(value["first_transport_prefix_tokens"][arm] > 0 for arm in value["arms"])
