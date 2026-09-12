"""Additive attempt003 owner for the exact-full-query realization."""

import argparse
import json
from pathlib import Path

import owner_v2 as implementation
import study
import study_v3


ATTEMPT = study_v3.ATTEMPT
COLLECTOR = study.ROOT / "collect_v3.py"
OWNER_SECONDS = implementation.OWNER_SECONDS
implementation.ATTEMPT = ATTEMPT
implementation.COLLECTOR = COLLECTOR
implementation.verify = study_v3.verify
execute = implementation.execute


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--output", type=Path, default=ATTEMPT)
    parser.add_argument("--outer-seconds", type=int, default=OWNER_SECONDS); args = parser.parse_args()
    if args.command == "verify": print(study_v3.verify()["identity"])
    else:
        result = execute(args.output, args.outer_seconds); print(json.dumps(result, sort_keys=True))
        raise SystemExit(0 if result["complete"] else 1)

