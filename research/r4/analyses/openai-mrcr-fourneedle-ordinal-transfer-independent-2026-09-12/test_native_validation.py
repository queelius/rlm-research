from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("fourneedle_native_validation", ROOT / "native_validation.py")
native = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(native)


def test_sampling_contract_rejects_the_only_changed_field() -> None:
    expected = {
        "temperature": 0.5,
        "top_p": 1.0,
        "seed": 202609260001,
        "max_tokens": 2048,
        "reasoning_effort": None,
        "extra_body": {"top_k": -1, "min_p": 0.0, "return_token_ids": True, "cache_salt": "0"},
    }
    assert native.sampling_issues(expected, 202609260001) == []
    changed = {**expected, "temperature": 1.0}
    assert native.sampling_issues(changed, 202609260001) == ["sampling.temperature"]


def test_cpu_ready_identity_and_closure_are_checked() -> None:
    value = native.verify_analysis_ready()
    assert value["identity"] == "4aed35848565e22be47254b7ed46aa1405b59406d8eb548d06289b4fd2840b4d"


def test_length_exhaustion_with_empty_reply_is_not_a_decode_mismatch() -> None:
    calls = {2: {"finish_reason": "length"}}
    matches = [{"node": 2, "role": "root", "audit_index": 0}]
    assert native.terminal_expectation(calls, matches, "") == "NO_PHYSICAL_STOP_EMPTY_REPLY"
