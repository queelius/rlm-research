"""Exact held16 raw collector, rebound only to the three token-TIS arms."""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
from pathlib import Path
import sys

import checkpoint
import study


SOURCE = study.SOURCE_EVAL / "collect.py"


def _source():
    previous = {name: sys.modules.get(name) for name in ("study", "checkpoint")}
    sys.modules["study"] = study
    sys.modules["checkpoint"] = checkpoint
    try:
        spec = importlib.util.spec_from_file_location("token_tis_held_source_collect", SOURCE)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        for name, value in previous.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value


source = _source()
shaped_summary = source.shaped_summary
source_module = source.source_module


async def run(arm: str, endpoint: Path, output: Path, deadline: float) -> int:
    if arm not in ("base", "lr1e-5", "lr1e-4"):
        raise ValueError("unknown fixed token-TIS arm")
    return await source.run(arm, endpoint, output, deadline)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=("base", "lr1e-5", "lr1e-4"), required=True)
    parser.add_argument("--endpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--deadline", type=float, required=True)
    args = parser.parse_args()
    raise SystemExit(asyncio.run(run(args.arm, args.endpoint, args.output, args.deadline)))
