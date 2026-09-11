import importlib
import json
import os
from pathlib import Path
import subprocess
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "root-question-sensitive-terminal-rlvr-recovery-v2"


def test_exact_lr_only_recipe_and_distinct_namespace():
    study = importlib.import_module("lr_study")
    recipe = study.read(ROOT / "RECIPE.json")
    source = study.read(SOURCE / "RECIPE.json")
    changed = {key for key in recipe if recipe.get(key) != source.get(key)}
    assert changed == {"learning_rate", "schema", "training_wall_cap_seconds"}
    assert recipe["learning_rate"] == 1e-5
    assert recipe["training_wall_cap_seconds"] == 1800
    assert study.ROOT_START_SHA == "4d8287537a9ff3d8e33bc0314f64315dee06e71b801257b389dab8b667e27aca"
    assert study.CHILD_SHA == "c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3"
    assert study.CAMPAIGN_ID != study.source_study.CAMPAIGN_ID


def test_optimizer_group_guard_rejects_restored_high_lr():
    train = importlib.import_module("lr_train")
    good = SimpleNamespace(param_groups=[{"lr": 1e-5, "weight_decay": 0.0,
                                          "betas": (0.9, 0.999), "eps": 1e-8}])
    assert train.assert_optimizer_recipe(good, {"learning_rate": 1e-5,
                                                "weight_decay": 0.0})
    bad = SimpleNamespace(param_groups=[{"lr": 5e-5, "weight_decay": 0.0,
                                         "betas": (0.9, 0.999), "eps": 1e-8}])
    with pytest.raises(ValueError, match="learning rate"):
        train.assert_optimizer_recipe(bad, {"learning_rate": 1e-5,
                                            "weight_decay": 0.0})


def test_fixed_inputs_and_namespace_map():
    study = importlib.import_module("lr_study")
    receipt = study.read(ROOT / "inputs/SOURCE_MAP.json")
    for name in ("PLANS.json", "GROUPS.json", "PUBLIC.json", "HOST_GOLD.json",
                 "NATIVE_TEMPLATE.json", "PROMPTS_ACCURATE.json", "PROVENANCE.json"):
        assert study.sha(ROOT / "inputs" / name) == study.sha(SOURCE / "inputs" / name)
    assert receipt["scientific_inputs_byte_equal"] is True
    assert receipt["task_hashes_preserved"] is False
    assert receipt["namespace_only_task_hash_changes"] is True
    assert receipt["namespace_only_generation_changes"] is True
    assert receipt["training_rows"] == 192 and receipt["readout_rows"] == 72
    assert len(receipt["task_hash_map"]) == 120


def test_budget_and_new_readout_inventory_only():
    owner = importlib.import_module("lr_owner")
    assert owner.budget(100.0) == {"started": 100.0, "training_end": 12100.0,
                                  "readout_end": 14800.0, "work": 14800.0,
                                  "owned": 15070.0,
                                  "outer": 15100.0}
    rows = owner.planned_inventory(ROOT / "outputs/fixture")
    assert len(rows) == 264
    assert sum(row["phase"] == "training" for row in rows) == 192
    assert sum(row["phase"] == "readout" for row in rows) == 72
    assert {row.get("arm") for row in rows if row["phase"] == "readout"} == {"lr1e5_last"}


def test_reporting_contract_includes_execution_semantics_and_sparse_disclosure():
    design = (ROOT / "DESIGN.md").read_text()
    assert "faithful+strict" in design
    assert "gold-zero" in design
    assert "sparse-head" in design
    assert "not bitwise" in design


def test_new_fixed_last_phase_uses_exact_frozen72():
    collect = importlib.import_module("terminal_collect")
    rows = collect.planned("readout-lr1e5_last")
    assert len(rows) == 72
    with pytest.raises(ValueError):
        collect.planned("readout-start")


def test_actual_training_and_final_binding_resolve_local_start(monkeypatch):
    """Exercise the lazy qualified binding seam used by both owner phases."""
    study = importlib.import_module("lr_study")
    collect = importlib.import_module("terminal_collect")
    # The prospective closure is deliberately unsealed during CPU qualification.
    # Bypass only that seal gate; binding_for and every lazy native dependency are real.
    binding_study = collect.binding_for.__globals__["s"]
    monkeypatch.setattr(binding_study, "verify_prepared", binding_study.verify_campaign)
    policy = study.fixed_start()
    training = collect.binding_for(policy)
    final = collect.binding_for(policy)
    for binding in (training, final):
        assert binding["starting_binding"]["path"] == str(ROOT / "START.json")
        assert binding["starting_binding"]["sha256"] == study.sha(ROOT / "START.json")
        assert binding["campaign_policy"] == policy
        assert binding["starting_binding"]["policy0"] == policy


def test_campaign_closure_is_unsealed_and_binds_reused_baseline():
    study = importlib.import_module("lr_study")
    prepare = importlib.import_module("lr_prepare_campaign")
    built = prepare.build()
    assert built == study.read(ROOT / "CAMPAIGN.json")
    assert built["intervention"] == {"field": "learning_rate", "from": 5e-5,
                                     "to": 1e-5}
    assert built["readout"] == {"new_calls": 72, "policy": "lr1e5_last",
                                "reused_start_calls": 72}
    assert built["baseline"]["manifest_sha256"] == (
        "81774d0e3807deb1b2991ee64c5092c665cf3e93e03255f24f0a3ff7b34a3bd4"
    )
    assert built["sparse_numerics_not_bitwise_dense"] is True
    assert not (ROOT / "READY.json").exists()


def test_fresh_cli_namespace_and_entrypoints():
    study = importlib.import_module("lr_study")
    environment = {**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"}
    probe = subprocess.run(
        [str(study.NATIVE), "-c",
         "import json,lr_study,lr_owner,lr_prepare_campaign;"
         "print(json.dumps({'root':str(lr_study.ROOT),'owner':lr_owner.__file__,"
         "'prepare':lr_prepare_campaign.__file__}))"],
        cwd=ROOT, env=environment, text=True, capture_output=True, check=True, timeout=30,
    )
    value = json.loads(probe.stdout)
    assert value["root"] == str(ROOT)
    assert Path(value["owner"]).resolve() == ROOT / "lr_owner.py"
    assert Path(value["prepare"]).resolve() == ROOT / "lr_prepare_campaign.py"
    for python, script in ((study.NATIVE, "terminal_collect.py"),
                           (study.TRAIN, "lr_train.py")):
        result = subprocess.run([str(python), str(ROOT / script), "--help"], cwd=ROOT,
                                env=environment, text=True, capture_output=True, timeout=30)
        assert result.returncode == 0, (script, result.stdout, result.stderr)


def test_lr_policy_namespace_allows_fixed_cursor_noops(tmp_path):
    study = importlib.import_module("lr_study")
    train = importlib.import_module("lr_train")
    committed = study.ATTEMPT / "window-03/training/checkpoint-2"
    policy = {"step": 2, "path": str(committed)}
    assert train.check_policy_namespace(policy, {"candidate_window": 5})
    with pytest.raises(ValueError, match="foreign high-LR"):
        train.check_policy_namespace({"step": 2, "path": str(tmp_path / "checkpoint-2")},
                                     {"candidate_window": 5})


def test_material_cpu_qualifications_are_real_and_gpu_free():
    study = importlib.import_module("lr_study")
    transport = study.read(ROOT / "qualification-transport1/RESULT.json")
    adam = study.read(ROOT / "qualification-adam/RESULT.json")
    assert transport["provider_calls"] == transport["completed_slots"] == 1
    assert transport["actual_model_calls"] == transport["gpu_calls"] == 0
    assert transport["first_transport_prefix_token_counts"] == [1079]
    assert adam["real_torch_adamw"] is True
    assert (adam["restored_step"], adam["advanced_step"]) == (1, 2)
    assert adam["wrong_5e5_rejected"] is True and adam["gpu_calls"] == 0
