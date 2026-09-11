import json


def test_seed_scan_excludes_only_the_approved_proposal_and_new_sidecar():
    import prepare

    value = prepare.scan_seeds()
    assert value["matches_outside_new_sidecar"] == []
    assert value["excluded_approved_proposal"].endswith("2026-09-10-mnli-positional-anchor-binding-design.md")


def test_frozen_inputs_are_exact_and_paired():
    import protocol as p
    import study as s

    plan = s.read(s.ROOT / "inputs/PLAN.json")
    requests = s.read(s.ROOT / "inputs/REQUESTS.json")
    native = s.read(s.ROOT / "inputs/CPU_NATIVE.json")
    assert plan == p.plan()
    assert len(plan) == len(requests) == len(native["request_wire_sha256"]) == 96
    for row in plan:
        assert requests[row["id"]] == p.request(p.contexts()[row["context_index"]], row)
        assert requests[row["id"]]["seed"] == row["seed"]
        assert requests[row["id"]].get("tools") in (None, [])


def test_no_outcome_or_gold_enters_prompts_and_seed_scan_is_clean():
    import study as s

    requests = s.read(s.ROOT / "inputs/REQUESTS.json")
    seed_scan = s.read(s.ROOT / "inputs/SEED_SCAN.json")
    assert seed_scan["matches_outside_new_sidecar"] == []
    assert seed_scan["outcomes_consulted"] is False
    for body in requests.values():
        text = json.dumps(body["messages"])
        assert "gold_label" not in text
