"""Exact 96-row collector reused in the attempt-002 namespace."""

import argparse
import asyncio
from pathlib import Path
import owner
import protocol as p
import scoring
import study as s

module = s.load(
    "field_order_recovery_collect",
    s.ORIGINAL / "collect.py",
    "b4f9c8fc7b79c8fcf92ccf61bb9622fa3b1568a89c606473964fd9e4cae13872",
    {"study": s, "protocol": p, "scoring": scoring, "owner": owner},
)
run, summarize = module.run, module.summarize


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("run",))
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--deadline", required=True, type=float)
    args = parser.parse_args()
    owner.validate_argv(
        [
            str(s.NATIVE),
            str(s.ROOT / "collect.py"),
            "run",
            "--endpoint",
            args.endpoint,
            "--output",
            args.output,
            "--deadline",
            str(args.deadline),
        ]
    )
    print(asyncio.run(run(Path(args.endpoint), Path(args.output), args.deadline)))
