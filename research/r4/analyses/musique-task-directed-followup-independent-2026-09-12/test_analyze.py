from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def module():
    path = ROOT / "analyze.py"
    spec = importlib.util.spec_from_file_location("musique_followup_independent_fixture", path)
    value = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(value)
    return value


def test_independent_answer_and_support_scoring_is_strict():
    a = module()
    gold = {"answer": "The Nile", "answer_aliases": ["Nile"], "support_idxs": [1, 2]}
    score = a.score_text('{"answer":"Nile!","support_idxs":[1,3]}', gold, 4)
    assert score == {
        "valid_json": True, "answer_em": 1.0, "answer_f1": 1.0,
        "support_em": 0.0, "support_f1": 0.5,
        "parsed": {"answer": "Nile!", "support_idxs": [1, 3]},
    }
    assert a.score_text('{"answer":"Nile","support_idxs":[1,1]}', gold, 4)["valid_json"] is False
    assert a.score_text('{"answer":"Nile","support_idxs":[5]}', gold, 4)["valid_json"] is False
    assert a.score_text('{"answer":"wrong","support_idxs":[1,2]}', gold, 4)["answer_em"] == 0


def test_raw_native_call_is_redecoded_and_request_bound(tmp_path):
    a = module()

    class Tokenizer:
        def decode(self, ids, skip_special_tokens=True):
            assert skip_special_tokens is True
            return '{"answer":"Nile","support_idxs":[1]}'

    schedule = {
        "call_id": "call-1", "record_id": "q1", "role": "targeted", "seed": 17,
        "temperature": 0.5, "max_tokens": 1024, "question_index": 0,
    }
    prompt = [{"role": "user", "content": "fixture"}]
    body = {
        "model": a.MODEL_ALIAS, "token_ids": [10, 11], "cache_salt": "0",
        "sampling_params": {
            "seed": 17, "temperature": 0.5, "top_p": 1.0, "top_k": -1,
            "min_p": 0.0, "max_tokens": 1024, "logprobs": 1,
        },
    }
    response = {
        "model": a.MODEL_ALIAS, "request_id": "provider-1",
        "choices": [{"token_ids": [20, 151645], "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 2, "completion_tokens": 2,
                  "prompt_tokens_details": {"cached_tokens": 1}},
    }
    calls = tmp_path / "calls"; native = tmp_path / "native"; prompts = tmp_path / "prompts"
    calls.mkdir(); native.mkdir(); prompts.mkdir()
    request_path = native / "call-1-REQUEST.json"
    response_path = native / "call-1-RESPONSE.json"
    prompt_path = prompts / "call-1.json"
    request_path.write_text(json.dumps(body))
    response_path.write_text(json.dumps(response))
    prompt_path.write_text(json.dumps(prompt))
    record = {
        **schedule, "physical_started": True, "transport_valid": True,
        "status": "returned_valid", "finish_reason": "stop", "request_id": "provider-1",
        "request_path": str(request_path), "response_path": str(response_path),
        "prompt_path": str(prompt_path), "request_bytes_sha256": a.sha(request_path),
        "response_bytes_sha256": a.sha(response_path), "prompt_sha256": a.sha(prompt_path),
        "body_sha256": a.digest(body),
        "text": '{"answer":"Nile","support_idxs":[1]}',
        "prefix_tokens": 2, "usage": response["usage"], "wall_seconds": 1.25,
    }
    (calls / "call-1.json").write_text(json.dumps(record))
    checked = a.check_call(tmp_path, schedule, Tokenizer())
    assert not checked["violations"], checked["violations"]
    assert checked["authenticated"] and checked["decoded_text"].startswith('{"answer"'), checked
    assert checked["usage"] == {"prompt_tokens": 2, "completion_tokens": 2, "cached_tokens": 1}
    assert checked["raw_finish_reason"] == "stop"
    bad = copy.deepcopy(body); bad["sampling_params"]["seed"] = 18
    request_path.write_text(json.dumps(bad))
    assert a.check_call(tmp_path, schedule, Tokenizer())["authenticated"] is False


def test_paired_summary_keeps_unknown_separate_and_compares_equal_cost_arms():
    a = module()
    rows = []
    for record_id, outcomes in {
        "q1": {"stop": "W", "broad": "W", "targeted": "C", "full_source": "C"},
        "q2": {"stop": "C", "broad": "U", "targeted": "W", "full_source": "W"},
    }.items():
        for arm, outcome in outcomes.items():
            rows.append({
                "record_id": record_id, "arm": arm, "hop": 2, "outcome": outcome,
                "score": None if outcome == "U" else {
                    "answer_em": float(outcome == "C"), "answer_f1": float(outcome == "C"),
                    "support_em": 0.0, "support_f1": 0.5, "valid_json": True,
                },
                "gold_mentioned_in_extra": None,
            })
    summary = a.summarize_rows(rows, planned=2)
    assert summary["arms"]["broad"]["unavailable"] == 1
    assert summary["paired"]["broad_to_targeted"] == {
        "planned": 2, "both_available": 1, "unknown_pairs": 1,
        "wins": 1, "losses": 0, "same_correct": 0, "same_wrong": 0,
    }
    assert summary["paired"]["stop_to_targeted"]["wins"] == 1
    assert summary["paired"]["stop_to_targeted"]["losses"] == 1


def test_frozen_plan_has_balanced_pairing_and_exact_budgets():
    a = module()
    receipt = a.verify_plan()
    assert receipt["questions"] == 12 and receipt["calls"] == 132
    assert receipt["roles_per_question"] == 11
    assert receipt["hop_counts"] == {"2": 4, "3": 4, "4": 4}
    assert receipt["policy_calls"] == {"stop": 48, "broad": 72, "targeted": 72, "full_source": 12}
    assert receipt["paired_followup_seed_equal"] and receipt["paired_final_seed_equal"]
