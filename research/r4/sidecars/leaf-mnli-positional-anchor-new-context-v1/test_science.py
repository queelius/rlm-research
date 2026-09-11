import json

import protocol as p
import scoring
import study as s


def test_exact_192_inventory_and_pairing():
    plan = s.read(s.ROOT / "PLAN.json")
    assert plan == p.plan()
    assert len(plan) == len({row["id"] for row in plan}) == 192
    assert len({row["context_index"] for row in plan}) == 16
    for context_index in range(16):
        values = [row for row in plan if row["context_index"] == context_index]
        assert len(values) == 12
        assert {row["arm"] for row in values} == set(p.ARMS)
        assert {row["seed"] for row in values} == {p.SEEDS[context_index]}


def test_selection_and_seed_boundaries_are_clean():
    selection = s.read(s.ROOT / "SELECTION_AUDIT.json")
    scan = s.read(s.ROOT / "SEED_SCAN.json")
    assert selection["selected_contexts"] == 16
    assert selection["selected_premise_groups"] == 256
    assert selection["prior_selected_overlap"] == []
    assert selection["label_mutation_ranking_invariant"]
    assert scan["matches_outside_new_sidecar"] == []


def test_all_requests_match_protocol_and_hide_gold():
    requests = s.read(s.ROOT / "REQUESTS.json")
    prompts = s.read(s.ROOT / "PROMPT_IDS.json")
    contexts = p.contexts()
    for row in p.plan():
        assert requests[row["id"]] == p.request(contexts[row["context_index"]], row)
        assert len(prompts[row["id"]]) + 3072 <= 8192
        assert "gold_label" not in json.dumps(requests[row["id"]]["messages"])


def test_primary_summary_is_16_context_interaction():
    rows = [{"coordinate": row, "score": scoring.missing(p.contexts()[row["context_index"]]), "physical_attempt": False, "usage_observed": None} for row in p.plan()]
    summary = scoring.summarize(rows)
    assert len(summary["cells"]) == 12
    assert summary["primary"]["late_denominator"] == 1536
    assert len(summary["primary"]["context_interactions"]) == 16
    assert summary["secondary_output_only_original_gate"]["late_denominator"] == 1536


def test_whole_contract_rejects_wrong_rows_without_salvage():
    context = p.contexts()[0]
    message = {"content": json.dumps([{"row": 0, "label": "neutral"}] * 48), "tool_calls": []}
    result = scoring.score(message, context, "wrong_present_row_first")
    assert result["available"] and not result["contract_valid"]
    assert result["strict_correct"] == 0 and result["predictions"] is None
