"""Exact 96-row collector in the additive attempt-002 namespace."""

import argparse
import asyncio
from pathlib import Path

import owner_v2 as owner
import protocol_v2 as p
import recovery_study as s
import scoring_v2 as scoring

module = s.load(
    "position_anchor_recovery_collect",
    s.ROOT / "collect.py",
    "8c7f8723e1be08c1f8af3ce95bca65b3a3b2caf32cf94c020eee07cf5a17e1ea",
    {"study": s, "protocol": p, "scoring": scoring, "owner": owner},
)
run, summarize = module.run, module.summarize


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("run",))
    parser.add_argument("--endpoint", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--deadline", required=True, type=float)
    args = parser.parse_args()
    owner.validate_argv([str(s.NATIVE), str(s.ROOT / "collect_v2.py"), "run", "--endpoint", str(args.endpoint), "--output", str(args.output), "--deadline", str(args.deadline)])
    print(asyncio.run(run(args.endpoint, args.output, args.deadline)))
