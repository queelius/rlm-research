"""Export fresh recursive actions with current-serving, never historical, log provenance."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import driver


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--allow-partial", action="store_true")
    args = parser.parse_args()
    frozen = json.loads((args.attempt / "SPEC.json").read_text())
    if frozen["schema"] != driver.STUDY:
        raise ValueError("this exporter is restricted to the declared native recursion collection")
    for source, expected in frozen["source_file_sha256"].items():
        if driver.q.file_hash(Path(source)) != expected:
            raise ValueError(f"frozen input changed: {source}")
    driver.validate_serving_evidence(frozen["serving_evidence"])
    # Additive process-local override: the immutable exporter core never reads its old log.
    driver.exporter.observed_logprob_contract = lambda: frozen["serving_evidence"]
    rows, group, manifest = driver.exporter.export_attempt(
        args.attempt, allow_partial=args.allow_partial
    )
    manifest.update(
        {
            "collection": driver.STUDY,
            "questions_reused_from_development": True,
            "further_update_authorized": False,
            "review_required": (
                "Inspect mixed groups, actual recursive capture and child semantic quality"
            ),
            "export_wrapper_sha256": driver.q.file_hash(Path(__file__).resolve()),
        }
    )
    args.output.mkdir(parents=True, exist_ok=False)
    with (args.output / "episodes.jsonl").open("x") as stream:
        for row in rows:
            stream.write(json.dumps(row, sort_keys=True, allow_nan=False) + "\n")
    if group is not None:
        driver.q.atomic_json(args.output / "training-group.json", group)
    manifest["output_sha256"] = {
        path.name: driver.q.file_hash(path) for path in args.output.iterdir() if path.is_file()
    }
    driver.q.atomic_json(args.output / "MANIFEST.json", manifest)
    print(
        json.dumps(
            {
                key: manifest[key]
                for key in (
                    "complete",
                    "recorded",
                    "trainable_episodes",
                    "verified_successes",
                    "controller_turns",
                    "action_tokens",
                    "training_group_episodes",
                    "training_group_unavailable_reason",
                )
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
