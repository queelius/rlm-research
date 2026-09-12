"""T1 repair: retain the proven client constructor and alter only temperature."""

from __future__ import annotations

import argparse
import asyncio
from dataclasses import replace
import importlib.util
from pathlib import Path
import sys

import checkpoint
import study_v2 as study


ROOT = Path(__file__).resolve().parent
_previous = {name: sys.modules.get(name) for name in ("study", "checkpoint")}
sys.modules.update(study=study, checkpoint=checkpoint)
try:
    _spec = importlib.util.spec_from_file_location("mrcr_t1_v1_collect_for_v2", ROOT / "collect.py")
    source = importlib.util.module_from_spec(_spec)
    assert _spec.loader is not None
    _spec.loader.exec_module(source)
finally:
    for _name, _module in _previous.items():
        if _module is None:
            sys.modules.pop(_name, None)
        else:
            sys.modules[_name] = _module

# V1's wrapper retained this alias from the completed T0.5 collector even
# though it replaced the innermost run-time global with a reconstructed
# context.  Keep this exact constructor as the transport authority.
proven_model_context = source.source.model_context


def model_context(endpoint: dict, coordinate: dict):
    if coordinate.get("temperature") != 1.0:
        raise ValueError("T1 coordinate changed")
    prior = proven_model_context(endpoint, coordinate)
    sampling = prior.sampling.model_copy(update={"temperature": 1.0})
    return replace(prior, sampling=sampling)


def verify_ready() -> dict:
    ready = study.read(study.READY)
    if ready.get("identity") != study.digest(
        {key: value for key, value in ready.items() if key != "identity"}
    ):
        raise ValueError("T1 V2 READY changed")
    for raw, expected in ready.get("closure_sha256", {}).items():
        if study.sha(Path(raw)) != expected:
            raise ValueError("T1 V2 closure changed: " + raw)
    if study.digest(study.schedule("train")) != ready["inputs"]["schedule_sha256"]:
        raise ValueError("T1 V2 schedule changed")
    return ready


# The executable inner eval collector sits below both the T1 V1 and screen
# wrappers. Bind each executable module, not merely the facade export.
_cursor = source
for _depth in range(3):
    _cursor.verify_ready = verify_ready
    _cursor.model_context = model_context
    _next = getattr(_cursor, "source", None)
    if _next is None:
        break
    _cursor = _next

hooks = source.source.hooks
native_checkpoints = source.source.native_checkpoints


async def run(phase: str, arm: str, endpoint: Path, output: Path, deadline: float) -> int:
    if phase != "train" or arm != "checkpoint32":
        raise ValueError("fixed T1 V2 phase/arm differs")
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
