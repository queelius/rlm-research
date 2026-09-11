"""Attempt-002 owner using the unchanged 96-row/1,800-second allocation."""

import argparse
from pathlib import Path
import protocol as p
import study as s

module = s.load(
    "field_order_recovery_owner",
    s.ORIGINAL / "owner.py",
    "7ffb97756262b5cbdfeb89f378e9e6a5c4770f36fdd8382141b2f61075cdc054",
    {"study": s, "protocol": p},
)
validate_argv, collector_argv, credential, binding, preflight, suite, execute = (
    getattr(module, name)
    for name in (
        "validate_argv",
        "collector_argv",
        "credential",
        "binding",
        "preflight",
        "suite",
        "execute",
    )
)


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
