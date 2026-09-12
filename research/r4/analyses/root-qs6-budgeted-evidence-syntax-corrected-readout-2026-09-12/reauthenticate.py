"""Call-free endpoint re-authentication after the syntax screen's stale TASKS prefix bug."""

from __future__ import annotations

from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
STORE = HERE.parents[1]
SIDE = STORE / "sidecars/root-qs6-budgeted-evidence-syntax-v1"
ATTEMPT = SIDE / "outputs/attempt-001"
INDEPENDENT = STORE / "analyses/root-qs6-budgeted-evidence-syntax-independent-2026-09-12"
SOURCE_RESULT = INDEPENDENT / "RESULT.json"
PLANS = SIDE / "PLANS.json"
PREFIXES = SIDE / "PREFIXES.json"
TASKS = SIDE / "TASKS.json"
READY = SIDE / "READY.json"
ARMS = ("budgeted_plain", "budgeted_syntax_example")
PINS = {
    SOURCE_RESULT: "5ccd140585bef1231f2331e198c6a195ba213aa1bfd932fc6c3a04eeac305d36",
    READY: "c2af923cd014642eea1884861570f25a54f245bae99df02e44a0d66fe92ee960",
    PLANS: "3c055492bdd450f5186b421bf567d0fd12390875bc0e89f0a8803057165224b0",
    PREFIXES: "35b735a398bc367af1780944f6108478639f1ad037f43ee597599b1c4226bcaf",
    TASKS: "f3e2c2deda673458b711f83da96ab4ab8758d4f55919e9775a87c157f76975a5",
}


def read(path: Path) -> dict:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_corrected_tasks(plans: dict, prefixes: dict, tasks: dict) -> dict:
    """Replace only the stale audit field, requiring paired prompts to be identical."""
    corrected = copy.deepcopy(tasks)
    if set(plans) != set(tasks):
        raise ValueError("plan/task arm inventory differs")
    for arm, arm_plans in plans.items():
        for task_name, task in corrected[arm].items():
            rows = [row for row in arm_plans if row["task_name"] == task_name]
            values = [prefixes[row["id"]]["token_ids"] for row in rows]
            if len(values) != 2 or values[0] != values[1]:
                raise ValueError("task/repeat does not resolve one frozen condition prefix")
            task["first_prompt_token_ids"] = values[0]
    return corrected


def augment_gold(plans: dict, host_gold: dict) -> dict:
    """Map frozen helper-repeat context IDs to their pinned public source context."""
    result = copy.deepcopy(host_gold)
    seen = {}
    for arm_plans in plans.values():
        for row in arm_plans:
            mapping = row["source_context_id"]
            prior = seen.setdefault(row["context_id"], mapping)
            if prior != mapping:
                raise ValueError("synthetic context ID has inconsistent source mapping")
            result[row["context_id"]] = copy.deepcopy(host_gold[row["source_context_id"]])
    return result


def summarize(rows: list[dict], arms: tuple[str, str] = ARMS) -> dict:
    by_arm = {}
    for arm in arms:
        values = [row for row in rows if row["arm"] == arm]
        endpoint = Counter(
            "C" if row["endpoint_reward"] == 1 else "W" if row["endpoint_available"] else "U"
            for row in values
        )
        interface = Counter(row["interface_cwu"] for row in values)
        by_arm[arm] = {
            "planned": len(values),
            "endpoint_cwu": {key: endpoint[key] for key in "CWU"},
            "interface_cwu": {key: interface[key] for key in "CWU"},
            "interface_usable": sum(row["interface_usable"] for row in values),
            "strict_finals": sum(row["strict_final_exists"] for row in values),
            "finish_consistent_strict_finals": sum(
                row["strict_final_exists"] and row["local_finish_consistent"] for row in values
            ),
            "provider_errors": sum(row["provider_error"] is not None for row in values),
        }
    first, second = arms
    first_by_pair = {row["pair_id"]: row for row in rows if row["arm"] == first}
    second_by_pair = {row["pair_id"]: row for row in rows if row["arm"] == second}
    if first_by_pair.keys() != second_by_pair.keys():
        raise ValueError("paired inventory differs")
    endpoint_pairs = Counter()
    interface_pairs = Counter()
    for pair_id, left in first_by_pair.items():
        right = second_by_pair[pair_id]
        if not left["endpoint_available"] or not right["endpoint_available"]:
            endpoint_pairs["unknown"] += 1
        elif right["endpoint_reward"] > left["endpoint_reward"]:
            endpoint_pairs["syntax_wins"] += 1
        elif right["endpoint_reward"] < left["endpoint_reward"]:
            endpoint_pairs["syntax_losses"] += 1
        else:
            endpoint_pairs["ties"] += 1
        if right["interface_usable"] and not left["interface_usable"]:
            interface_pairs["syntax_wins"] += 1
        elif left["interface_usable"] and not right["interface_usable"]:
            interface_pairs["syntax_losses"] += 1
        else:
            interface_pairs["ties"] += 1
    return {
        "arms": by_arm,
        "paired_endpoint_correctness": {
            key: endpoint_pairs[key] for key in ("syntax_wins", "syntax_losses", "ties", "unknown")
        },
        "paired_interface_usability": {
            key: interface_pairs[key] for key in ("syntax_wins", "syntax_losses", "ties")
        },
    }


def _role_results(directory: Path) -> list[dict]:
    return [read(path) for path in sorted((directory / "role-audit").glob("*-result.json"))]


def _provider_errors(trace: dict, role_results: list[dict]) -> list[dict]:
    invocation = trace.get("id")
    return [
        {
            "request_id": row.get("request_id"),
            "status": row.get("status"),
            "depth": row.get("depth"),
            "http_status": (row.get("native_wire_response") or {}).get("http_status"),
            "error": row.get("error"),
        }
        for row in role_results
        if row.get("invocation") == invocation and row.get("status") == "error"
    ]


def derive() -> dict:
    for path, expected in PINS.items():
        if sha(path) != expected:
            raise ValueError(f"pinned source changed: {path}")
    plans, prefixes, tasks = read(PLANS), read(PREFIXES), read(TASKS)
    independent = read(SOURCE_RESULT)
    independent_rows = {(row["arm"], row["coordinate_id"]): row for row in independent["rows"]}
    corrected_tasks = build_corrected_tasks(plans, prefixes, tasks)

    sys.path.insert(0, str(SIDE))
    try:
        import collect  # type: ignore
        import terminal_metrics  # type: ignore
    finally:
        sys.path.pop(0)
    if Path(collect.__file__).resolve() != (SIDE / "collect.py").resolve():
        raise ValueError("wrong syntax collector imported")

    metric_study = terminal_metrics.qualified.s
    original_read = metric_study.read
    task_path = (metric_study.ROOT / "inputs/TASKS.json").resolve()
    gold_path = (metric_study.ROOT / "inputs/HOST_GOLD.json").resolve()
    corrected_gold = augment_gold(plans, original_read(gold_path))
    active_arm = [None]

    def corrected_read(path):
        resolved = Path(path).resolve()
        if resolved == task_path:
            return corrected_tasks[active_arm[0]]
        if resolved == gold_path:
            return corrected_gold
        return original_read(path)

    metric_study.read = corrected_read
    rows = []
    try:
        for arm in ARMS:
            active_arm[0] = arm
            collect.activate(arm)
            rollout = ATTEMPT / arm / "collection/rollout"
            spec = read(rollout / "SPEC.json")
            role_results = _role_results(rollout)
            for plan in plans[arm]:
                prior = independent_rows[(arm, plan["id"])]
                episode = read(rollout / "episodes" / f"{plan['id']}.json")
                if json.loads(episode["task"]["data"]["answer"]) != [prior["gold_target"]]:
                    raise ValueError("raw task answer differs from independently reconstructed gold")
                corrected = terminal_metrics.endpoint(episode, rollout, spec, plan)
                trace = episode["traces"][0]
                errors = _provider_errors(trace, role_results)
                if corrected["available"] and errors:
                    raise ValueError("authenticated endpoint unexpectedly has provider error")
                interface_usable = bool(
                    corrected["available"]
                    and prior["strict_final_exists"]
                    and prior["finish_consistent"]
                    and prior["final_finish_reason"] == "stop"
                    and prior["raw_trace_clean"]
                )
                interface_cwu = (
                    "C" if interface_usable and prior["gold_exact"] is True
                    else "W" if interface_usable
                    else "U"
                )
                rows.append(
                    {
                        "arm": arm,
                        "coordinate_id": plan["id"],
                        "pair_id": plan["pair_id"],
                        "family": plan["family"],
                        "source_context_id": plan["source_context_id"],
                        "repeat": plan["repeat"],
                        "endpoint_available": corrected["available"],
                        "endpoint_reward": corrected["reward"],
                        "endpoint_format": corrected["format"],
                        "endpoint_finish_reason": corrected.get("finish_reason"),
                        "endpoint_reason": corrected.get("reason"),
                        "endpoint_final_request_id": corrected.get("final_request_id"),
                        "corrected_first_prompt_verified": corrected.get("first_prompt_verified"),
                        "provider_error": errors[0] if len(errors) == 1 else None,
                        "strict_final_exists": prior["strict_final_exists"],
                        "strict_final": prior["strict_final"],
                        "gold_target": prior["gold_target"],
                        "gold_exact": prior["gold_exact"],
                        "local_finish_consistent": prior["finish_consistent"],
                        "interface_usable": interface_usable,
                        "interface_cwu": interface_cwu,
                        "raw_sha256": prior["raw_sha256"],
                    }
                )
    finally:
        metric_study.read = original_read

    result = {
        "schema": "root-qs6-budgeted-evidence-syntax-corrected-readout-v1",
        "status": "complete_call_free_reauthentication",
        "original_all_unavailable_preserved": True,
        "new_model_calls": 0,
        "correction": {
            "fields": ["first_prompt_token_ids", "synthetic_context_to_source_gold_mapping"],
            "first_prompt_source": str(PREFIXES),
            "model_or_response_changed": False,
            "reason": (
                "the condition collector copied the original task record and changed task_hash only; "
                "the inherited exporter therefore checked each actual condition prompt against stale IDs"
            ),
        },
        "semantics": {
            "endpoint": (
                "inherited authenticated endpoint: a returned stop/length response is observed; "
                "anything not exactly correct is W"
            ),
            "interface": "unique strict final plus matching accepted finish state plus native stop",
            "provider_or_unreturned": "U",
        },
        "summary": summarize(rows),
        "rows": rows,
        "source_sha256": {str(path): sha(path) for path in PINS},
    }
    return result


def render(result: dict) -> str:
    plain = result["summary"]["arms"][ARMS[0]]
    syntax = result["summary"]["arms"][ARMS[1]]
    paired_endpoint = result["summary"]["paired_endpoint_correctness"]
    paired_interface = result["summary"]["paired_interface_usability"]
    return f"""---
title: Corrected syntax-interface readout
date: 2026-09-12
status: complete_call_free_reauthentication
---

# The syntax example reduced invalid actions but worsened observed endpoints

This additive audit re-authenticates the original48 saved episodes against the
exact condition-specific prompts frozen before generation. It makes no model
calls and does not replace the preserved all-unavailable export.

Under the inherited endpoint semantics, plain is C/W/U =
{plain['endpoint_cwu']['C']}/{plain['endpoint_cwu']['W']}/{plain['endpoint_cwu']['U']}
and syntax is {syntax['endpoint_cwu']['C']}/{syntax['endpoint_cwu']['W']}/{syntax['endpoint_cwu']['U']}.
Among the24 matched pairs, syntax has {paired_endpoint['syntax_wins']} win,
{paired_endpoint['syntax_losses']} losses, {paired_endpoint['ties']} ties and
{paired_endpoint['unknown']} unknown pairs. Returned finite-horizon `stop` or
`length` responses count as observed failures when they are not exactly correct;
only provider/unreturned outcomes remain unavailable.

The stricter action-interface result is plain C/W/U =
{plain['interface_cwu']['C']}/{plain['interface_cwu']['W']}/{plain['interface_cwu']['U']}
and syntax {syntax['interface_cwu']['C']}/{syntax['interface_cwu']['W']}/{syntax['interface_cwu']['U']}.
Syntax has {paired_interface['syntax_wins']} usability wins and
{paired_interface['syntax_losses']} losses. The syntax arm never aligned a strict
final with its accepted local `finish()` state; plain did so five times.

The original raw comparison's useful secondary count remains35→8 rejected API
actions. That lower syntax-error count did not translate into better endpoints.
Two plain and three syntax requests exceeded the8192-token context limit and are
the five remaining unavailable outcomes. Both arms used only physical root calls;
saved-map `classify` callbacks were logical local calls, not child inference.

This is an exploratory result on two familiar, research-exposed contexts. It does
not establish generalization, causal evidence use, or live child-compute savings.
"""


def main() -> None:
    result = derive()
    with (HERE / "CORRECTED_RESULT.json").open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    (HERE / "CORRECTED_REPORT.md").write_text(render(result))
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
