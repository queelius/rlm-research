"""Exact raw MRCR collector under the terminal-strip-disabled condition."""

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
    sys.modules.update(study=study, checkpoint=checkpoint)
    try:
        path = study.SOURCE_EVAL / "collect.py"
        spec = importlib.util.spec_from_file_location("mrcr_long_transfer_collect_source", path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module
    finally:
        for name, value in previous.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value


source = _load_source()
hooks = study.terminal_hooks()


def verify_ready() -> dict:
    ready = study.read(study.READY)
    if ready.get("identity") != study.digest(
        {key: value for key, value in ready.items() if key != "identity"}
    ):
        raise ValueError("long-transfer READY identity changed in collector process")
    for raw, expected in ready.get("closure_sha256", {}).items():
        if study.sha(Path(raw)) != expected:
            raise ValueError("long-transfer closure changed in collector process: " + raw)
    if study.digest(study.schedule()) != ready["inputs"]["schedule_sha256"]:
        raise ValueError("long-transfer schedule changed in collector process")
    return ready


source.verify_ready = verify_ready


async def run(phase: str, arm: str, endpoint: Path, output: Path, deadline: float) -> int:
    if phase != "long" or arm not in ("base", "checkpoint32"):
        raise ValueError("fixed long-transfer phase/arm differs")
    with hooks.installed() as contract:
        code = await source.run(phase, arm, endpoint, output, deadline)
        study.write_x(output / "TERMINAL_STRIP_CONTRACT.json", contract)
        return code


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("long",), required=True)
    parser.add_argument("--arm", choices=("base", "checkpoint32"), required=True)
    parser.add_argument("--endpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--deadline", type=float, required=True)
    args = parser.parse_args()
    raise SystemExit(asyncio.run(run(args.phase, args.arm, args.endpoint, args.output, args.deadline)))
