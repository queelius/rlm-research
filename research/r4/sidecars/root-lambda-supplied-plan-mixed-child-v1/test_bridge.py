import json
from pathlib import Path

import study as s


def without_alias(value):
    value = json.loads(json.dumps(value))
    value["model"] = "<policy>"
    return value


def test_science_plan_and_requests_equal_frozen_c32_except_policy_identity():
    prior = s.PRIOR_CEILING
    new_plan = s.read(s.ROOT / "inputs/PLAN.json")
    old_plan = s.read(prior / "inputs/PLAN.json")
    assert len(new_plan) == len(old_plan) == 40
    for new_row, old_row in zip(new_plan, old_plan, strict=True):
        assert new_row["model_policy"] == "mixed_sft24"
        assert new_row["id"] != old_row["id"]
        assert {k: v for k, v in new_row.items() if k not in ("id", "model_policy")} == {
            k: v for k, v in old_row.items() if k not in ("id", "model_policy")
        }
    new = s.read(s.ROOT / "inputs/REQUESTS.json")
    old = s.read(prior / "inputs/REQUESTS.json")
    assert not set(new) & set(old)
    assert all(without_alias(new[new_row["id"]]) == without_alias(old[old_row["id"]])
               for new_row, old_row in zip(new_plan, old_plan, strict=True))
    assert {body["model"] for body in new.values()} == {s.MIXED_ALIAS}
    new_prompts = s.read(s.ROOT / "inputs/PROMPT_IDS.json")
    old_prompts = s.read(prior / "inputs/PROMPT_IDS.json")
    assert all(new_prompts[new_row["id"]] == old_prompts[old_row["id"]]
               for new_row, old_row in zip(new_plan, old_plan, strict=True))


def test_exact_mixed_checkpoint_and_four_checkpoint_lineage():
    assert s.sha(s.MIXED / "adapter_model.safetensors") == s.MIXED_SHA
    for step in (6, 12, 18, 24):
        checkpoint = s.MIXED.parent / f"checkpoint-{step:04d}"
        state = s.read(checkpoint / "state.json")
        assert state["step"] == step and state["cursor"] == step * 4


def test_frozen_gate_uses_cluster_pair_sum_and_exact_delta():
    import analysis

    old = [{"cluster": i, "size": size, "absolute_error": 5, "strict": False,
            "final_available": True} for i in range(4) for size in (64, 256)]
    new = [{**row, "absolute_error": 4 if row["cluster"] < 3 else 6,
            "strict": index < 2} for index, row in enumerate(old)]
    gate = analysis.gate(old, new)
    assert gate["clusters_with_lower_sum_absolute_error"] == 3
    assert gate["exact_episode_gain"] == 2
    assert gate["no_availability_loss"] is True and gate["pass"] is True


def test_old_control_receipts_pin_every_physical_call_file():
    pins = s.read(s.ROOT / "inputs/OLD_CONTROL_PINS.json")
    assert pins["owner_terminal_sha256"] == s.sha(
        s.PRIOR_CEILING / "outputs/attempt-001/OWNER_TERMINAL.json"
    )
    assert pins["counts"] == {"REQUEST.json": 40, "RESPONSE.json": 40, "RESULT.json": 40}
    assert len(pins["physical_files_sha256"]) == 120
    assert all(s.sha(path) == digest for path, digest in pins["physical_files_sha256"].items())
