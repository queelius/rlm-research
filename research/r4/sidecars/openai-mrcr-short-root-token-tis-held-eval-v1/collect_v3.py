"""V3 collector entrypoint bound to the additive READY and checkpoint verifier."""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
from pathlib import Path
import sys

import checkpoint_v3 as checkpoint
import study_v3 as study


def _load_source():
    previous = {name: sys.modules.get(name) for name in ("study_v2", "checkpoint_v2")}
    sys.modules["study_v2"] = study
    sys.modules["checkpoint_v2"] = checkpoint
    try:
        path = study.ROOT / "collect_v2.py"
        spec = importlib.util.spec_from_file_location("token_tis_held_v3_collect_source", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        for name, value in previous.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value


source = _load_source()
source_module = source.source_module
shaped_summary = source.shaped_summary


async def run(arm: str, endpoint: Path, output: Path, deadline: float) -> int:
    return await source.run(arm, endpoint, output, deadline)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=("base", "lr1e-5", "lr1e-4"), required=True)
    parser.add_argument("--endpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--deadline", type=float, required=True)
    args = parser.parse_args()
    raise SystemExit(asyncio.run(run(args.arm, args.endpoint, args.output, args.deadline)))

