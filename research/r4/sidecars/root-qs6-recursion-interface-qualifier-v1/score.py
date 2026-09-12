"""Endpoint and protocol gate for the six-family interface qualifier."""

from collections import Counter
import json
from pathlib import Path


def _protocol_from_rows(rows):
    imports = sum(row.get("raw_protocol", {}).get("bad_import_attempts", 0) for row in rows)
    repeated = max(
        (row.get("raw_protocol", {}).get("max_identical_code_repeats", 1) for row in rows),
        default=1,
    )
    return {"bad_import_attempts": imports, "max_consecutive_identical_code_calls": repeated}


def raw_protocol(rollout):
    summary = {
        "episodes": 0,
        "bad_import_attempts": 0,
        "max_consecutive_identical_code_calls": 1,
        "episodes_with_repeated_identical_action_loop": 0,
    }
    for path in Path(rollout).glob("episodes/*.json"):
        value = json.loads(path.read_text())
        trace = (value.get("traces") or [{}])[0]
        codes = []
        for node in trace.get("nodes") or []:
            message = node.get("message") or {}
            if not isinstance(message, dict) or message.get("role") != "assistant":
                continue
            for call in message.get("tool_calls") or []:
                arguments = call.get("arguments", "")
                try:
                    code = json.loads(arguments).get("code", "")
                except (json.JSONDecodeError, AttributeError):
                    code = arguments
                codes.append(code)
                summary["bad_import_attempts"] += int("from rlm import rlm" in code)
        maximum = 1
        current = 1
        for previous, following in zip(codes, codes[1:]):
            current = current + 1 if following == previous else 1
            maximum = max(maximum, current)
        summary["max_consecutive_identical_code_calls"] = max(
            summary["max_consecutive_identical_code_calls"], maximum
        )
        summary["episodes_with_repeated_identical_action_loop"] += int(maximum > 1)
        summary["episodes"] += 1
    return summary


def compute(rows, semantic_request_audit, protocol=None):
    protocol = protocol or _protocol_from_rows(rows)
    modes = Counter(row["coordinate"]["mode"] for row in rows)
    families = Counter(row["coordinate"]["family"] for row in rows)
    observable = sum(
        row.get("terminal_observable") is True and row.get("endpoint_reward") in (0, 1)
        for row in rows
    )
    correct = sum(row.get("endpoint_reward") == 1 for row in rows)
    failures = []
    if protocol["bad_import_attempts"] != 0:
        failures.append("bad_import_attempts")
    if protocol["max_consecutive_identical_code_calls"] != 1:
        failures.append("repeated_identical_action_loop")
    if observable < 10:
        failures.append("observable_endpoints_below_10_of_12")
    if modes != Counter({"no_child": 6, "enabled": 6}):
        failures.append("mode_inventory")
    if families != Counter({family: 2 for family in ("J1", "J2", "M1", "M2", "T1", "T2")}):
        failures.append("family_inventory")
    if not semantic_request_audit.get("parity"):
        failures.append("semantic_typed_role_request_id_parity")
    return {
        "schema": "root-qs6-recursion-interface-qualifier-result-v1",
        "episodes": len(rows),
        "endpoint_correct": correct,
        "endpoint_incorrect": observable - correct,
        "endpoint_unavailable": len(rows) - observable,
        "protocol": protocol,
        "semantic_request_audit": semantic_request_audit,
        "gate": {
            "pass": not failures,
            "failures": failures,
            "requirements": {
                "bad_import_attempts": 0,
                "max_consecutive_identical_code_calls": 1,
                "minimum_observable_endpoints": 10,
                "all_six_families_in_both_modes": True,
                "semantic_typed_role_request_id_parity": True,
            },
        },
    }
