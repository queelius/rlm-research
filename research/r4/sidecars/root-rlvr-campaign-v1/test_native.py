"""CPU-only native prefix/routing reuse and frozen task/coordinate contracts."""

import copy

import pytest

import campaign_common as c
import campaign_native as native


def test_original_task_identity_and_transfer_split_are_frozen():
    identities = native.task_identity(native.make_tasks())
    assert identities == c.read(c.ROOT / "inputs/TASK_IDENTITIES.json")
    pilot_tasks = {t["name"]: t for t in c.read(c.PILOT / "SPEC.json")["tasks"]}
    for name, task in pilot_tasks.items():
        assert identities[name]["task_hash"] == task["arms"]["sft_child"]["task_hash"]
        assert identities[name]["context_sha256"] == task["context_sha256"]
    plan = c.read(c.ROOT / "inputs/PLANS.json")
    assert all(len(rows) == 32 for rows in plan["training"].values())
    assert len(plan["validation"]) == 8
    original = {(r["task_name"], r["repeat"]): r for r in plan["transfer_original"]}
    selected = {(r["task_name"], r["repeat"]): r for r in plan["transfer_selected"]}
    assert original.keys() == selected.keys()
    assert all(original[key]["seed"] == selected[key]["seed"] for key in original)
    public = c.read(c.ROOT / "inputs/TRANSFER_PUBLIC.json")
    pilot = c.read(c.PILOT / "inputs/PUBLIC.json")
    assert not ({g for x in public["contexts"] for g in x["group_ids"]}
                & {g for x in pilot["contexts"] for g in x["group_ids"]})


def test_real_native_three_call_fixture_keeps_two_root_targets_and_no_child_credit():
    fixture = c.PILOT / "qualification-attempt-001"
    roots, evidence = native.exporter.episode_turns(c.read(fixture / "EPISODE.json"), fixture, native.capture.binding())
    assert len(roots) == 2 and len(evidence) == 3
    assert all(t["role_depth"] == 0 and t["credited"] for t in roots)
    assert all(not t["credited"] for t in evidence if t["role_depth"] == 1)
    for turn in roots:
        assert turn["labels"][:turn["prompt_length"]] == [-100] * turn["prompt_length"]
        assert turn["loss_mask"][:turn["prompt_length"]] == [0] * turn["prompt_length"]


def test_depth_routing_uses_actual_current_alias_not_original_literal():
    from native_routing import route_native
    roles = {"root": "campaign-root-step7", "children": ["fixed-child"]}
    headers = {"x-rlm-role-depth": "0", "x-rlm-role-invocation": "native-proof",
               "x-rlm-role-request-id": "a" * 32, "x-rlm-role-kind": "ordinary"}
    body = {"model": "campaign-root-step7", "messages": [{"role": "user", "content": "public context"}]}
    assert route_native(copy.deepcopy(body), headers, roles, "fixed-child")["actual_alias"] == roles["root"]
    assert route_native(copy.deepcopy(body), {**headers, "x-rlm-role-depth": "1"}, roles, "fixed-child")["actual_alias"] == "fixed-child"
    with pytest.raises(ValueError, match="root alias"):
        route_native({**body, "model": "stale-original"}, headers, roles, "fixed-child")


def test_owned_service_stop_rejects_pid_reuse_without_signaling(tmp_path, monkeypatch):
    import campaign
    service = tmp_path / "service"
    c.write_once(service / "SERVER_START.json", {"fixture": True})
    c.write_once(service / "BINDING.json", {"fixture": True})
    owner = {"process": {"pid": 123, "start_ticks": 10},
             "server_start_sha256": c.file_hash(service / "SERVER_START.json"),
             "binding_sha256": c.file_hash(service / "BINDING.json")}
    monkeypatch.setattr(campaign, "claim_service", lambda path: owner)
    monkeypatch.setattr(campaign, "process_identity", lambda pid: {"pid": 123, "start_ticks": 11})
    def forbidden_signal(*args):
        raise AssertionError("must not signal a reused PID")
    monkeypatch.setattr(campaign.os, "killpg", forbidden_signal)
    with pytest.raises(ValueError, match="PID/group identity"):
        campaign.stop_service(service)
