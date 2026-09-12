"""One bounded service owner per fixed arm for the fresh paired seed block."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys

import checkpoint
import study


STAGES = {
    "base": study.ROOT / "outputs/base-001",
    "lr1e-5": study.ROOT / "outputs/lr1e-5-001",
    "lr1e-4": study.ROOT / "outputs/lr1e-4-001",
}


def _load_source():
    path = study.SOURCE_EVAL / "owner.py"
    previous = {name: sys.modules.get(name) for name in ("study", "checkpoint")}
    sys.modules["study"] = study
    sys.modules["checkpoint"] = checkpoint
    try:
        spec = importlib.util.spec_from_file_location("token_tis_seed2_shaped_owner", path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        module.STAGES = STAGES
        return module
    finally:
        for name, value in previous.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value


source = _load_source()


def plan():
    return {
        "schema": "mrcr-token-tis-held16-seed2-three-arm-plan-v1",
        "stage_argv": {
            stage: [
                str(study.NATIVE), str(study.ROOT / "owner.py"), "run", "--stage", stage,
                "--output", str(output), "--outer-seconds", str(study.OWNER_SECONDS),
            ]
            for stage, output in STAGES.items()
        },
        "episodes_per_arm": 16,
        "optimizer_steps": 0,
        "selection": False,
        "paired_schedule_sha256": study.digest(study.schedule("held")),
        "external_cap_seconds_each": 700,
        "collector": str(study.ROOT / "collect.py"),
    }


def verify(stage: str):
    return source.verify(stage)


def execute(stage: str, output: Path, outer_seconds: int):
    return source.execute(stage, output, outer_seconds)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run", "plan"))
    parser.add_argument("--stage", choices=tuple(STAGES))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--outer-seconds", type=int, default=study.OWNER_SECONDS)
    args = parser.parse_args()
    if args.command == "plan":
        value = plan()
    elif args.command == "verify":
        if args.stage is None:
            parser.error("verify requires --stage")
        value = {"identity": verify(args.stage)["identity"]}
    else:
        if args.stage is None:
            parser.error("run requires --stage")
        value = execute(args.stage, args.output or STAGES[args.stage], args.outer_seconds)
    print(json.dumps(value, indent=2, sort_keys=True))
    if args.command == "run" and not value["complete"]:
        raise SystemExit(1)
