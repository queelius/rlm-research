"""Recompute baseline/native outcomes from immutable raw episodes under one metric contract."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import native_prefill_arm as native

base = native.baseline


def load_attempt(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    spec = json.loads((path / "SPEC.json").read_text())
    planned = {row["id"]: row for row in spec["plan"]}
    records = []
    for source in sorted((path / "episodes").glob("*.json")):
        row = json.loads(source.read_text())
        if row["coordinate"] != planned.get(source.stem):
            raise ValueError(f"episode coordinate differs from plan: {source}")
        if base.digest(row["episode"]) != row["episode_sha256"]:
            raise ValueError(f"raw episode hash mismatch: {source}")
        metrics = native.episode_metrics(row["episode"], row["timing"]["wall_seconds"])
        records.append({**row, "derived": metrics, "source_sha256": base.file_hash(source)})
    return spec, records


def analyze(attempts: dict[str, Path]) -> dict[str, Any]:
    by_run = {}
    source_specs = {}
    cells = []
    mixed_groups = []
    matched = defaultdict(dict)
    for label, path in attempts.items():
        spec, records = load_attempt(path)
        source_specs[label] = {
            "path": str(path),
            "spec_sha256": base.file_hash(path / "SPEC.json"),
            "planned": len(spec["plan"]),
            "recorded": len(records),
            "complete": len(records) == len(spec["plan"]),
            "treatment": spec.get("treatment", {"name": "baseline"}),
            "coordinate_plan_sha256": spec["coordinate_plan_sha256"],
            "episode_sha256": {row["coordinate"]["id"]: row["source_sha256"] for row in records},
        }
        by_run[label] = native.summarize(records, len(spec["plan"]))
        by_run[label]["treatment"] = source_specs[label]["treatment"]
        grouped = defaultdict(list)
        for row in records:
            coordinate, metrics = row["coordinate"], row["derived"]
            key = (coordinate["task_name"], coordinate["temperature"], coordinate["seed"])
            matched[key][(label, coordinate["client_path"])] = metrics
            grouped[
                (coordinate["task_name"], coordinate["temperature"], coordinate["client_path"])
            ].append(row)
        for cell in by_run[label]["cells"]:
            matching_rows = [
                row["derived"]
                for row in records
                if row["coordinate"]["client_path"] == cell["client_path"]
                and row["coordinate"]["temperature"] == cell["temperature"]
            ]
            cells.append(
                {
                    "run": label,
                    **cell,
                    "execution_failures": sum(
                        not row["execution_completed"] for row in matching_rows
                    ),
                    "completed_format_failures": sum(
                        row["execution_completed"] and row["strict_terminal_valid"] is False
                        for row in matching_rows
                    ),
                    "scored_terminals": sum(
                        row["strict_reward"] is not None for row in matching_rows
                    ),
                }
            )
        for (task, temperature, client), rows in grouped.items():
            usable = [row for row in rows if row["derived"]["update_eligible"]]
            rewards = [row["derived"]["strict_reward"] for row in usable]
            if (
                client == "train"
                and temperature > 0
                and len(usable) >= 2
                and set(rewards) == {0, 1}
            ):
                mixed_groups.append(
                    {
                        "run": label,
                        "task": task,
                        "temperature": temperature,
                        "rewards": rewards,
                        "episode_ids": [row["coordinate"]["id"] for row in usable],
                        "interpretation": (
                            "Calibration only; fresh grouped rollouts required for the next update."
                        ),
                    }
                )
    contrasts = []
    labels = list(attempts)
    if len(labels) == 2:
        before, after = labels
        for (task, temperature, seed), cells_at_coordinate in sorted(matched.items()):
            keys = [(run, client) for run in labels for client in ("eval", "train")]
            if any(key not in cells_at_coordinate for key in keys):
                continue
            record = {
                "task": task,
                "temperature": temperature,
                "seed": seed,
                "before": before,
                "after": after,
                "all_four_completed": all(
                    cells_at_coordinate[key]["execution_completed"] for key in keys
                ),
            }
            for metric in ("python_used", "strict_terminal_valid", "strict_correct"):
                values = [cells_at_coordinate[key][metric] for key in keys]
                if any(value is None for value in values) or not record["all_four_completed"]:
                    record[f"{metric}_interaction"] = None
                else:
                    record[f"{metric}_interaction"] = (
                        int(values[3]) - int(values[2]) - int(values[1]) + int(values[0])
                    )
            contrasts.append(record)
    return {
        "schema": "strict-client-prefill-comparison-v1",
        "source_attempts": source_specs,
        "runs": by_run,
        "cells": cells,
        "matched_interactions": contrasts,
        "mixed_train_groups": mixed_groups,
        "measurement": {
            "input_tokens": (
                "logical_input_tokens = raw prompt_tokens + cached_input_tokens; "
                "cache reporting remains separate"
            ),
            "policy_format_failure": (
                "completed observable malformed output is strict reward 0, "
                "independent of capture trainability"
            ),
            "intent": (
                "closing_tag_ipython_intent_heuristic is diagnostic only "
                "and never changes execution or scoring"
            ),
            "inference": (
                "Descriptive paired exploratory analysis; tasks are the clustering unit "
                "and repeated seeds are not independent task samples."
            ),
        },
        "analysis_source_sha256": {
            str(path): base.file_hash(path)
            for path in (Path(__file__).resolve(), Path(native.__file__), Path(base.__file__))
        },
    }


def report(value: dict[str, Any]) -> str:
    lines = [
        "# Matched client and native-prefill comparison",
        "",
        "This report recomputes both runs from preserved raw episodes using one metric contract.",
        "",
        "| Run | Client | T | Episodes | Executed Python | Strict format | Exact | "
        "Execution errors | Logical input tokens |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in value["cells"]:
        lines.append(
            f"| {row['run']} | {row['client_path']} | {row['temperature']} | {row['episodes']} | "
            f"{row['python_used']} | {row['strict_terminal_valid']} | {row['strict_correct']} | "
            f"{row['execution_failures']} | {row['logical_input_tokens']} |"
        )
    lines.extend(
        [
            "",
            f"Mixed nonzero-temperature train groups: {len(value['mixed_train_groups'])}.",
            "",
            "Counts refer to retained records; source_attempts.complete identifies unfinished "
            "runs. Malformed completed policy outputs keep zero reward; failed execution "
            "has null outcome. Cache coverage is recorded separately from logical input tokens. "
            "The missing-opening-tag intent field is a heuristic diagnostic, "
            "never a parser fallback.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt", action="append", required=True, help="LABEL=/absolute/attempt")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    attempts = {}
    for item in args.attempt:
        label, raw = item.split("=", 1)
        if label in attempts:
            raise ValueError("duplicate run label")
        attempts[label] = Path(raw).resolve()
    value = analyze(attempts)
    if args.output_dir:
        output = args.output_dir.resolve()
        if output.exists() or any(output.is_relative_to(path) for path in attempts.values()):
            raise ValueError("analysis needs a new output directory outside the source attempts")
        base.atomic_json(output / "analysis.json", value)
        (output / "REPORT.md").write_text(report(value))
        base.atomic_json(
            output / "MANIFEST.json",
            {
                path.name: base.file_hash(path)
                for path in (output / "analysis.json", output / "REPORT.md")
            },
        )
    else:
        print(json.dumps(value, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
