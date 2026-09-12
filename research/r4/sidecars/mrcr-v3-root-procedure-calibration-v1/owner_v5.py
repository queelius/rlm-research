"""Attempt-005 owner for the canonical task-setup dispatch repair."""

import argparse
import json
from pathlib import Path

import owner_v4 as sealed
import study as base
import study_v5


ATTEMPT = study_v5.ATTEMPT
COLLECTOR = base.ROOT / "collect_v5.py"
OWNER_SECONDS = sealed.OWNER_SECONDS
sealed.implementation.ATTEMPT = ATTEMPT
sealed.implementation.COLLECTOR = COLLECTOR
sealed.implementation.verify = study_v5.verify


def execute(output, outer_seconds):
    original = sealed.implementation.study.write_x

    def write(path, value):
        if Path(path).name == "OWNER_RUN.json":
            value = {**value, "repair": (
                "patch the canonical registry-loaded MRCRTask.setup to materialize the exact "
                "frozen full-query through the allocation-qualified runtime"
            )}
        return original(path, value)

    sealed.implementation.study.write_x = write
    try:
        return sealed.implementation.execute(output, outer_seconds)
    finally:
        sealed.implementation.study.write_x = original


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--output", type=Path, default=ATTEMPT)
    parser.add_argument("--outer-seconds", type=int, default=OWNER_SECONDS)
    args = parser.parse_args()
    if args.command == "verify":
        print(study_v5.verify()["identity"])
    else:
        result = execute(args.output, args.outer_seconds)
        print(json.dumps(result, sort_keys=True))
        raise SystemExit(0 if result["complete"] else 1)
