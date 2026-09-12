"""One fixed owned service for each checkpoint32 readout stage."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys

import checkpoint
import study


STAGES = {
    "train32": {"phase": "train", "arm": "checkpoint32", "output": study.ROOT / "outputs/train32-001"},
    "held-base": {"phase": "held", "arm": "base", "output": study.ROOT / "outputs/held-base-001"},
    "held-checkpoint32": {"phase": "held", "arm": "checkpoint32", "output": study.ROOT / "outputs/held-checkpoint32-001"},
}


def _load_source():
    path = study.SOURCE_EVAL / "owner.py"
    text = path.read_text()
    if text.count('STAGES["train"]') != 1:
        raise ValueError("inherited held-gate train stage boundary changed")
    text = text.replace('STAGES["train"]', 'STAGES["train32"]')
    if text.count('stage != "train"') != 2:
        raise ValueError("inherited train-gate boundary changed")
    text = text.replace('stage != "train"', 'stage != "train32"')
    previous = {name: sys.modules.get(name) for name in ("study", "checkpoint")}
    sys.modules["study"] = study
    sys.modules["checkpoint"] = checkpoint
    try:
        spec = importlib.util.spec_from_loader("procedural_sft_continue32_owner_source", loader=None)
        module = importlib.util.module_from_spec(spec)
        module.__file__ = str(path) + ":continue32"
        exec(compile(text, module.__file__, "exec"), module.__dict__)
        module.STAGES = STAGES
        return module
    finally:
        for name, value in previous.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value


source = _load_source()
held_gate = source.held_gate
verify = source.verify
execute = source.execute


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--stage", choices=tuple(STAGES), required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--outer-seconds", type=int, default=study.OWNER_SECONDS)
    args = parser.parse_args()
    if args.command == "verify":
        print(verify(args.stage)["identity"])
    else:
        value = execute(args.stage, args.output or STAGES[args.stage]["output"], args.outer_seconds)
        print(json.dumps(value, sort_keys=True))
        raise SystemExit(0 if value["complete"] else 1)
