"""T1 attempt-003: repair the exact pre-network role-audit expectation."""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
from pathlib import Path
import sys

import checkpoint
import study_v3 as study


ROOT = Path(__file__).resolve().parent
_previous = {name: sys.modules.get(name) for name in ("study_v2", "checkpoint")}
sys.modules.update(study_v2=study, checkpoint=checkpoint)
try:
    _spec = importlib.util.spec_from_file_location("mrcr_t1_v2_collect_for_v3", ROOT / "collect_v2.py")
    source = importlib.util.module_from_spec(_spec)
    assert _spec.loader is not None
    _spec.loader.exec_module(source)
finally:
    for _name, _module in _previous.items():
        if _module is None:
            sys.modules.pop(_name, None)
        else:
            sys.modules[_name] = _module


def role_hooks():
    """Load the pinned role hook with its sampling assertion changed to T1."""
    path = study.ROLE_SOURCE
    text = path.read_text()
    needle = '"temperature": 0.5'
    if text.count(needle) != 1:
        raise ValueError("pinned role hook temperature assertion changed")
    text = text.replace(needle, '"temperature": 1.0')
    previous_path = list(sys.path)
    try:
        sys.path.insert(0, str(path.parent))
        spec = importlib.util.spec_from_loader("mrcr_t1_role_hooks_v3", loader=None)
        module = importlib.util.module_from_spec(spec)
        module.__file__ = str(path)
        exec(compile(text, str(path), "exec"), module.__dict__)
        return module
    finally:
        sys.path[:] = previous_path


def verify_ready() -> dict:
    ready = study.read(study.READY)
    if ready.get("identity") != study.digest(
        {key: value for key, value in ready.items() if key != "identity"}
    ):
        raise ValueError("T1 V3 READY changed")
    for raw, expected in ready.get("closure_sha256", {}).items():
        if study.sha(Path(raw)) != expected:
            raise ValueError("T1 V3 closure changed: " + raw)
    if study.digest(study.schedule("train")) != ready["inputs"]["schedule_sha256"]:
        raise ValueError("T1 V3 schedule changed")
    return ready


# Bind both checks through every executable wrapper down to the eval collector.
_cursor = source
for _depth in range(4):
    _cursor.verify_ready = verify_ready
    if hasattr(_cursor, "role_hooks"):
        _cursor.role_hooks = role_hooks
    _next = getattr(_cursor, "source", None)
    if _next is None:
        break
    _cursor = _next

model_context = source.model_context
hooks = source.hooks
native_checkpoints = source.native_checkpoints


async def run(phase: str, arm: str, endpoint: Path, output: Path, deadline: float) -> int:
    if phase != "train" or arm != "checkpoint32":
        raise ValueError("fixed T1 V3 phase/arm differs")
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

