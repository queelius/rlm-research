import importlib
from copy import deepcopy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent


def modules():
    assert (ROOT / "prepare.py").exists(), "independent seed preparation absent"
    return importlib.import_module("prepare"), importlib.import_module("campaign_common")


def test_fresh_initial_policy_has_no_inherited_optimizer_or_rng():
    _, c = modules()
    policy = c.original_policy()
    assert policy["step"] == 0 and policy["adapter_sha256"] == "857a7ce6907c759a8c1b478eb53029d3b700b81c3094d8edb3394e52def9fcb6"
    assert policy["optimizer_sha256"] is policy["rng_sha256"] is policy["state_sha256"] is None
    g = c.generation_identity("test", 1, policy, "plan")
    assert c.check_generation(g, policy, 0) == 1
    bad = deepcopy(g)
    bad["round"] = 4
    bad["generation_id"] = c.digest({k: v for k, v in bad.items() if k != "generation_id"})
    with pytest.raises(ValueError):
        c.check_generation(bad, policy, 0)


def test_all_fresh_rollout_seeds_and_matched_transfer_dispatch():
    prep, c = modules()
    old = c.read(c.OLD / "inputs/PLANS.json")
    plans = prep.make_plans(old)
    old_seeds = {r["seed"] for rs in old["training"].values() for r in rs} | {r["seed"] for k in ["validation", "transfer_original", "transfer_selected"] for r in old[k]}
    new_rows = [r for rs in plans["training"].values() for r in rs] + plans["validation"] + plans["transfer_original"]
    assert len(new_rows) == len({r["seed"] for r in new_rows}) == 288
    assert not {r["seed"] for r in new_rows} & old_seeds
    for a, b in zip(plans["transfer_original"], plans["transfer_selected"], strict=True):
        assert (a["task_name"], a["seed"], a["dispatch_order"]) == (b["task_name"], b["seed"], b["dispatch_order"])
    for round_id in map(str, range(1, 9)):
        assert len(plans["training"][round_id]) == 32
        fields = ["task_name", "source_id", "context_window_id", "context_sha256", "split", "repeat", "temperature", "client_path", "arm"]
        assert sorted(tuple(r[k] for k in fields) for r in plans["training"][round_id]) == sorted(tuple(r[k] for k in fields) for r in old["training"][round_id])


def test_recipe_preserves_math_and_only_changes_seed_caps_metadata():
    prep, c = modules()
    old = c.read(c.OLD / "RECIPE.json")
    new = prep.make_recipe(old)
    for k in old.keys() - {"training_seed", "caps", "declared_at_utc", "limitations"}:
        assert new[k] == old[k]
    assert new["training_seed"] == 981265001
    assert new["caps"]["global"] == 5880
    assert new["optimizer_steps"] == 8
