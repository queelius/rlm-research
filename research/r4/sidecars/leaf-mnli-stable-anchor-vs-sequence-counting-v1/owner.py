"""MAIN-only owner using the qualified 192-call released-base lifecycle."""

import argparse
from pathlib import Path

import protocol as p
import study as s


module = s.load(
    "stable_anchor_owner",
    s.PRIOR / "owner.py",
    "021eae6f5edfceaf95d190f8f1b556053fc83333debdeb7e4b846f9d813d74b6",
    {"study": s, "protocol": p},
)
CLOCK = module.CLOCK
validate_argv = module.validate_argv
collector_argv = module.collector_argv
credential = module.credential
binding = module.binding
preflight = module.preflight
suite = module.suite
execute = module.execute


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--output", type=Path, default=s.ATTEMPT)
    args = parser.parse_args()
    if args.command == "verify":
        print(s.verify()["identity"])
    else:
        result = execute(args.output)
        print(result)
        raise SystemExit(0 if result["complete"] else 1)
