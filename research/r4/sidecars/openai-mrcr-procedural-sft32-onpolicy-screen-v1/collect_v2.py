"""Additive V2 collector repairing only the flat READY input lookup."""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
from pathlib import Path
import sys

import checkpoint_v2 as checkpoint
import study_v2 as study


ROOT = Path(__file__).resolve().parent
previous = {name: sys.modules.get(name) for name in ("study", "checkpoint")}
sys.modules.update(study=study, checkpoint=checkpoint)
try:
    spec = importlib.util.spec_from_file_location("sft32_onpolicy_v1_collect_for_v2", ROOT / "collect.py")
    source = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(source)
finally:
    for name, value in previous.items():
        if value is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = value


def verify_ready() -> dict:
    ready = study.read(study.READY)
    if ready.get("identity") != study.digest(
        {key: value for key, value in ready.items() if key != "identity"}
    ):
        raise ValueError("V2 screen READY identity changed")
    if ready.get("terminal_condition", {}).get("name") != "terminal-strip-disabled":
        raise ValueError("V2 screen requires terminal-strip-disabled")
    for raw, expected in ready.get("closure_sha256", {}).items():
        if study.sha(Path(raw)) != expected:
            raise ValueError("V2 screen closure changed: " + raw)
    if study.digest(study.schedule("train")) != ready["inputs"]["schedule_sha256"]:
        raise ValueError("V2 screen schedule changed")
    return ready


# The inherited run resolves this global in its own source module.
source.verify_ready = verify_ready


async def run(phase: str, arm: str, endpoint: Path, output: Path, deadline: float) -> int:
    if phase != "train" or arm != "checkpoint32":
        raise ValueError("fixed V2 training-only checkpoint32 screen differs")
    return await source.run(phase, arm, endpoint, output, deadline)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("train",), required=True)
    parser.add_argument("--arm", choices=("checkpoint32",), required=True)
    parser.add_argument("--endpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--deadline", type=float, required=True)
    args = parser.parse_args()
    raise SystemExit(asyncio.run(run(args.phase, args.arm, args.endpoint, args.output, args.deadline)))

