"""Corrected owner entry point using mode-specific collection/export TASKS evidence."""

import argparse
from pathlib import Path

import collect_v2
import owner as v1
import study
import study_v2


v1.collect = collect_v2
study.verify = study_v2.verify


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--output", type=Path, default=study.ATTEMPT)
    parser.add_argument("--outer-seconds", type=int, default=study.OUTER_SECONDS)
    args = parser.parse_args()
    if args.command == "verify":
        print(study_v2.verify()["identity"])
    else:
        result = v1.execute(args.output, args.outer_seconds)
        print(result)
        raise SystemExit(0 if result["complete"] else 1)
