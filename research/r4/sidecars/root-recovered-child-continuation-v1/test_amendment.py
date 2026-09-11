"""Focused actual-data regression; fixtures are read-only and no model is contacted."""

import importlib
import copy
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parent / "root-rlvr-campaign-v1"))
OLD_ATTEMPT = ROOT.parent / "root-rlvr-campaign-v1/outputs/attempt-v2-001/round-04/collection/rollout"


def test_recovered_unsampled_child_failure_is_excluded_not_integrity_corruption():
    # Before implementation this executes the actual old exporter and fails on its
    # known integrity entry, not on a missing import or a mocked classification.
    module = importlib.import_module("native_amendment" if (ROOT / "native_amendment.py").exists() else "campaign_native")
    if module.__name__ == "native_amendment":
        rows, group, manifest = module.rebuild_export(OLD_ATTEMPT, amendment_id="cpu-qualification-before-freeze")
    else:
        rows, group, manifest = module.rebuild_export(OLD_ATTEMPT)
    assert manifest["integrity_failures"] == []
    assert sum(row["reward"] is not None for row in rows) == 29
    known = next(row for row in rows if row["episode_id"] == "ca1caf2a391bd5d3fa6e8573eae84ad9b941b3f6401c77a4f264f11efa5c1557")
    assert known["reward"] is None and known["admission_metadata"]["endpoint_reward"] == 0
    assert group is not None
    old_rows = json.loads((OLD_ATTEMPT.parent / "export/EPISODES.json").read_text())
    assert [{k: v for k, v in row.items() if k != "admission_metadata"} for row in rows] == old_rows
    assert manifest["endpoint_outcomes"] == {"0": 18, "1": 12, "unobservable": 2}
    assert {row["episode_id"] for row in rows if row["reward"] is not None} == {row["episode_id"] for row in old_rows if row["reward"] is not None}


def failed_fixture():
    import native_amendment as native
    episode = json.loads((OLD_ATTEMPT / "episodes/ca1caf2a391bd5d3fa6e8573eae84ad9b941b3f6401c77a4f264f11efa5c1557.json").read_text())
    call = next(c for c in episode["episode"]["traces"][0]["calls"] if c.get("error"))
    audit = json.loads((OLD_ATTEMPT.with_name("rollout-routing") / "role-audit/c7c199ca93d548cb85451bc9420fbd88-result.json").read_text())
    binding = json.loads((OLD_ATTEMPT / "SPEC.json").read_text())["role_binding"]
    return native, call, audit, binding, episode["coordinate"]["seed"]


@pytest.mark.parametrize("mutation", ["alias", "hash", "root_depth", "http500", "missing_id", "sampled_node", "completion", "length", "sampling"])
def test_ambiguous_or_wrongly_bound_failed_attempt_remains_fatal(mutation):
    native, call, audit, binding, seed = failed_fixture()
    call, audit = copy.deepcopy(call), copy.deepcopy(audit)
    if mutation == "alias": audit["actual_alias"] = binding["role_map"]["root"]
    elif mutation == "hash": audit["model_sha256"] = "0" * 64
    elif mutation == "root_depth": audit["depth"] = 0
    elif mutation == "http500": audit["native_wire_response"]["http_status"] = 500
    elif mutation == "missing_id": call["acp"] = {}
    elif mutation == "sampled_node": call["node"] = 0
    elif mutation == "completion": audit["native_response"] = {"tokens": {"completion_ids": [123]}}
    elif mutation == "length": audit["native_wire_request"]["body"]["token_ids"].pop()
    elif mutation == "sampling": audit["native_wire_request"]["body"]["sampling_params"]["temperature"] = 1.0
    with pytest.raises(ValueError):
        native.verify_failed_call(call, audit, binding, seed)


def test_failed_call_certificate_does_not_admit_recovered_actions():
    native, call, audit, binding, seed = failed_fixture()
    proof = native.verify_failed_call(call, audit, binding, seed)
    assert proof["training_admission"] is False
    assert proof["prompt_tokens"] == 9972 and proof["model_context_limit"] == 8192
