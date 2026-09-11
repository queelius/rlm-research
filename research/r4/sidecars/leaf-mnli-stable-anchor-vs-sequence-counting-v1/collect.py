"""Qualified four-worker collector rebound to the stable-anchor protocol."""

import argparse
import asyncio
from pathlib import Path

import owner
import protocol as p
import scoring
import study as s


module = s.load(
    "stable_anchor_collect",
    s.PRIOR / "collect.py",
    "7cc6d945da253f3fab414c80b4fb1ec8b56ac79a80d7856ac94966775c9f6312",
    {"study": s, "protocol": p, "scoring": scoring, "owner": owner},
)
run = module.run
summarize = module.summarize


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("run",))
    parser.add_argument("--endpoint", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--deadline", required=True, type=float)
    args = parser.parse_args()
    owner.validate_argv(
        [
            str(s.NATIVE), str(s.ROOT / "collect.py"), "run", "--endpoint",
            str(args.endpoint), "--output", str(args.output), "--deadline", str(args.deadline),
        ]
    )
    print(asyncio.run(run(args.endpoint, args.output, args.deadline)))
