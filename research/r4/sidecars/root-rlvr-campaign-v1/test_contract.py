import copy
import json

import pytest

import campaign_common as c


def test_generation_requires_exact_previous_step_root_and_child():
    policy = {"step": 1, "adapter_sha256": "root-one", "config_sha256": "config",
              "optimizer_sha256": "moments", "rng_sha256": "rng", "state_sha256": "state",
              "path": "/frozen/checkpoint-1"}
    generation = c.generation_identity("campaign", 2, policy, "plan")
    assert c.check_generation(generation, policy, 1) == 2
    with pytest.raises(ValueError, match="optimizer"):
        c.check_generation(generation, policy, 0)
    changed = {**policy, "adapter_sha256": "stale-root"}
    with pytest.raises(ValueError, match="policy"):
        c.check_generation(generation, changed, 1)
    changed_generation = copy.deepcopy(generation)
    changed_generation["fixed_child_sha256"] = "other-child"
    with pytest.raises(ValueError, match="identity|child"):
        c.check_generation(changed_generation, policy, 1)


def test_write_once_never_overwrites_and_commit_cursor_is_contiguous(tmp_path):
    target = tmp_path / "record.json"
    c.write_once(target, {"value": 1})
    with pytest.raises(FileExistsError):
        c.write_once(target, {"value": 2})
    assert json.loads(target.read_text()) == {"value": 1}
    assert c.contiguous_steps([]) == 0
    assert c.contiguous_steps([1, 2]) == 2
    with pytest.raises(ValueError, match="contiguous"):
        c.contiguous_steps([1, 3])
    with pytest.raises(ValueError, match="duplicate"):
        c.contiguous_steps([1, 1])


def test_seed_contract_matches_declared_hash_and_validation_reuses_coordinates():
    expected = int(c.digest(["root-rlvr-campaign-v1", 981260800, 3, "task", 2])[:8], 16) % (2**31 - 1)
    assert c.sample_seed(3, "task", 2) == expected
    assert c.sample_seed("validation", "task", 2) != expected


def test_completed_malformed_policy_zero_but_capture_failure_null():
    assert c.reward_admission(True, True, 0, True) == 0
    assert c.reward_admission(True, True, 1, False) is None
    assert c.reward_admission(False, False, 0, False) is None
