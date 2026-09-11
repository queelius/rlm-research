"""Unchanged 64-endpoint owner under the unused attempt-002 namespace."""

import argparse
from pathlib import Path
import study as s

original = s.load(
    "scale_harness_recovery_original_owner",
    s.ORIGINAL / "owner.py",
    "202d66593af79fe80022ad9dc4d6e7a6fe6a20483305f553e74e1c4c80167a7a",
    {"study": s},
)
POLICY_ORDER = original.POLICY_ORDER
budget, clock_metadata, error, inventory, collector_argv, execute = (
    original.budget,
    original.clock_metadata,
    original.error,
    original.inventory,
    original.collector_argv,
    original.execute,
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
        print({"complete": result["complete"], "released": result["released"]})
        raise SystemExit(0 if result["complete"] else 1)

