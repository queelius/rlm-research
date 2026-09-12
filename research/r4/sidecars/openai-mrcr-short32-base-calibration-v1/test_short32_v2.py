import json
from pathlib import Path

import pytest

import study


def kwargs(**updates):
    value = {
        "root_reply": None,
        "answer": "MARKER1234payload",
        "marker": "MARKER1234",
        "stop_condition": "unknown_framework_stop",
        "trace_ok": False,
        "trace_errors": [],
        "returned_root_actions": 1,
        "returned_child_actions": 0,
        "native_mapping_complete": True,
    }
    value.update(updates)
    return value


def test_unknown_stop_is_unavailable_not_model_zero():
    import classify_v2

    value = classify_v2.classify_outcome(**kwargs())
    assert value["scientifically_available"] is False
    assert value["reward"] is None
    assert value["failure_class"] == "ambiguous_nonmodel_stop_unavailable"


def test_only_explicit_model_stops_receive_zero():
    import classify_v2

    limited = classify_v2.classify_outcome(**kwargs(stop_condition="max_turns"))
    assert limited["scientifically_available"] is True
    assert limited["reward"] == 0.0
    invalid = classify_v2.classify_outcome(
        **kwargs(stop_condition="agent_completed", trace_ok=True)
    )
    assert invalid["scientifically_available"] is True
    assert invalid["failure_class"] == "model_invalid_terminal"
    infra = classify_v2.classify_outcome(
        **kwargs(stop_condition="max_turns", trace_errors=[{"type": "TransportError"}])
    )
    assert infra["scientifically_available"] is False
    assert infra["failure_class"] == "infrastructure_unavailable"


def test_v2_owner_is_additive_and_uses_repaired_collector():
    import owner_v2

    assert owner_v2.ATTEMPT == study.ROOT / "outputs/attempt-002"
    assert owner_v2.COLLECTOR == study.ROOT / "collect_v2.py"
    assert not (study.ROOT / "READY_V2.json").exists()


def test_readonly_is_documented_as_instruction_not_enforcement():
    amendment = json.loads((study.ROOT / "REVIEW_AMENDMENT_V2.json").read_text())
    assert amendment["context_file"]["model_instruction_says_read_only"] is True
    assert amendment["context_file"]["filesystem_immutability_enforced"] is False
    assert amendment["context_file"]["verified_boundary"] == "initial byte identity only"


def test_exact_mapping_on_real_two_turn_short32_smoke():
    import causal_map_v2

    root = study.ROOT / "cpu-smoke"
    trace = json.loads((root / "EPISODE.json").read_text())["traces"][0]
    native = [
        json.loads(path.read_text())
        for path in sorted((root / "native-calls").glob("*-result.json"))
    ]
    result = causal_map_v2.map_trace(trace, native)
    assert result["complete"] is True
    assert (result["root_actions"], result["child_actions"]) == (2, 0)
    assert [row["node"] for row in result["matches"]] == [2, 4]
    assert all(row["client_request_id"] != row["provider_response_id"] for row in result["matches"])


def test_actual_multiturn_child_graph_counts_turns_not_invocations():
    import causal_map_v2

    path = Path(
        "/project/alex_phd/runs/rlm-research-r4/sidecars/"
        "root-operator-composition-transfer-v1/outputs/attempt-001/sft6/free/"
        "c91a2a543aa54382e8140e820f08a9fb83536517674befaede776655f3e45d4b/"
        "EPISODE.json"
    )
    trace = json.loads(path.read_text())["traces"][0]
    native = []
    for index, call in enumerate(trace["calls"]):
        evidence = causal_map_v2.node_evidence(trace["nodes"], call["node"])
        native.append(
            {
                "status": "returned",
                "session_id": trace["id"],
                "model": call["model"],
                "sampling": call["sampling"],
                "turn": {"trace_id": trace["id"]},
                "response": {
                    "id": f"provider-{index}",
                    "model": call["model"],
                    "finish_reason": call["finish_reason"],
                    "tokens": {
                        "prompt_ids": evidence["prompt_ids"],
                        "completion_ids": evidence["completion_ids"],
                        "completion_logprobs": evidence["completion_logprobs"],
                    },
                },
                "evidence": {
                    "completion_ids_sha256": causal_map_v2._digest(
                        evidence["completion_ids"]
                    )
                },
            }
        )
    result = causal_map_v2.map_trace(trace, native)
    assert result["complete"] is True
    assert len(trace["calls"]) == 4
    assert trace["metrics"]["sub_rlm_num_calls"] == 1.0
    assert (result["root_actions"], result["child_actions"]) == (2, 2)
    assert result["child_invocations"] == 1


def test_runtime_condition_rejects_result_count_without_raw_evidence(tmp_path):
    import owner_v2

    attempt = tmp_path / "attempt"
    (attempt / "science").mkdir(parents=True)
    study.write_x(
        attempt / "OWNER_TERMINAL.json",
        {"complete": True, "released": True, "errors": None, "elapsed_seconds": 10},
    )
    study.write_x(
        attempt / "science/RESULT.json",
        {"complete": True, "recorded": 32, "native_result_files": 10},
    )
    result = owner_v2.runtime_condition(attempt)
    assert result["qualified"] is False
    assert result["returned_native_responses"] == 0
    assert result["elapsed_bound_kind"] == "whole_owner_conservative_bound_not_science_interval"
