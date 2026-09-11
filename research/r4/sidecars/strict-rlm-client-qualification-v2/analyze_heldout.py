"""Leakage-controlled descriptive pre/post analysis under the frozen heldout protocol."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from analyze_comparison import base, load_attempt

ROOT = Path(__file__).resolve().parent
PROTOCOL = ROOT / "HELDOUT_ANALYSIS_PROTOCOL.json"


def paired_counts(before: dict[Any, Any], after: dict[Any, Any]) -> dict[str, Any]:
    keys = before.keys() | after.keys()
    pairs = [
        (before[key], after[key])
        for key in keys
        if before.get(key) is not None and after.get(key) is not None
    ]
    wins = sum(post > pre for pre, post in pairs)
    losses = sum(post < pre for pre, post in pairs)
    return {
        "planned_pairs": len(keys),
        "observable_pairs": len(pairs),
        "wins": wins,
        "losses": losses,
        "ties": len(pairs) - wins - losses,
        "unobservable_or_missing_pairs": len(keys) - len(pairs),
        "paired_delta": (wins - losses) / len(pairs) if pairs else None,
    }


def summarize(attempts: dict[str, Path]) -> dict[str, Any]:
    protocol = json.loads(PROTOCOL.read_text())
    excluded = set(protocol["primary"]["excluded_task_ids"])
    runs, outcomes, source_specs = [], {}, {}
    expected_plan = None
    for label, path in attempts.items():
        spec, records = load_attempt(path)
        plan = spec["plan"]
        if any(row.get("split") != "heldout" for row in plan) or len(plan) != 16:
            raise ValueError("expected the frozen16-episode heldout plan")
        if expected_plan is not None and plan != expected_plan:
            raise ValueError("heldout task/client/temperature/seed coordinates changed across arms")
        expected_plan = plan
        source_specs[label] = {
            "attempt": str(path),
            "spec_sha256": base.file_hash(path / "SPEC.json"),
            "model": spec["endpoint"]["model"],
            "adapter": spec["source_endpoint_descriptor"]["adapter"],
            "collection_phase": spec["collection_phase"],
            "complete": len(records) == len(plan),
            "record_sha256": {row["coordinate"]["id"]: row["source_sha256"] for row in records},
        }
        outcomes[label] = {}
        for split, omit in (("primary", excluded), ("secondary", set())):
            planned = [row for row in plan if int(row["task_name"].rsplit(":", 1)[1]) not in omit]
            ids = {row["id"] for row in planned}
            selected = [row for row in records if row["coordinate"]["id"] in ids]
            results = {row["id"]: None for row in planned}
            results.update(
                {row["coordinate"]["id"]: row["derived"]["strict_reward"] for row in selected}
            )
            outcomes[label][split] = results
            observed = sum(value is not None for value in results.values())
            successes = sum(value == 1 for value in results.values())
            runs.append(
                {
                    "run": label,
                    "split": split,
                    "planned": len(planned),
                    "recorded": len(selected),
                    "observable_terminals": observed,
                    "strict_successes": successes,
                    "strict_policy_failures": sum(value == 0 for value in results.values()),
                    "observable_exact_rate": successes / observed if observed else None,
                    "fixed_budget_success_yield": successes / len(planned),
                    "execution_failures": sum(
                        not row["derived"]["execution_completed"] for row in selected
                    ),
                    "completed_format_failures": sum(
                        row["derived"]["execution_completed"]
                        and row["derived"]["strict_terminal_valid"] is False
                        for row in selected
                    ),
                    "python_episodes": sum(row["derived"]["python_used"] for row in selected),
                    "logical_input_tokens": sum(
                        row["derived"]["logical_input_tokens"] for row in selected
                    ),
                    "completion_tokens": sum(
                        row["derived"]["completion_tokens"] for row in selected
                    ),
                }
            )
    labels = list(attempts)
    comparisons = [
        {
            "before": labels[0],
            "after": label,
            "split": split,
            **paired_counts(outcomes[labels[0]][split], outcomes[label][split]),
        }
        for label in labels[1:]
        for split in ("primary", "secondary")
    ]
    return {
        "schema": "strict-rlm-heldout-analysis-v1",
        "protocol": protocol,
        "protocol_sha256": base.file_hash(PROTOCOL),
        "runs": runs,
        "paired_comparisons": comparisons,
        "source_attempts": source_specs,
        "source_file_sha256": {
            str(path): base.file_hash(path)
            for path in (Path(__file__).resolve(), ROOT / "tests/test_heldout_analysis.py")
        },
        "interpretation": (
            "Task-clustered exploratory paired counts, not independent-sample significance. "
            "Observable exact rate excludes unavailable outcomes; fixed-budget success yield "
            "keeps the planned denominator but does not relabel infrastructure failures reward0."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt", action="append", required=True, help="LABEL=/absolute/attempt")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    attempts = {}
    for value in args.attempt:
        label, path = value.split("=", 1)
        if label in attempts:
            raise ValueError("duplicate attempt label")
        attempts[label] = Path(path).resolve()
    value = summarize(attempts)
    if args.output_dir:
        output = args.output_dir.resolve()
        if output.exists() or any(output.is_relative_to(path) for path in attempts.values()):
            raise ValueError("analysis requires a new directory outside immutable source attempts")
        base.atomic_json(output / "analysis.json", value)
        base.atomic_json(
            output / "MANIFEST.json", {"analysis.json": base.file_hash(output / "analysis.json")}
        )
    else:
        print(json.dumps(value, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
