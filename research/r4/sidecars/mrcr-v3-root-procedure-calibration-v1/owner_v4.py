"""Attempt-004 owner; repairs only the failed runtime image/store binding."""

import argparse
import json
from pathlib import Path

import owner_v2 as implementation
import study as base_study
import study_v4


ATTEMPT = study_v4.ATTEMPT
COLLECTOR = base_study.ROOT / "collect_v4.py"
OWNER_SECONDS = implementation.OWNER_SECONDS
implementation.ATTEMPT = ATTEMPT
implementation.COLLECTOR = COLLECTOR
implementation.verify = study_v4.verify
execute = implementation.execute


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--output", type=Path, default=ATTEMPT)
    parser.add_argument("--outer-seconds", type=int, default=OWNER_SECONDS)
    args = parser.parse_args()
    if args.command == "verify":
        print(study_v4.verify()["identity"])
    else:
        result = execute(args.output, args.outer_seconds)
        print(json.dumps(result, sort_keys=True))
        raise SystemExit(0 if result["complete"] else 1)

