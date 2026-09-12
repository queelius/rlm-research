"""Exact original raw collector with checkpoint32 binding."""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
from pathlib import Path
import sys

import checkpoint
import study


def _load_source():
    previous = {name: sys.modules.get(name) for name in ("study", "checkpoint")}
    sys.modules["study"] = study
    sys.modules["checkpoint"] = checkpoint
    try:
        path = study.SOURCE_EVAL / "collect.py"
        spec = importlib.util.spec_from_file_location("procedural_sft_continue32_collect_source", path)
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
source_module = lambda: source
verify_ready = source.verify_ready
role_hooks = source.role_hooks
model_context = source.model_context
inspect_trace = source.inspect_trace
manipulation_gate = source.manipulation_gate
summarize = source.summarize


async def run(phase: str, arm: str, endpoint: Path, output: Path, deadline: float) -> int:
    if phase not in ("train", "held") or arm not in ("base", "checkpoint32"):
        raise ValueError("fixed phase/arm differs")
    return await source.run(phase, arm, endpoint, output, deadline)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("train", "held"), required=True)
    parser.add_argument("--arm", choices=("base", "checkpoint32"), required=True)
    parser.add_argument("--endpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--deadline", type=float, required=True)
    args = parser.parse_args()
    raise SystemExit(asyncio.run(run(args.phase, args.arm, args.endpoint, args.output, args.deadline)))
