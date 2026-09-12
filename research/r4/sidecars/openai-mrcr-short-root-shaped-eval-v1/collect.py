"""Exact source-pinned MRCR collector with shaped-reward diagnostics."""

from __future__ import annotations

import argparse
import asyncio
import functools
import hashlib
import importlib.util
import math
from pathlib import Path
import sys

import checkpoint
import study


SOURCE = study.EVAL_SOURCE / "collect.py"
SOURCE_SHA = "47f6d338ceaa29021b92baa8eddb73e5ee1d98281bd81a42be4b87137f9869db"


def shaped_summary(records):
    available = [row for row in records if row["derived"]["scientifically_available"]]
    return {
        "raw_exact": sum(bool(row["derived"]["raw_exact"]) for row in available),
        "raw_similarity_at_least_0_90": sum(
            float(row["derived"]["reward"]) >= 0.90 for row in available
        ),
        "shaped_reward_sum": math.fsum(
            0.5 * (float(row["derived"]["reward"]) >= 0.90)
            + 0.5 * bool(row["derived"]["raw_exact"])
            for row in available
        ),
        "scientifically_available": len(available),
        "infrastructure_unavailable": len(records) - len(available),
        "newline_or_output_repair": None,
    }


@functools.lru_cache(maxsize=1)
def source_module():
    raw = SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA:
        raise ValueError("reviewed exact-raw MRCR collector changed")
    text = raw.decode()
    before = 'for phase in ("train", "held"):'
    if text.count(before) != 1:
        raise ValueError("collector verification phase transform boundary changed")
    text = text.replace(before, 'for phase in ("held",):')
    previous_study = sys.modules.get("study")
    previous_checkpoint = sys.modules.get("checkpoint")
    sys.modules["study"] = study
    sys.modules["checkpoint"] = checkpoint
    try:
        spec = importlib.util.spec_from_loader("shaped_root_eval_exact_collector", loader=None)
        module = importlib.util.module_from_spec(spec)
        module.__file__ = str(SOURCE) + ":shaped-root-held16"
        exec(compile(text, module.__file__, "exec"), module.__dict__)
    finally:
        if previous_study is None:
            sys.modules.pop("study", None)
        else:
            sys.modules["study"] = previous_study
        if previous_checkpoint is None:
            sys.modules.pop("checkpoint", None)
        else:
            sys.modules["checkpoint"] = previous_checkpoint
    original = module.summarize

    def summarize(records, phase, arm):
        result = original(records, phase, arm)
        result.update(shaped_summary(records))
        result["schema"] = "openai-mrcr-shaped-root-heldout-result-v1"
        result["primary_metric"] = "paired raw exact"
        result["official_similarity_is_diagnostic"] = True
        result["shaped_reward_is_diagnostic"] = True
        return result

    module.summarize = summarize
    return module


async def run(arm: str, endpoint: Path, output: Path, deadline: float) -> int:
    return await source_module().run("held", arm, endpoint, output, deadline)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=("base", "updated"), required=True)
    parser.add_argument("--endpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--deadline", type=float, required=True)
    args = parser.parse_args()
    raise SystemExit(asyncio.run(run(args.arm, args.endpoint, args.output, args.deadline)))
