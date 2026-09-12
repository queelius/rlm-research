"""V4.1 owner: preserve V4 execution and correct its OWNER_RUN repair description."""

import argparse
import json
from pathlib import Path

import owner_v4 as sealed
import study_v4


ATTEMPT = sealed.ATTEMPT
OWNER_SECONDS = sealed.OWNER_SECONDS
REPAIR = (
    "collector uses allocation-qualified image digest and runtime-an22-5801-v1 "
    "private Docker CLI/store; exact V3 science is unchanged"
)


def correct_owner_run(value):
    return {**value, "repair": REPAIR}


def execute(output, outer_seconds):
    original = sealed.implementation.study.write_x

    def write(path, value):
        if Path(path).name == "OWNER_RUN.json":
            value = correct_owner_run(value)
        return original(path, value)

    sealed.implementation.study.write_x = write
    try:
        return sealed.execute(output, outer_seconds)
    finally:
        sealed.implementation.study.write_x = original


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
